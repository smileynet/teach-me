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

# Windows consoles default to cp1252; force UTF-8 so ✓/→/emoji glyphs don't crash (#265).
import sys as _sys
if hasattr(_sys.stdout, "reconfigure"):
    _sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(_sys.stderr, "reconfigure"):
    _sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from extract_concepts import extract_concepts, ConceptGraph, _normalize_term
from map_from_chunks import slugify

try:
    import inflection
except ImportError:
    inflection = None  # Graceful degradation — skip singularization

# L-level thresholds (calibrated against test fixtures:
# "socket" = 0.818 → L1, "batch processing" = 0.200 → L3)
L1_THRESHOLD = 0.5   # Core concepts — recall level
L2_THRESHOLD = 0.2   # Practice concepts — understand/apply
# Below L2 → L3 (analysis/synthesis)

# Single words that are never meaningful as edge concepts or standalone concepts.
# These pass the >50% frequency filter but are semantically empty.
GENERIC_EDGE_TERMS = frozenset({
    "time", "single", "point", "change", "root", "system", "code",
    "approach", "way", "thing", "state", "states", "type", "types",
    "value", "values", "case", "cases", "use", "color",
    "trick", "method", "function", "data", "result", "set",
    "number", "part", "name", "form", "level", "place",
    "world", "space", "texture", "vertex", "software",
})

# Multi-word terms that should never be collapsed during dedup
PROTECTED_COMPOUNDS = frozenset({
    "borrow checker", "render pipeline", "thread pool",
    "garbage collector", "type system", "pattern matching",
    "cache invalidation", "consistent hashing", "shader global",
    "gradient texture", "toon shading", "light function",
})


def _dedup_key(term: str) -> str:
    """Compute deduplication key for a concept term.

    Single-word terms get singularized. Multi-word terms are protected
    from morphological changes (they're compound concepts, not words).
    """
    normalized = term.lower().strip()

    # Protect multi-word compounds
    if " " in normalized:
        if normalized in PROTECTED_COMPOUNDS:
            return normalized
        # For unprotected multi-word terms, singularize last word only
        parts = normalized.split()
        if inflection and len(parts[-1]) > 3:
            parts[-1] = inflection.singularize(parts[-1])
        return " ".join(parts)

    # Single-word: singularize
    if inflection and len(normalized) > 3:
        return inflection.singularize(normalized)
    return normalized


def deduplicate_concepts(concepts: list) -> list:
    """Merge near-synonym concepts, keeping the highest-scoring variant.

    Groups by dedup key (singularized form), merges defined_in/used_in,
    keeps the display form of the highest-scoring member.
    """
    groups: dict[str, list] = {}
    for c in concepts:
        key = _dedup_key(c.term)
        if key not in groups:
            groups[key] = []
        groups[key].append(c)

    deduped = []
    for key, members in groups.items():
        # Keep highest-scoring member as the representative
        members.sort(key=lambda m: m.score, reverse=True)
        best = members[0]
        # Merge locations from duplicates
        for other in members[1:]:
            best.defined_in = list(set(best.defined_in + other.defined_in))
            best.used_in = list(set(best.used_in + other.used_in))
        deduped.append(best)

    deduped.sort(key=lambda c: c.score, reverse=True)
    return deduped


def filter_generic_terms(concepts: list, chunks: list[dict], threshold: float = 0.5) -> list:
    """Remove concepts appearing in more than threshold fraction of chunks.

    Terms that appear in >50% of chunks are corpus-wide noise, not
    domain-specific concepts.
    """
    total_chunks = max(len(chunks), 1)
    filtered = []
    for c in concepts:
        appearing_in = set(c.defined_in + c.used_in)
        chunk_freq = len(appearing_in) / total_chunks
        if chunk_freq <= threshold:
            filtered.append(c)
    return filtered


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


def compute_composite_score(
    foundational_score: float,
    prerequisite_depth: int,
    first_appear: int,
    last_appear: int,
    total_chunks: int,
    in_degree: int,
) -> float:
    """Compute composite difficulty/foundationality score.

    Combines multiple signals to determine how foundational a concept is:
    - Depth in prerequisite graph (deeper = more advanced)
    - Frequency/foundational score (higher = more foundational)
    - First appearance position (earlier = more foundational)
    - Survivor time (appears across more of the document = more foundational)
    - In-degree (more things depend on it = more foundational)

    Lower composite score = more foundational (L1).
    Higher composite score = more advanced (L3).
    """
    # Normalize each signal to 0-1
    depth_norm = min(prerequisite_depth / 5.0, 1.0)  # cap at depth 5
    freq_norm = 1.0 - min(foundational_score / 1.0, 1.0)  # invert: high freq = low score
    first_norm = first_appear / max(total_chunks - 1, 1)  # 0 = first chunk, 1 = last
    survivor = (last_appear - first_appear) / max(total_chunks - 1, 1)
    survivor_norm = 1.0 - survivor  # invert: long survivor = foundational
    indegree_norm = 1.0 - min(in_degree / 5.0, 1.0)  # invert: high in-degree = foundational

    # Weighted composite (higher = more advanced)
    composite = (
        depth_norm * 0.30
        + freq_norm * 0.20
        + first_norm * 0.20
        + survivor_norm * 0.15
        + indegree_norm * 0.15
    )
    return round(composite, 3)


def assign_levels_by_percentile(concepts_out: list[dict]) -> None:
    """Assign L-levels based on composite score percentiles.

    L1 (bottom 20% composite = most foundational)
    L2 (middle 50%)
    L3 (top 30% = most advanced/specialized)
    """
    if len(concepts_out) < 3:
        # Too few to percentile — use simple heuristic
        for i, c in enumerate(concepts_out):
            c["level"] = "L1" if i == 0 else "L2"
        return

    scores = sorted([c["_composite"] for c in concepts_out])
    n = len(scores)

    # Check for uniform scores (no differentiation possible)
    if scores[0] == scores[-1]:
        # All equal — assign by position (first = L1, middle = L2, last = L3)
        for i, c in enumerate(concepts_out):
            frac = i / max(n - 1, 1)
            if frac <= 0.2:
                c["level"] = "L1"
            elif frac <= 0.7:
                c["level"] = "L2"
            else:
                c["level"] = "L3"
        return

    p20 = scores[int(n * 0.2)]  # top 20% foundational threshold
    p70 = scores[int(n * 0.7)]  # top 70% = bottom 30% advanced threshold

    for c in concepts_out:
        if c["_composite"] <= p20:
            c["level"] = "L1"
        elif c["_composite"] <= p70:
            c["level"] = "L2"
        else:
            c["level"] = "L3"


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


def _topic_salience(defined_in, used_in, target_indices, total_chunks, alpha=0.1):
    """Smoothed log-ratio of in-topic vs rest chunk-appearance (#286).

    Add-alpha smoothed so a single-chunk term can't score unbounded-high — the raw
    freq_in_topic/freq_in_domain ratio's documented failure mode on ~10-chunk corpora
    (rare-term over-weighting). Higher = more distinctive to this topic.
    """
    app = set(defined_in + used_in)
    tgt = set(target_indices)
    topic = len(app & tgt)
    rest = len(app - tgt)
    topic_total = max(len(tgt), 1)
    rest_total = max(total_chunks - len(tgt), 1)
    v = 2  # smoothing vocab size (in-topic vs rest)
    return (math.log((topic + alpha) / (topic_total + alpha * v))
            - math.log((rest + alpha) / (rest_total + alpha * v)))


def _select_anchors_and_hooks(concepts_out, target_indices, total_chunks, top_n,
                              n_anchors=2):
    """Pick ~n_anchors in-topic ANCHORS (footing) + the rest as distinctive HOOKS (#286).

    2 anchors + (top_n-2) hooks: enough pervasive footing for a learner to recognize the
    topic, but a majority of slots go to distinctive hooks so sibling topics don't look
    identical. Anchors: highest in-topic appearance (tiebreak global score). Hooks: highest
    smoothed topic-salience (tiebreak global score, then term length to favor real concepts
    over fragments). Falls back to score-desc if the topic had no matchable chunks.
    """
    tgt = set(target_indices)

    def in_topic_count(c):
        return len(set(c["defined_in"] + c["used_in"]) & tgt)

    def pervasiveness(c):
        # Fraction of ALL chunks the term appears in — high = domain-wide connective,
        # a bad anchor (footing should be topic-central, not everywhere).
        return len(set(c["defined_in"] + c["used_in"])) / max(total_chunks, 1)

    relevant = [c for c in concepts_out if in_topic_count(c) > 0]
    if not relevant:
        return sorted(concepts_out, key=lambda c: -c["score"])[:top_n]

    # Anchors: topic-central footing. Exclude domain-pervasive terms (>40% of all chunks)
    # so connectives like "rules"/"ensures" can't win footing slots (#286). Fall back to
    # the full relevant set if the cap would starve the anchor band.
    anchor_pool = [c for c in relevant if pervasiveness(c) <= 0.4] or relevant
    anchors = sorted(anchor_pool, key=lambda c: (-in_topic_count(c), -c["score"]))[:n_anchors]
    anchor_terms = {c["term"] for c in anchors}

    def hook_key(c):
        # On single-chunk topics every topic-exclusive term ties on smoothed salience, so
        # YAKE's own intra-document relevance (LOWER=better: freq+position+casing) is the
        # real discriminator — it ranks Box/Drop/NdotL above generic connectives. Order:
        # (1) salience desc, (2) YAKE asc (None last), (3) concept-shaped, (4) score, (5) len.
        term = c["term"]
        concept_shaped = (" " in term) or (term[:1].isupper() and term.lower() != term)
        yake = c.get("_yake")
        return (
            -_topic_salience(c["defined_in"], c["used_in"], target_indices, total_chunks),
            yake if yake is not None else float("inf"),
            not concept_shaped,
            -c["score"],
            -len(term),
        )

    hooks = sorted(
        (c for c in relevant if c["term"] not in anchor_terms), key=hook_key
    )[: max(0, top_n - len(anchors))]
    return anchors + hooks


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
    # Run concept extraction on all chunks. Pull a WIDE candidate pool (not just the
    # global top-N): the two-band selection (#286) needs low-global-score but
    # topic-distinctive concepts to survive as hook candidates — a narrow cap starves them.
    result = extract_concepts(chunks, top_n=max(top_n * 8, 40))

    # Quality filters: deduplicate near-synonyms, remove generic terms
    result_concepts = deduplicate_concepts(result.concepts)
    result_concepts = filter_generic_terms(result_concepts, chunks, threshold=0.5)
    # Filter generic single-word terms that pass frequency filter but are semantically empty
    result_concepts = [
        c for c in result_concepts
        if c.term.lower().strip() not in GENERIC_EDGE_TERMS
    ]
    # Filter the domain/language name itself — it's not a concept to learn.
    # Token/stem match, not exact-slug: "rust" from "rust-fundamentals" must be caught
    # so `Rust` stops appearing as a top concept (#286).
    domain_tokens = set(domain.lower().replace("-", " ").split()) | {domain.lower()}
    result_concepts = [
        c for c in result_concepts
        if c.term.lower().strip() not in domain_tokens
        and _normalize_term(c.term) not in domain_tokens
    ]

    # Find the chunk index for the target topic
    target_indices = []
    for i, chunk in enumerate(chunks):
        chunk_slug = slugify(chunk.get("heading", ""))
        if chunk_slug == topic_slug or topic_slug in chunk_slug:
            target_indices.append(i)

    # Build concept list with composite scoring
    total_chunks = max(len(chunks), 1)
    concepts_out = []
    # Candidate pool must be TOPIC-AWARE (#286), not just the global top-N. Hook candidates
    # like Box/Drop are in ONE late chunk, so their global foundational score is tiny and a
    # rank-N truncation drops them before the two-band selection can surface them. Include
    # EVERY concept that touches a target-topic chunk, plus the global top-40 (for anchors).
    _tgt = set(target_indices)
    _topic_relevant = [c for c in result_concepts
                       if _tgt & set(c.defined_in + c.used_in)]
    _global_top = result_concepts[:40]
    _seen = set()
    candidate_pool = []
    for c in _topic_relevant + _global_top:
        if id(c) not in _seen:
            _seen.add(id(c))
            candidate_pool.append(c)
    for concept in candidate_pool:
        # Check if concept is relevant to target topic
        relevant_to_target = any(
            idx in target_indices
            for idx in concept.defined_in + concept.used_in
        )

        # Compute prerequisite depth
        depth = 0
        in_degree = 0
        for idx in concept.defined_in:
            if result.graph.has_node(idx):
                depth = max(depth, compute_prerequisite_depth(result.graph, idx))
                in_degree += result.graph.in_degree(idx)

        # Compute first/last appearance for survivor time
        all_appearances = sorted(set(concept.defined_in + concept.used_in))
        first_appear = all_appearances[0] if all_appearances else 0
        last_appear = all_appearances[-1] if all_appearances else 0

        # Composite score for L-level assignment
        composite = compute_composite_score(
            foundational_score=concept.score,
            prerequisite_depth=depth,
            first_appear=first_appear,
            last_appear=last_appear,
            total_chunks=total_chunks,
            in_degree=in_degree,
        )

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
            "level": "L2",  # placeholder — assigned by percentile below
            "_composite": composite,
            "_yake": concept.yake_score,  # internal, for the #286 hook tiebreak; popped before write
            "defined_in": concept.defined_in,
            "used_in": concept.used_in,
            "prerequisite_of": prereq_of[:5],
            "relevant_to_target": relevant_to_target,
        })

    # Assign L-levels by percentile of composite scores
    assign_levels_by_percentile(concepts_out)

    # Two-band selection (#286): a few pervasive ANCHORS (footing) + a couple distinctive
    # HOOKS (the gap). Interest-driven discovery wants both, not pure distinctiveness — an
    # obscure top-salience term with no footing is inert (inverted-U of curiosity).
    concepts_out = _select_anchors_and_hooks(
        concepts_out, target_indices, total_chunks, top_n
    )

    # Remove internal fields
    for c in concepts_out:
        c.pop("_composite", None)
        c.pop("_yake", None)

    # Build edge suggestions for question framing — domain-specific only
    generic_terms = {
        _normalize_term(c.term)
        for c in result.concepts
        if len(set(c.defined_in + c.used_in)) / total_chunks > 0.5
    }

    edges_out = []
    for edge in result.edges:
        if edge.source in target_indices or edge.target in target_indices:
            # Fix 6: Skip edges referencing generic terms
            if _normalize_term(edge.concept) in generic_terms:
                continue
            # Fix 7: Skip edges with single-word generic concepts
            if edge.concept.lower().strip() in GENERIC_EDGE_TERMS:
                continue
            # Fix 8: Skip edges referencing the domain/language name itself
            if edge.concept.lower().strip() == domain.lower():
                continue
            source_heading = chunks[edge.source].get("heading", "") if edge.source < len(chunks) else ""
            target_heading = chunks[edge.target].get("heading", "") if edge.target < len(chunks) else ""
            suggestion = _generate_question_suggestion(edge, source_heading, target_heading)
            if suggestion:  # Skip empty suggestions
                edges_out.append({
                    "from_topic": slugify(source_heading),
                    "to_topic": slugify(target_heading),
                    "concept": edge.concept,
                    "type": edge.edge_type,
                    "suggestion": suggestion,
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
