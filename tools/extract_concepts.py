#!/usr/bin/env python3
"""extract_concepts.py — Extract concepts and prerequisite edges from chunks.

Uses YAKE for keyword extraction, regex for explicit cross-references,
and a first-mention heuristic for implicit prerequisite edges.
Produces a NetworkX DiGraph suitable for MAP.md generation.

Usage:
    python tools/extract_concepts.py chunks.json [--top-n 8] [--output graph.json]
"""

from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

import networkx as nx
import yake


# --- Data structures ---


@dataclass
class Concept:
    term: str
    score: float  # foundational-ness: frequency × (1 / first_position)
    defined_in: list[int] = field(default_factory=list)
    used_in: list[int] = field(default_factory=list)


@dataclass
class Edge:
    source: int  # chunk index (dependency — earlier chunk)
    target: int  # chunk index (dependent — later chunk)
    edge_type: str  # "explicit_ref" | "first_mention"
    concept: str  # term or matched pattern
    weight: float  # 0.0–1.0


@dataclass
class ConceptGraph:
    concepts: list[Concept]
    edges: list[Edge]
    per_chunk: list[dict]  # [{index, heading, keywords: [str]}]
    graph: nx.DiGraph


# --- YAKE keyword extraction ---


def extract_keywords_per_chunk(
    chunks: list[dict], top_n: int = 8
) -> list[list[tuple[str, float]]]:
    """Run YAKE on each chunk, return top_n keywords per chunk.

    Returns list of [(keyword, yake_score)] per chunk.
    Lower YAKE score = more important.
    """
    kw_extractor = yake.KeywordExtractor(
        lan="en",
        n=3,  # up to trigrams
        dedupLim=0.7,  # deduplication threshold
        top=top_n * 2,  # extract more, filter later
        features=None,
    )

    results = []
    for chunk in chunks:
        text = chunk.get("content", "")
        if not text or len(text.split()) < 10:
            results.append([])
            continue

        raw_keywords = kw_extractor.extract_keywords(text)
        # Filter: drop single-char keywords and pure numbers
        filtered = [
            (kw, score)
            for kw, score in raw_keywords
            if len(kw) > 2 and not kw.replace(" ", "").isdigit()
        ]
        results.append(filtered[:top_n])

    return results


# --- Explicit reference detection ---

EXPLICIT_REF_PATTERNS = [
    # Backward references
    (r"as we (?:saw|covered|discussed|learned|built) in (?:chapter|section|§)\s*(\d+)", "backward"),
    (r"(?:from|in) (?:chapter|section|§)\s*(\d+)", "backward"),
    (r"recall (?:from )?(?:chapter|section|§)\s*(\d+)", "backward"),
    (r"as (?:mentioned|described|explained) in (?:chapter|section|§)\s*(\d+)", "backward"),
    (r"building on .+ from (?:chapter|section|§)\s*(\d+)", "backward"),
    # Forward references
    (r"(?:as )?we'?ll (?:see|cover|discuss|explore) in (?:chapter|section|§)\s*(\d+)", "forward"),
    (r"see (?:chapter|section|§)\s*(\d+)", "forward"),
    (r"(?:covered|discussed) (?:later )?in (?:chapter|section|§)\s*(\d+)", "forward"),
    # Named section references (not numbered)
    (r"as we (?:saw|covered|discussed) (?:in (?:the )?(?:previous|last|earlier)) (?:chapter|section)", "backward_relative"),
    (r"(?:the )?(?:previous|preceding) (?:chapter|section)", "backward_relative"),
    (r"(?:the )?(?:next|following) (?:chapter|section)", "forward_relative"),
]


def detect_explicit_references(chunks: list[dict]) -> list[Edge]:
    """Find explicit cross-references between chunks using regex."""
    edges = []

    # Build chapter-number to chunk-index mapping
    chapter_map: dict[int, int] = {}
    for i, chunk in enumerate(chunks):
        match = re.match(r"(?:chapter|part)\s+(\d+)", chunk["heading"], re.IGNORECASE)
        if match:
            chapter_map[int(match.group(1))] = i
        # Also try leading number: "1. Introduction", "1.1 Basics"
        match = re.match(r"^(\d+)[\.\):\s]", chunk["heading"])
        if match:
            num = int(match.group(1))
            if num not in chapter_map:
                chapter_map[num] = i

    for chunk_idx, chunk in enumerate(chunks):
        content = chunk.get("content", "")
        for pattern, direction in EXPLICIT_REF_PATTERNS:
            for match in re.finditer(pattern, content, re.IGNORECASE):
                if direction in ("backward", "forward"):
                    ref_num = int(match.group(1))
                    ref_idx = chapter_map.get(ref_num)
                    if ref_idx is None or ref_idx == chunk_idx:
                        continue
                    # Edge direction: dependency points from earlier to later
                    if direction == "backward":
                        # Current chunk depends on referenced chunk
                        edges.append(Edge(
                            source=ref_idx,
                            target=chunk_idx,
                            edge_type="explicit_ref",
                            concept=match.group(0),
                            weight=0.9,
                        ))
                    else:
                        # Referenced chunk will depend on current
                        edges.append(Edge(
                            source=chunk_idx,
                            target=ref_idx,
                            edge_type="explicit_ref",
                            concept=match.group(0),
                            weight=0.7,
                        ))
                elif direction == "backward_relative" and chunk_idx > 0:
                    edges.append(Edge(
                        source=chunk_idx - 1,
                        target=chunk_idx,
                        edge_type="explicit_ref",
                        concept=match.group(0),
                        weight=0.6,
                    ))
                elif direction == "forward_relative" and chunk_idx < len(chunks) - 1:
                    edges.append(Edge(
                        source=chunk_idx,
                        target=chunk_idx + 1,
                        edge_type="explicit_ref",
                        concept=match.group(0),
                        weight=0.5,
                    ))

    return edges


# --- First-mention heuristic ---


def _normalize_term(term: str) -> str:
    """Lowercase, strip punctuation for matching."""
    return re.sub(r"[^\w\s]", "", term.lower()).strip()


def _is_defined_in_chunk(term: str, chunk: dict) -> bool:
    """A term is 'defined' if it appears in the heading or first 2 sentences."""
    norm = _normalize_term(term)
    heading_norm = _normalize_term(chunk["heading"])
    if norm in heading_norm:
        return True

    content = chunk.get("content", "")
    # First two sentences
    sentences = re.split(r"[.!?]+", content)[:2]
    first_part = " ".join(sentences).lower()
    return norm in first_part


def _term_appears_in_chunk(term: str, chunk: dict) -> bool:
    """Check if term appears anywhere in the chunk content."""
    norm = _normalize_term(term)
    content = _normalize_term(chunk.get("content", ""))
    return norm in content


def detect_first_mention_edges(
    chunks: list[dict], keywords_per_chunk: list[list[tuple[str, float]]]
) -> list[Edge]:
    """Detect prerequisite edges via first-mention heuristic.

    Logic: if term T is defined in chunk A (appears in heading or first 2 sentences)
    and used in chunk B (B > A), then B depends on A.
    """
    edges = []

    # Collect all significant keywords across all chunks
    all_terms: dict[str, int] = {}  # term → first chunk where defined
    for chunk_idx, keywords in enumerate(keywords_per_chunk):
        for term, _score in keywords:
            norm = _normalize_term(term)
            if norm not in all_terms and _is_defined_in_chunk(term, chunks[chunk_idx]):
                all_terms[norm] = chunk_idx

    # For each term defined in chunk A, find later chunks that use it
    for term, defining_chunk in all_terms.items():
        usage_count = 0
        for later_idx in range(defining_chunk + 1, len(chunks)):
            if _term_appears_in_chunk(term, chunks[later_idx]):
                usage_count += 1

        if usage_count == 0:
            continue

        # Create edges to chunks that use the term (not all — just those that use it)
        for later_idx in range(defining_chunk + 1, len(chunks)):
            if _term_appears_in_chunk(term, chunks[later_idx]):
                # Weight based on usage count (more usage = more foundational)
                weight = min(0.8, 0.3 + (usage_count * 0.1))
                edges.append(Edge(
                    source=defining_chunk,
                    target=later_idx,
                    edge_type="first_mention",
                    concept=term,
                    weight=round(weight, 2),
                ))

    return edges


# --- Foundational-ness scoring ---


def compute_foundational_scores(
    chunks: list[dict], keywords_per_chunk: list[list[tuple[str, float]]]
) -> list[Concept]:
    """Score concepts by how foundational they are.

    Score = frequency_across_chunks × (1 / first_appearance_position).
    """
    # Track where each term appears
    term_chunks: dict[str, list[int]] = {}  # norm_term → [chunk indices]
    term_original: dict[str, str] = {}  # norm → best original form

    for chunk_idx, keywords in enumerate(keywords_per_chunk):
        for term, _score in keywords:
            norm = _normalize_term(term)
            if norm not in term_chunks:
                term_chunks[norm] = []
                term_original[norm] = term
            term_chunks[norm].append(chunk_idx)

    concepts = []
    total_chunks = max(len(chunks), 1)

    for norm, chunk_indices in term_chunks.items():
        if not chunk_indices:
            continue
        frequency = len(set(chunk_indices)) / total_chunks
        first_pos = min(chunk_indices)
        # Position factor: 1.0 for first chunk, decreasing
        position_factor = 1.0 / (first_pos + 1)
        score = round(frequency * position_factor, 3)

        # Determine where defined vs used
        defined_in = []
        used_in = []
        for idx in sorted(set(chunk_indices)):
            if _is_defined_in_chunk(term_original[norm], chunks[idx]):
                defined_in.append(idx)
            else:
                used_in.append(idx)

        concepts.append(Concept(
            term=term_original[norm],
            score=score,
            defined_in=defined_in,
            used_in=used_in,
        ))

    # Sort by score descending
    concepts.sort(key=lambda c: c.score, reverse=True)
    return concepts


# --- Main extraction ---


def extract_concepts(chunks: list[dict], top_n: int = 8) -> ConceptGraph:
    """Extract concepts and prerequisite edges from document chunks.

    Args:
        chunks: List of chunk dicts from chunk_pdf.py.
        top_n: Number of keywords to extract per chunk.

    Returns:
        ConceptGraph with concepts, edges, per-chunk keywords, and a NetworkX DiGraph.
    """
    # Layer 1: YAKE keywords
    keywords_per_chunk = extract_keywords_per_chunk(chunks, top_n)

    # Layer 2: Explicit references
    explicit_edges = detect_explicit_references(chunks)

    # Layer 3: First-mention heuristic
    first_mention_edges = detect_first_mention_edges(chunks, keywords_per_chunk)

    # Combine edges
    all_edges = explicit_edges + first_mention_edges

    # Compute foundational-ness scores
    concepts = compute_foundational_scores(chunks, keywords_per_chunk)

    # Build per-chunk summary
    per_chunk = []
    for i, chunk in enumerate(chunks):
        kws = keywords_per_chunk[i] if i < len(keywords_per_chunk) else []
        per_chunk.append({
            "index": i,
            "heading": chunk["heading"],
            "keywords": [kw for kw, _score in kws],
        })

    # Build NetworkX graph
    graph = nx.DiGraph()
    for i, chunk in enumerate(chunks):
        graph.add_node(i, heading=chunk["heading"])
    for edge in all_edges:
        # If edge already exists, keep highest weight
        if graph.has_edge(edge.source, edge.target):
            existing = graph[edge.source][edge.target]
            if edge.weight > existing.get("weight", 0):
                graph[edge.source][edge.target].update(
                    weight=edge.weight, type=edge.edge_type, concept=edge.concept
                )
        else:
            graph.add_edge(
                edge.source, edge.target,
                weight=edge.weight, type=edge.edge_type, concept=edge.concept,
            )

    return ConceptGraph(
        concepts=concepts,
        edges=all_edges,
        per_chunk=per_chunk,
        graph=graph,
    )


# --- Serialization ---


def to_json(result: ConceptGraph) -> dict:
    """Serialize ConceptGraph to a JSON-safe dict."""
    return {
        "concepts": [
            {
                "term": c.term,
                "score": c.score,
                "defined_in": c.defined_in,
                "used_in": c.used_in,
            }
            for c in result.concepts
        ],
        "edges": [
            {
                "from": e.source,
                "to": e.target,
                "type": e.edge_type,
                "concept": e.concept,
                "weight": e.weight,
            }
            for e in result.edges
        ],
        "per_chunk": result.per_chunk,
        "graph_stats": {
            "nodes": result.graph.number_of_nodes(),
            "edges": result.graph.number_of_edges(),
            "is_dag": nx.is_directed_acyclic_graph(result.graph),
        },
    }


# --- CLI ---


def main() -> None:
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        print("Usage: python tools/extract_concepts.py <chunks.json> [--top-n N] [--output out.json]")
        print("\nExtracts concepts and prerequisite edges from chunk_pdf.py output.")
        sys.exit(0)

    path = Path(args[0])
    if not path.exists():
        print(f"File not found: {path}", file=sys.stderr)
        sys.exit(1)

    top_n = 8
    output_path = None
    if "--top-n" in args:
        idx = args.index("--top-n")
        top_n = int(args[idx + 1])
    if "--output" in args:
        idx = args.index("--output")
        output_path = Path(args[idx + 1])

    chunks = json.loads(path.read_text())
    result = extract_concepts(chunks, top_n)

    # Print summary
    print(f"Chunks:    {len(chunks)}")
    print(f"Concepts:  {len(result.concepts)}")
    print(f"Edges:     {len(result.edges)} "
          f"({sum(1 for e in result.edges if e.edge_type == 'explicit_ref')} explicit, "
          f"{sum(1 for e in result.edges if e.edge_type == 'first_mention')} first-mention)")
    print(f"Graph:     {result.graph.number_of_nodes()} nodes, "
          f"{result.graph.number_of_edges()} edges, "
          f"DAG={nx.is_directed_acyclic_graph(result.graph)}")
    print()

    # Top concepts
    print("Top concepts (by foundational-ness):")
    for c in result.concepts[:10]:
        defined = f"defined in {c.defined_in}" if c.defined_in else "implicit"
        print(f"  {c.score:.3f}  {c.term:<30} {defined}")

    # Per-chunk keywords
    print("\nPer-chunk keywords:")
    for pc in result.per_chunk:
        kws = ", ".join(pc["keywords"][:5])
        print(f"  [{pc['index']:>2}] {pc['heading'][:40]:<40} → {kws}")

    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(to_json(result), indent=2, ensure_ascii=False))
        print(f"\nSaved to {output_path}")


if __name__ == "__main__":
    main()
