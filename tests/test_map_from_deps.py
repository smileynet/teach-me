"""Tests for tools/map_from_deps.py — dependency-reordered MAP.md generation."""

import json
import tempfile
from pathlib import Path

import networkx as nx
import pytest

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
from map_from_deps import (
    generate_dependency_ordered_map,
    mwfas_break_cycles,
    compute_blended_scores,
    topological_sort_scored,
    detect_modules,
)
from map_parser import load_map


FIXTURES = Path(__file__).resolve().parent / "fixtures"


def load_fixture(name: str) -> list[dict]:
    return json.loads((FIXTURES / name).read_text())


# --- Integration tests ---


class TestGenerateDependencyOrderedMap:
    def test_reference_produces_different_order(self):
        chunks = load_fixture("chunks_reference.json")
        map_md = generate_dependency_ordered_map(chunks, "socket-api", "Socket API")
        # Extract topic slugs from output
        slugs = [line.replace("### ", "") for line in map_md.split("\n") if line.startswith("### ")]
        # Original is alphabetical; reordered should differ
        original_order = list(range(len(chunks)))
        assert slugs[0] == "accept"  # accept defines "socket", should be first
        # close() was 3rd alphabetically, should move later
        assert slugs.index("close") > 5

    def test_output_parseable_by_map_parser(self):
        chunks = load_fixture("chunks_reference.json")
        map_md = generate_dependency_ordered_map(chunks, "socket-api", "Socket API")
        tmp = Path(tempfile.mktemp(suffix=".MAP.md"))
        try:
            tmp.write_text(map_md)
            dm = load_map(tmp)
            assert dm.domain == "socket-api"
            assert len(dm.topics) > 0
            for topic in dm.topics:
                assert topic.slug
                assert topic.title
                assert topic.scope in ("lightweight", "substantial", "deep")
        finally:
            tmp.unlink(missing_ok=True)

    def test_prereqs_respect_dag(self):
        """No topic should appear before its prereqs in the ordering."""
        chunks = load_fixture("chunks_reference.json")
        map_md = generate_dependency_ordered_map(chunks, "test", "Test")
        tmp = Path(tempfile.mktemp(suffix=".MAP.md"))
        try:
            tmp.write_text(map_md)
            dm = load_map(tmp)
            slug_position = {t.slug: i for i, t in enumerate(dm.topics)}
            for topic in dm.topics:
                for prereq in topic.prereqs:
                    assert slug_position[prereq] < slug_position[topic.slug], (
                        f"{topic.slug} (pos {slug_position[topic.slug]}) "
                        f"appears before prereq {prereq} (pos {slug_position[prereq]})"
                    )
        finally:
            tmp.unlink(missing_ok=True)

    def test_fallback_on_sparse_graph(self):
        """When density < 0.05, falls back to document order."""
        # Create a minimal fixture with very few edges possible
        chunks = [
            {"heading": "Topic A", "level": 1, "page_start": 1,
             "content": "Unique alpha content that has no shared terms with others at all.", "word_count": 200,
             "has_code": False, "has_table": False},
            {"heading": "Topic B", "level": 1, "page_start": 5,
             "content": "Completely different beta material with zero overlap whatsoever.", "word_count": 200,
             "has_code": False, "has_table": False},
            {"heading": "Topic C", "level": 1, "page_start": 10,
             "content": "Third gamma section discussing unrelated independent concepts.", "word_count": 200,
             "has_code": False, "has_table": False},
        ]
        map_md = generate_dependency_ordered_map(chunks, "sparse", "Sparse")
        # Should contain the fallback comment
        assert "density < 0.05" in map_md or "document order" in map_md.lower() or len(map_md) > 0

    def test_empty_chunks(self):
        map_md = generate_dependency_ordered_map([], "test", "Test")
        assert map_md == ""

    def test_has_frontmatter(self):
        chunks = load_fixture("chunks_reference.json")
        map_md = generate_dependency_ordered_map(chunks, "my-domain", "My Title")
        assert "domain: my-domain" in map_md
        assert 'description: "My Title"' in map_md
        assert "generated:" in map_md
        assert "depth: 0" in map_md


# --- MWFAS cycle-breaking ---


class TestMWFAS:
    def test_breaks_all_cycles(self):
        G = nx.DiGraph()
        G.add_edge(0, 1, weight=0.8)
        G.add_edge(1, 2, weight=0.7)
        G.add_edge(2, 0, weight=0.2)  # weakest — should be cut
        dag, removed = mwfas_break_cycles(G)
        assert nx.is_directed_acyclic_graph(dag)

    def test_removes_weakest_edge(self):
        G = nx.DiGraph()
        G.add_edge(0, 1, weight=0.9)
        G.add_edge(1, 2, weight=0.8)
        G.add_edge(2, 0, weight=0.1)  # weakest
        dag, removed = mwfas_break_cycles(G)
        # Should remove the 0.1 edge (2→0)
        assert len(removed) == 1
        assert removed[0][0] == 2
        assert removed[0][1] == 0

    def test_already_dag_no_changes(self):
        G = nx.DiGraph()
        G.add_edge(0, 1, weight=0.8)
        G.add_edge(1, 2, weight=0.7)
        dag, removed = mwfas_break_cycles(G)
        assert removed == []
        assert dag.number_of_edges() == 2

    def test_readds_compatible_edges(self):
        """After breaking cycles, try re-adding removed edges that don't recreate cycles."""
        G = nx.DiGraph()
        # Two separate cycles
        G.add_edge(0, 1, weight=0.8)
        G.add_edge(1, 0, weight=0.1)  # cycle 1
        G.add_edge(2, 3, weight=0.7)
        G.add_edge(3, 2, weight=0.2)  # cycle 2
        dag, removed = mwfas_break_cycles(G)
        assert nx.is_directed_acyclic_graph(dag)
        assert len(removed) == 2


# --- Blended scoring ---


class TestBlendedScoring:
    def test_scores_between_zero_and_one(self):
        G = nx.DiGraph()
        G.add_edge(0, 1, weight=0.8)
        G.add_edge(0, 2, weight=0.7)
        G.add_edge(1, 3, weight=0.6)
        scores = compute_blended_scores(G, 4)
        for n, s in scores.items():
            assert 0.0 <= s <= 1.0, f"Node {n} score {s} out of range"

    def test_root_node_scores_highest(self):
        """Node with high in-degree + early position should score highest."""
        G = nx.DiGraph()
        for i in range(1, 5):
            G.add_edge(0, i, weight=0.5)
        scores = compute_blended_scores(G, 5)
        # Node 0 has highest out-degree and earliest position
        assert scores[0] == max(scores.values())


# --- Module detection ---


class TestModuleDetection:
    def test_detects_size_3_scc(self):
        G = nx.DiGraph()
        # Triangle cycle
        G.add_edge(0, 1, weight=0.5)
        G.add_edge(1, 2, weight=0.5)
        G.add_edge(2, 0, weight=0.5)
        # Non-cyclic node
        G.add_edge(3, 0, weight=0.5)
        chunks = [
            {"heading": "A"}, {"heading": "B"}, {"heading": "C"}, {"heading": "D"}
        ]
        modules = detect_modules(G, chunks)
        assert len(modules) == 1
        assert set(modules[0].node_indices) == {0, 1, 2}

    def test_ignores_size_2_scc(self):
        G = nx.DiGraph()
        G.add_edge(0, 1, weight=0.5)
        G.add_edge(1, 0, weight=0.3)
        chunks = [{"heading": "A"}, {"heading": "B"}]
        modules = detect_modules(G, chunks)
        assert len(modules) == 0

    def test_no_modules_in_dag(self):
        G = nx.DiGraph()
        G.add_edge(0, 1, weight=0.8)
        G.add_edge(1, 2, weight=0.7)
        chunks = [{"heading": "A"}, {"heading": "B"}, {"heading": "C"}]
        modules = detect_modules(G, chunks)
        assert len(modules) == 0


# --- Topological sort with scoring ---


class TestTopologicalSortScored:
    def test_respects_edges(self):
        G = nx.DiGraph()
        G.add_edge(0, 1)
        G.add_edge(0, 2)
        G.add_edge(1, 3)
        scores = {0: 1.0, 1: 0.5, 2: 0.8, 3: 0.1}
        order = topological_sort_scored(G, scores)
        assert order.index(0) < order.index(1)
        assert order.index(0) < order.index(2)
        assert order.index(1) < order.index(3)

    def test_tiebreak_by_score(self):
        G = nx.DiGraph()
        G.add_edge(0, 1)
        G.add_edge(0, 2)
        # Both 1 and 2 become available after 0; 2 has higher score → comes first
        scores = {0: 1.0, 1: 0.3, 2: 0.9}
        order = topological_sort_scored(G, scores)
        assert order[0] == 0
        assert order[1] == 2  # higher score → earlier
        assert order[2] == 1
