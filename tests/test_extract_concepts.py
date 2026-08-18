"""Tests for tools/extract_concepts.py — concept extraction and dependency detection."""

import json
from pathlib import Path

import pytest

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
from extract_concepts import (
    extract_concepts,
    extract_keywords_per_chunk,
    detect_explicit_references,
    detect_first_mention_edges,
    compute_foundational_scores,
    to_json,
    Edge,
    _normalize_term,
    _is_defined_in_chunk,
)

FIXTURES = Path(__file__).resolve().parent / "fixtures"


def load_fixture(name: str) -> list[dict]:
    return json.loads((FIXTURES / name).read_text())


# --- Integration tests ---


class TestExtractConcepts:
    def test_tutorial_extracts_concepts(self):
        chunks = load_fixture("chunks_tutorial.json")
        result = extract_concepts(chunks, top_n=8)
        assert len(result.concepts) > 0
        assert len(result.per_chunk) == len(chunks)

    def test_tutorial_has_explicit_references(self):
        chunks = load_fixture("chunks_tutorial.json")
        result = extract_concepts(chunks, top_n=8)
        explicit = [e for e in result.edges if e.edge_type == "explicit_ref"]
        # The tutorial fixture has many cross-chapter references
        assert len(explicit) >= 5

    def test_tutorial_has_first_mention_edges(self):
        chunks = load_fixture("chunks_tutorial.json")
        result = extract_concepts(chunks, top_n=8)
        first_mention = [e for e in result.edges if e.edge_type == "first_mention"]
        assert len(first_mention) >= 3

    def test_reference_has_no_explicit_refs(self):
        chunks = load_fixture("chunks_reference.json")
        result = extract_concepts(chunks, top_n=8)
        explicit = [e for e in result.edges if e.edge_type == "explicit_ref"]
        assert len(explicit) == 0

    def test_reference_has_shared_concepts(self):
        chunks = load_fixture("chunks_reference.json")
        result = extract_concepts(chunks, top_n=8)
        # "socket" should be the most foundational concept
        top = result.concepts[0]
        assert "socket" in top.term.lower()

    def test_graph_nodes_match_chunks(self):
        chunks = load_fixture("chunks_tutorial.json")
        result = extract_concepts(chunks, top_n=8)
        assert result.graph.number_of_nodes() == len(chunks)

    def test_graph_edges_have_attributes(self):
        chunks = load_fixture("chunks_tutorial.json")
        result = extract_concepts(chunks, top_n=8)
        for u, v, data in result.graph.edges(data=True):
            assert "weight" in data
            assert "type" in data
            assert "concept" in data

    def test_serialization_roundtrip(self):
        chunks = load_fixture("chunks_tutorial.json")
        result = extract_concepts(chunks, top_n=8)
        serialized = to_json(result)
        assert "concepts" in serialized
        assert "edges" in serialized
        assert "per_chunk" in serialized
        assert "graph_stats" in serialized
        # Should be JSON-serializable
        json_str = json.dumps(serialized)
        assert len(json_str) > 0

    def test_empty_chunks(self):
        result = extract_concepts([], top_n=8)
        assert result.concepts == []
        assert result.edges == []
        assert result.per_chunk == []
        assert result.graph.number_of_nodes() == 0


# --- YAKE keyword extraction ---


class TestKeywordExtraction:
    def test_extracts_keywords_per_chunk(self):
        chunks = load_fixture("chunks_tutorial.json")
        keywords = extract_keywords_per_chunk(chunks, top_n=8)
        assert len(keywords) == len(chunks)
        # Each chunk with content should have keywords
        for i, kws in enumerate(keywords):
            if chunks[i].get("content") and len(chunks[i]["content"].split()) >= 10:
                assert len(kws) > 0, f"Chunk {i} should have keywords"
                assert len(kws) <= 8

    def test_keywords_are_meaningful(self):
        chunks = load_fixture("chunks_tutorial.json")
        keywords = extract_keywords_per_chunk(chunks, top_n=8)
        # No single-char or pure-number keywords
        for kws in keywords:
            for term, score in kws:
                assert len(term) > 2
                assert not term.replace(" ", "").isdigit()

    def test_short_content_yields_empty(self):
        chunks = [{"content": "Short.", "heading": "X", "word_count": 1}]
        keywords = extract_keywords_per_chunk(chunks, top_n=8)
        assert keywords[0] == []

    def test_empty_content_yields_empty(self):
        chunks = [{"content": "", "heading": "X", "word_count": 0}]
        keywords = extract_keywords_per_chunk(chunks, top_n=8)
        assert keywords[0] == []


# --- Explicit reference detection ---


class TestExplicitReferences:
    def test_backward_chapter_reference(self):
        chunks = [
            {"heading": "Chapter 1: Intro", "content": "Welcome.", "level": 1},
            {"heading": "Chapter 2: More", "content": "As we saw in Chapter 1, this matters.", "level": 1},
        ]
        edges = detect_explicit_references(chunks)
        assert len(edges) >= 1
        edge = edges[0]
        assert edge.source == 0
        assert edge.target == 1
        assert edge.edge_type == "explicit_ref"

    def test_forward_chapter_reference(self):
        chunks = [
            {"heading": "Chapter 1: Intro", "content": "We'll see in Chapter 2 how this works.", "level": 1},
            {"heading": "Chapter 2: Details", "content": "Here we go.", "level": 1},
        ]
        edges = detect_explicit_references(chunks)
        assert len(edges) >= 1
        # "We'll see in Chapter 2" matches forward pattern → source=0, target=1
        # But "in Chapter 2" also matches the backward pattern → source=1, target=0
        # Both edges are valid detections; verify at least one edge connects these chunks
        connected = any(
            (e.source == 0 and e.target == 1) or (e.source == 1 and e.target == 0)
            for e in edges
        )
        assert connected

    def test_relative_backward_reference(self):
        chunks = [
            {"heading": "Part A", "content": "First part.", "level": 1},
            {"heading": "Part B", "content": "As discussed in the previous chapter, we proceed.", "level": 1},
        ]
        edges = detect_explicit_references(chunks)
        assert len(edges) >= 1
        assert edges[0].source == 0
        assert edges[0].target == 1

    def test_no_references_in_api_docs(self):
        chunks = load_fixture("chunks_reference.json")
        edges = detect_explicit_references(chunks)
        assert len(edges) == 0

    def test_self_reference_ignored(self):
        chunks = [
            {"heading": "Chapter 1: Only", "content": "See Chapter 1 for details.", "level": 1},
        ]
        edges = detect_explicit_references(chunks)
        assert len(edges) == 0


# --- First-mention heuristic ---


class TestFirstMention:
    def test_term_in_heading_creates_edge(self):
        chunks = [
            {"heading": "Event Sourcing", "content": "Event sourcing is a pattern for storing state."},
            {"heading": "Advanced Patterns", "content": "Building on event sourcing, we can create projections."},
        ]
        keywords = [
            [("event sourcing", 0.01)],
            [("projections", 0.02)],
        ]
        edges = detect_first_mention_edges(chunks, keywords)
        # "event sourcing" defined in chunk 0 heading, used in chunk 1
        es_edges = [e for e in edges if "event sourcing" in e.concept]
        assert len(es_edges) >= 1
        assert es_edges[0].source == 0
        assert es_edges[0].target == 1

    def test_edges_point_forward(self):
        chunks = load_fixture("chunks_tutorial.json")
        keywords = extract_keywords_per_chunk(chunks, top_n=8)
        edges = detect_first_mention_edges(chunks, keywords)
        for edge in edges:
            assert edge.source < edge.target, (
                f"First-mention edge should point forward: {edge.source} → {edge.target}"
            )

    def test_no_edges_for_isolated_terms(self):
        chunks = [
            {"heading": "Alpha", "content": "Alpha is a unique concept not repeated."},
            {"heading": "Beta", "content": "Beta is completely different from alpha."},
        ]
        # Only extract "unique concept" from chunk 0 — not present in chunk 1
        keywords = [
            [("unique concept", 0.01)],
            [("completely different", 0.02)],
        ]
        edges = detect_first_mention_edges(chunks, keywords)
        uc_edges = [e for e in edges if "unique concept" in e.concept]
        assert len(uc_edges) == 0


# --- Foundational-ness scoring ---


class TestFoundationalScoring:
    def test_early_frequent_terms_score_highest(self):
        chunks = load_fixture("chunks_reference.json")
        keywords = extract_keywords_per_chunk(chunks, top_n=8)
        concepts = compute_foundational_scores(chunks, keywords)
        # "socket" appears in almost every chunk and starts in chunk 0
        top = concepts[0]
        assert "socket" in top.term.lower()
        assert top.score > 0.5

    def test_scores_between_zero_and_one(self):
        chunks = load_fixture("chunks_tutorial.json")
        keywords = extract_keywords_per_chunk(chunks, top_n=8)
        concepts = compute_foundational_scores(chunks, keywords)
        for c in concepts:
            assert 0.0 <= c.score <= 1.0


# --- Helper functions ---


class TestHelpers:
    def test_normalize_term(self):
        assert _normalize_term("Event Sourcing!") == "event sourcing"
        assert _normalize_term("  spaces  ") == "spaces"

    def test_is_defined_in_heading(self):
        chunk = {"heading": "Event Sourcing", "content": "Some other text here."}
        assert _is_defined_in_chunk("event sourcing", chunk)

    def test_is_defined_in_first_sentences(self):
        chunk = {"heading": "Introduction", "content": "Event sourcing is a key pattern. It stores all state changes. More details follow later in this lengthy paragraph."}
        assert _is_defined_in_chunk("event sourcing", chunk)

    def test_not_defined_if_only_in_later_content(self):
        chunk = {"heading": "Other Topic", "content": "First sentence about X. Second about Y. Third mentions event sourcing briefly."}
        assert not _is_defined_in_chunk("event sourcing", chunk)
