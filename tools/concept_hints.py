#!/usr/bin/env python3
"""concept_hints.py — Produce structured concept hints for lesson generation.

Reads source chunks for a domain/topic and produces a JSON file at
.scratch/concepts/{slug}.json with:
- Ranked concepts with foundational-ness scores
- Suggested L-levels (L1/L2/L3) based on score + prerequisite depth
- Prerequisite edges with question-framing suggestions
- Candidate glossary terms

Used by the generate-topic and jargon skills as structured input.

Usage:
    python tools/concept_hints.py source-chunks/domain.json --topic slug --output .scratch/concepts/slug.json
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from extract_concepts import extract_concepts, ConceptGraph, _normalize_term
from map_from_chunks import slugify

# L-level thresholds (calibrated against test fixtures:
# "socket" = 0.818 → L1, "batch processing" = 0.200 → L3)
L1_THRESHOLD = 0.5   # Core concepts — recall level
L2_THRESHOLD = 0.2   # Practice concepts — understand/apply
# Below L2 → L3 (analysis/synthesis)


def compute_level(score: float, prerequisite_depth: int) -> str:
    """Assign L-level based on foundational-ness score and DAG depth.

    Higher score + shallow depth → L1 (core, recall)
    Medium score or moderate depth → L2 (practice)
    Low score or deep in DAG → L3 (analysis/synthesis)
    """
    if score >= L1_THRESHOLD and prerequisite_depth <= 1:
        return "L1"
    if score >= L2_THRESHOLD or prerequisite_depth <= 2:
        return "L2"
    return "L3"


def compute_prerequisite_depth(graph, node: int) -> int:
    """Compute longest path from any root to this node (DAG depth)."""
    import networkx as nx

    if not graph.has_node(node):
        return 0

    predecessors = list(graph.predecessors(node))
    if not predecessors:
        return 0

    try:
        # Find all ancestors and compute max path length
        ancestors = nx.ancestors(graph, node)
        if not ancestors:
            return 0
        max_depth = 0
        for ancestor in ancestors:
            if graph.in_degree(ancestor) == 0:  # root node
                try:
                    path_len = nx.shortest_path_length(graph, ancestor, node)
                    max_depth = max(max_depth, path_len)
                except nx.NetworkXNoPath:
                    continue
        return max_depth
    except (nx.NetworkXError, nx.NodeNotFound):
        return 0


def generate_concept_hints(
    chunks: list[dict],
    topic_slug: str,
    domain: str,
    top_n: int = 10,
) -> dict:
    """Generate structured concept hints for a topic.

    Args:
        chunks: All chunks for the domain (from source-chunks/{domain}.json)
        topic_slug: The topic to generate hints for
        domain: Domain slug
        top_n: Maximum number of concepts to include

    Returns:
        Dict ready to serialize as JSON.
    """
    # Run concept extraction on all chunks
    result = extract_concepts(chunks, top_n=max(top_n, 8))

    # Find the chunk index for the target topic
    target_indices = []
    for i, chunk in enumerate(chunks):
        chunk_slug = slugify(chunk.get("heading", ""))
        if chunk_slug == topic_slug or topic_slug in chunk_slug:
            target_indices.append(i)

    # Build concept list — prioritize concepts relevant to target topic
    concepts_out = []
    for concept in result.concepts[:top_n * 2]:
        # Check if concept is relevant to target topic
        relevant_to_target = any(
            idx in target_indices
            for idx in concept.defined_in + concept.used_in
        )

        # Compute prerequisite depth
        depth = 0
        for idx in concept.defined_in:
            if result.graph.has_node(idx):
                depth = max(depth, compute_prerequisite_depth(result.graph, idx))

        level = compute_level(concept.score, depth)

        # Find what this concept is a prerequisite for
        prereq_of = []
        for idx in concept.defined_in:
            if result.graph.has_node(idx):
                for successor in result.graph.successors(idx):
                    if successor < len(chunks):
                        succ_slug = slugify(chunks[successor].get("heading", ""))
                        if succ_slug and succ_slug not in prereq_of:
                            prereq_of.append(succ_slug)

        concepts_out.append({
            "term": concept.term,
            "score": round(concept.score, 3),
            "level": level,
            "defined_in": concept.defined_in,
            "used_in": concept.used_in,
            "prerequisite_of": prereq_of[:5],
            "relevant_to_target": relevant_to_target,
        })

    # Sort: target-relevant first, then by score
    concepts_out.sort(key=lambda c: (not c["relevant_to_target"], -c["score"]))
    concepts_out = concepts_out[:top_n]

    # Build edge suggestions for question framing
    edges_out = []
    for edge in result.edges:
        if edge.source in target_indices or edge.target in target_indices:
            source_heading = chunks[edge.source].get("heading", "") if edge.source < len(chunks) else ""
            target_heading = chunks[edge.target].get("heading", "") if edge.target < len(chunks) else ""
            edges_out.append({
                "from_topic": slugify(source_heading),
                "to_topic": slugify(target_heading),
                "concept": edge.concept,
                "type": edge.edge_type,
                "suggestion": _generate_question_suggestion(edge, source_heading, target_heading),
            })

    return {
        "topic": topic_slug,
        "domain": domain,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "coverage_target": min(top_n, len(concepts_out)),
        "concepts": concepts_out,
        "edges": edges_out[:10],
    }


def _generate_question_suggestion(edge, source_heading: str, target_heading: str) -> str:
    """Generate a question framing suggestion from a prerequisite edge."""
    if edge.edge_type == "explicit_ref":
        return f"Explain how {target_heading} builds on {source_heading}"
    # first_mention
    return f"Why does understanding '{edge.concept}' matter for {target_heading}?"


def write_concept_hints(hints: dict, output_path: Path) -> Path:
    """Write concept hints JSON to the output path."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(hints, indent=2, ensure_ascii=False))
    return output_path


# --- CLI ---


def main() -> None:
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        print("Usage: python tools/concept_hints.py <chunks.json> --topic SLUG [--domain D] [--output PATH] [--top-n N]")
        print("\nProduces structured concept hints for lesson generation.")
        sys.exit(0)

    chunks_path = Path(args[0])
    topic_slug = ""
    domain = "untitled"
    output_path = None
    top_n = 10

    if "--topic" in args:
        topic_slug = args[args.index("--topic") + 1]
    if "--domain" in args:
        domain = args[args.index("--domain") + 1]
    if "--output" in args:
        output_path = Path(args[args.index("--output") + 1])
    if "--top-n" in args:
        top_n = int(args[args.index("--top-n") + 1])

    if not chunks_path.exists():
        print(f"Error: {chunks_path} not found", file=sys.stderr)
        sys.exit(1)
    if not topic_slug:
        print("Error: --topic is required", file=sys.stderr)
        sys.exit(1)

    chunks = json.loads(chunks_path.read_text())
    hints = generate_concept_hints(chunks, topic_slug, domain, top_n)

    if output_path:
        write_concept_hints(hints, output_path)
        print(f"✓ Concept hints written to {output_path}")
    else:
        # Default: .scratch/concepts/{slug}.json
        default_path = Path(".scratch/concepts") / f"{topic_slug}.json"
        write_concept_hints(hints, default_path)
        print(f"✓ Concept hints written to {default_path}")

    print(f"  Concepts:  {len(hints['concepts'])}")
    print(f"  Edges:     {len(hints['edges'])}")
    print(f"  Target:    {hints['coverage_target']} concepts to cover")


if __name__ == "__main__":
    main()
