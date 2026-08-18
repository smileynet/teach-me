#!/usr/bin/env python3
"""map_from_deps.py — Generate dependency-reordered MAP.md for reference-style documents.

When a document is reference-style (alphabetical, lookup-ordered), this tool
reorders topics by learning dependencies rather than document order.

Uses:
- extract_concepts.py for dependency graph construction
- MWFAS iterative cycle-breaking (spike #156: preserves strongest edges)
- Blended scoring: freq×position (0.6) + in-degree (0.4) for tie-breaking
- SCC handling: size 2 → soft prereqs, size 3+ → module grouping

Usage:
    python tools/map_from_deps.py chunks.json --domain "slug" --title "Title" [--output path]
"""

from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

import networkx as nx

sys.path.insert(0, str(Path(__file__).parent))
from extract_concepts import extract_concepts
from map_from_chunks import slugify, is_noise, derive_scope, extract_why


# =============================================================================
# Cycle-breaking: MWFAS iterative (from spike #156)
# =============================================================================


def mwfas_break_cycles(G: nx.DiGraph) -> tuple[nx.DiGraph, list[tuple[int, int, dict]]]:
    """Break cycles using Minimum Weighted Feedback Arc Set (iterative).

    Find cycle → remove min-weight edge → repeat.
    Then try re-adding removed edges (highest weight first) if they don't create cycles.

    Returns: (DAG copy, list of removed edges as (u, v, data))
    """
    H = G.copy()
    removed: list[tuple[int, int, dict]] = []

    while not nx.is_directed_acyclic_graph(H):
        try:
            cycle = nx.find_cycle(H)
        except nx.NetworkXNoCycle:
            break

        # Find min-weight edge in this cycle
        min_edge = min(cycle, key=lambda e: H[e[0]][e[1]].get("weight", 0.5))
        u, v = min_edge[0], min_edge[1]
        edge_data = H[u][v].copy()
        removed.append((u, v, edge_data))
        H.remove_edge(u, v)

    # Try re-adding removed edges (highest weight first) if they don't create cycles
    removed_sorted = sorted(removed, key=lambda e: e[2].get("weight", 0), reverse=True)
    final_removed = []
    for u, v, data in removed_sorted:
        H.add_edge(u, v, **data)
        if not nx.is_directed_acyclic_graph(H):
            H.remove_edge(u, v)
            final_removed.append((u, v, data))

    return H, final_removed


# =============================================================================
# Foundational scoring: blend freq×position (0.6) + in-degree (0.4)
# =============================================================================


def compute_blended_scores(
    dag: nx.DiGraph, num_chunks: int
) -> dict[int, float]:
    """Compute blended foundational score for tie-breaking.

    score = 0.6 * freq_position + 0.4 * normalized_in_degree

    freq_position: (in_degree + out_degree) / total_edges × (1 / (node_index + 1))
    in_degree: normalized to [0, 1]
    """
    total_edges = max(dag.number_of_edges(), 1)
    max_in = max((dag.in_degree(n) for n in dag.nodes()), default=1) or 1

    scores = {}
    for n in dag.nodes():
        # Frequency × position component
        freq = (dag.in_degree(n) + dag.out_degree(n)) / total_edges
        pos_factor = 1.0 / (n + 1)
        freq_pos = freq * pos_factor

        # In-degree component (normalized)
        in_deg = dag.in_degree(n) / max_in

        scores[n] = 0.6 * freq_pos + 0.4 * in_deg

    # Normalize to [0, 1]
    max_score = max(scores.values()) or 1
    return {n: v / max_score for n, v in scores.items()}


# =============================================================================
# Topological sort with tie-breaking
# =============================================================================


def topological_sort_scored(dag: nx.DiGraph, scores: dict[int, float]) -> list[int]:
    """Kahn's algorithm with tie-breaking by score (higher = earlier)."""
    in_degree = {n: dag.in_degree(n) for n in dag.nodes()}
    available = sorted(
        [n for n, d in in_degree.items() if d == 0],
        key=lambda n: scores.get(n, 0),
        reverse=True,
    )
    order = []

    while available:
        node = available.pop(0)
        order.append(node)
        for succ in dag.successors(node):
            in_degree[succ] -= 1
            if in_degree[succ] == 0:
                available.append(succ)
                available.sort(key=lambda n: scores.get(n, 0), reverse=True)

    return order


# =============================================================================
# SCC handling
# =============================================================================


@dataclass
class Module:
    """A group of mutually-reinforcing topics (SCC size 3+)."""
    name: str
    node_indices: list[int]


def detect_modules(G: nx.DiGraph, chunks: list[dict]) -> list[Module]:
    """Find SCCs of size 3+ and create module groupings."""
    modules = []
    for scc in nx.strongly_connected_components(G):
        if len(scc) >= 3:
            indices = sorted(scc)
            # Name from common concepts or first heading
            headings = [chunks[i]["heading"] for i in indices]
            # Use shortest common prefix or first heading
            name = slugify(headings[0]) + "-group"
            modules.append(Module(name=name, node_indices=indices))
    return modules


# =============================================================================
# MAP.md generation
# =============================================================================


@dataclass
class DepTopic:
    slug: str
    title: str
    why: str
    scope: str
    prereqs: list[str]
    soft_prereqs: list[str] = field(default_factory=list)
    module: str | None = None


def generate_dependency_ordered_map(
    chunks: list[dict], domain: str, title: str
) -> str:
    """Generate MAP.md with topics ordered by dependency graph.

    Pipeline:
    1. Extract concepts + edges (via extract_concepts)
    2. Check edge density — fall back to document order if too sparse
    3. Break cycles (MWFAS iterative)
    4. Detect modules (SCC size 3+) and soft prereqs (SCC size 2)
    5. Topological sort with blended scoring tie-break
    6. Generate MAP.md with evidence-based prereqs
    """
    if not chunks:
        return ""

    # Filter noise (same as map_from_chunks)
    content_chunks = []
    chunk_index_map: dict[int, int] = {}  # original index → filtered index
    for i, chunk in enumerate(chunks):
        if chunk.get("level", 1) > 2:
            continue
        if is_noise(chunk["heading"], chunk.get("word_count", 0)):
            continue
        if chunk.get("word_count", 0) < 50:
            continue
        chunk_index_map[i] = len(content_chunks)
        content_chunks.append(chunk)

    if not content_chunks:
        return ""

    # Extract concept graph
    result = extract_concepts(content_chunks, top_n=8)
    G = result.graph

    # Check edge density — fall back if too sparse
    n_nodes = G.number_of_nodes()
    n_edges = G.number_of_edges()
    possible_edges = n_nodes * (n_nodes - 1) if n_nodes > 1 else 1
    density = n_edges / possible_edges

    if density < 0.05:
        # Insufficient signal — fall back to document order
        return _fallback_document_order(content_chunks, domain, title)

    # Detect SCCs before cycle-breaking
    modules = detect_modules(G, content_chunks)
    module_membership: dict[int, str] = {}
    for mod in modules:
        for idx in mod.node_indices:
            module_membership[idx] = mod.name

    # Identify size-2 SCCs for soft prereqs
    soft_prereq_edges: list[tuple[int, int]] = []
    for scc in nx.strongly_connected_components(G):
        if len(scc) == 2:
            nodes = sorted(scc)
            # The weaker edge becomes a soft prereq
            a, b = nodes
            if G.has_edge(a, b) and G.has_edge(b, a):
                w_ab = G[a][b].get("weight", 0.5)
                w_ba = G[b][a].get("weight", 0.5)
                if w_ab <= w_ba:
                    soft_prereq_edges.append((a, b))
                else:
                    soft_prereq_edges.append((b, a))

    # Break cycles (MWFAS)
    dag, removed_edges = mwfas_break_cycles(G)

    # Compute blended scores
    scores = compute_blended_scores(dag, len(content_chunks))

    # Topological sort
    order = topological_sort_scored(dag, scores)

    # Build topics in dependency order
    topics: list[DepTopic] = []
    slug_by_index: dict[int, str] = {}

    # Pre-compute slugs
    seen_slugs: set[str] = set()
    for i in range(len(content_chunks)):
        slug = slugify(content_chunks[i]["heading"])
        if not slug:
            slug = f"topic-{i}"
        if slug in seen_slugs:
            slug = f"{slug}-{i}"
        seen_slugs.add(slug)
        slug_by_index[i] = slug

    for node_idx in order:
        if node_idx >= len(content_chunks):
            continue
        chunk = content_chunks[node_idx]
        slug = slug_by_index[node_idx]

        # Hard prereqs: direct predecessors in the DAG
        prereqs = [
            slug_by_index[pred]
            for pred in dag.predecessors(node_idx)
            if pred in slug_by_index
        ]

        # Soft prereqs: edges that were cut from size-2 SCCs
        soft = [
            slug_by_index[src]
            for src, dst in soft_prereq_edges
            if dst == node_idx and src in slug_by_index
        ]

        topics.append(DepTopic(
            slug=slug,
            title=chunk["heading"],
            why=extract_why(chunk.get("content", "")),
            scope=derive_scope(chunk.get("word_count", 0)),
            prereqs=prereqs,
            soft_prereqs=soft,
            module=module_membership.get(node_idx),
        ))

    return _render_map(topics, modules, domain, title, content_chunks)


def _fallback_document_order(chunks: list[dict], domain: str, title: str) -> str:
    """Generate document-order MAP when dependency signal is too weak."""
    from map_from_chunks import generate_map
    map_md = generate_map(chunks, domain, title)
    # Prepend a note
    note = ("<!-- Note: insufficient dependency signal (density < 0.05) "
            "for reordering. Using document order. -->\n")
    return note + map_md


def _render_map(
    topics: list[DepTopic],
    modules: list[Module],
    domain: str,
    title: str,
    chunks: list[dict],
) -> str:
    """Render MAP.md from ordered topics."""
    lines = [
        "---",
        f"domain: {domain}",
        f'description: "{title}"',
        f"generated: {date.today().isoformat()}",
        "depth: 0",
        "parent: null",
        "leads_to: []",
        "---",
        "",
        f"# {title}",
        "",
        "## Orientation",
        "",
        f"Topics reordered by learning dependencies (foundational concepts first). "
        f"{len(topics)} topics covering {sum(c.get('word_count', 0) for c in chunks):,} words.",
        "",
    ]

    # Module descriptions (if any)
    if modules:
        lines.append("**Modules** (mutually-reinforcing topics — take in any order within the group):")
        for mod in modules:
            member_slugs = [t.slug for t in topics if t.module == mod.name]
            lines.append(f"- *{mod.name}*: {', '.join(member_slugs)}")
        lines.append("")

    lines.append("## Topics")
    lines.append("")

    for topic in topics:
        prereqs_str = f"[{', '.join(topic.prereqs)}]" if topic.prereqs else "[]"
        lines.append(f"### {topic.slug}")
        lines.append(f"- **title:** {topic.title}")
        lines.append(f"- **why:** {topic.why}")
        lines.append(f"- **scope:** {topic.scope}")
        lines.append(f"- **prereqs:** {prereqs_str}")
        if topic.soft_prereqs:
            soft_str = f"[{', '.join(topic.soft_prereqs)}]"
            lines.append(f"- **soft_prereqs:** {soft_str}")
        if topic.module:
            lines.append(f"- **module:** {topic.module}")
        lines.append(f"- **status:** not-started")
        lines.append("")

    return "\n".join(lines)


# =============================================================================
# CLI
# =============================================================================


def main():
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        print("Usage: python tools/map_from_deps.py <chunks.json> --domain SLUG --title TITLE [--output path]")
        print("\nGenerates dependency-reordered MAP.md for reference-style documents.")
        print("Uses concept extraction to determine learning-optimal topic order.")
        sys.exit(0)

    chunks_path = Path(args[0])
    if not chunks_path.exists():
        print(f"Error: file not found: {chunks_path}", file=sys.stderr)
        sys.exit(1)

    domain = "untitled"
    title = "Untitled"
    output_path = None

    if "--domain" in args:
        domain = args[args.index("--domain") + 1]
    if "--title" in args:
        title = args[args.index("--title") + 1]
    if "--output" in args:
        output_path = Path(args[args.index("--output") + 1])

    chunks = json.loads(chunks_path.read_text())
    map_md = generate_dependency_ordered_map(chunks, domain, title)

    if not map_md:
        print("Error: no content chunks found after filtering", file=sys.stderr)
        sys.exit(1)

    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(map_md)
        topic_count = map_md.count("\n### ")
        print(f"✓ Generated {output_path} ({topic_count} topics, dependency-ordered)")
    else:
        print(map_md)


if __name__ == "__main__":
    main()
