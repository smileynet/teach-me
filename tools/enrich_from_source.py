#!/usr/bin/env python3
"""enrich_from_source.py — Multi-source enrichment for existing domains.

When a second source is ingested for an existing domain, this module:
1. Matches new chunks to existing topics (TF-IDF cosine + YAKE boost)
2. Detects conflict signals between matched pairs (dates, numbers, negation)
3. Writes an append-only enrichment overlay (sources/{domain}/enrichments.json)

Architecture: overlay pattern — original sources are never mutated. Enrichments
form a separate layer consumed by the teach skill at lesson generation time.

Usage:
    python tools/enrich_from_source.py <existing-chunks.json> <new-chunks.json> --domain D --workspace W
"""

from __future__ import annotations

# Windows consoles default to cp1252; force UTF-8 so ✓/→/emoji glyphs don't crash (#265).
import sys as _sys
if hasattr(_sys.stdout, "reconfigure"):
    _sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(_sys.stderr, "reconfigure"):
    _sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import json
import re
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from extract_concepts import extract_keywords_per_chunk, _normalize_term
from map_from_chunks import slugify


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------


@dataclass
class TopicMatch:
    """A match between a new chunk and an existing topic."""

    topic_slug: str
    new_chunk_index: int
    new_chunk_heading: str
    match_confidence: float
    match_method: str
    conflict_signals: list[str] = field(default_factory=list)
    conflict_type: str | None = None  # complementary|opinion|outdated|factual


@dataclass
class EnrichmentRecord:
    """One enrichment operation — appended to enrichments.json."""

    source_id: str
    ingested_at: str
    matches: list[dict]
    new_topics_proposed: list[dict]


# ---------------------------------------------------------------------------
# Topic matching (TF-IDF cosine + YAKE boost)
# ---------------------------------------------------------------------------

# Thresholds validated by spike #161 (F1=0.93 on container orchestration corpus)
HIGH_CONFIDENCE = 0.10
CANDIDATE_THRESHOLD = 0.05
YAKE_BOOST = 0.03


def match_topics(
    existing_chunks: list[dict],
    new_chunks: list[dict],
    high_threshold: float = HIGH_CONFIDENCE,
    low_threshold: float = CANDIDATE_THRESHOLD,
) -> tuple[list[TopicMatch], list[int]]:
    """Match new chunks to existing topics using TF-IDF cosine + YAKE keyword boost.

    Returns:
        (matches, unmatched_indices) where unmatched_indices are new chunks
        with no match above low_threshold.
    """
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity

    if not existing_chunks or not new_chunks:
        return [], list(range(len(new_chunks)))

    # Build content arrays
    existing_content = [c.get("content", "") for c in existing_chunks]
    new_content = [c.get("content", "") for c in new_chunks]

    # Filter out empty content
    valid_existing = [(i, c) for i, c in enumerate(existing_content) if c.strip()]
    valid_new = [(i, c) for i, c in enumerate(new_content) if c.strip()]

    if not valid_existing or not valid_new:
        return [], list(range(len(new_chunks)))

    # Fit TF-IDF on combined corpus
    all_docs = [c for _, c in valid_existing] + [c for _, c in valid_new]
    vectorizer = TfidfVectorizer(
        stop_words="english",
        max_features=5000,
        ngram_range=(1, 2),
    )
    tfidf_matrix = vectorizer.fit_transform(all_docs)

    n_existing = len(valid_existing)
    matrix_existing = tfidf_matrix[:n_existing]
    matrix_new = tfidf_matrix[n_existing:]

    # Cosine similarity (new × existing)
    cos_sim = cosine_similarity(matrix_new, matrix_existing)

    # YAKE keyword boost
    kw_existing = extract_keywords_per_chunk(existing_chunks, top_n=8)
    kw_new = extract_keywords_per_chunk(new_chunks, top_n=8)

    existing_sets = []
    for chunk_kws in kw_existing:
        existing_sets.append({_normalize_term(kw) for kw, _ in chunk_kws})

    new_sets = []
    for chunk_kws in kw_new:
        new_sets.append({_normalize_term(kw) for kw, _ in chunk_kws})

    # Compute hybrid scores and find best match per new chunk
    matches = []
    unmatched = []

    for new_local_idx, (new_orig_idx, _) in enumerate(valid_new):
        best_score = 0.0
        best_existing_idx = -1

        for ex_local_idx, (ex_orig_idx, _) in enumerate(valid_existing):
            tfidf_score = float(cos_sim[new_local_idx, ex_local_idx])

            # YAKE keyword overlap boost
            shared_count = len(new_sets[new_orig_idx] & existing_sets[ex_orig_idx])
            hybrid_score = tfidf_score + YAKE_BOOST * shared_count

            if hybrid_score > best_score:
                best_score = hybrid_score
                best_existing_idx = ex_orig_idx

        if best_score >= low_threshold and best_existing_idx >= 0:
            existing_heading = existing_chunks[best_existing_idx].get("heading", "")
            confidence_label = "high" if best_score >= high_threshold else "candidate"
            matches.append(TopicMatch(
                topic_slug=slugify(existing_heading),
                new_chunk_index=new_orig_idx,
                new_chunk_heading=new_chunks[new_orig_idx].get("heading", ""),
                match_confidence=round(best_score, 4),
                match_method=f"tfidf_cosine+yake_boost ({confidence_label})",
            ))
        else:
            unmatched.append(new_orig_idx)

    # Add indices for new chunks that were filtered out (empty content)
    all_new_valid_indices = {i for i, _ in valid_new}
    for i in range(len(new_chunks)):
        if i not in all_new_valid_indices:
            unmatched.append(i)

    return matches, sorted(unmatched)


# ---------------------------------------------------------------------------
# Conflict detection (heuristic)
# ---------------------------------------------------------------------------

# Patterns for extracting dates and numbers
_DATE_PATTERN = re.compile(
    r"\b(20[0-2]\d|19\d\d)\b"  # 4-digit year
)
_NUMBER_PATTERN = re.compile(
    r"\b(\d+(?:\.\d+)?)\s*(%|percent|ms|seconds?|minutes?|hours?|GB|MB|TB|nodes?)(?:\b|\s|$|[,.])",
    re.IGNORECASE,
)
_NEGATION_SIGNALS = re.compile(
    r"\b(not|unlike|contrary to|however|in contrast|whereas|but rather|"
    r"no longer|instead of|rather than|does not|cannot|isn't|won't)\b",
    re.IGNORECASE,
)


def detect_conflicts(
    matches: list[TopicMatch],
    existing_chunks: list[dict],
    new_chunks: list[dict],
) -> list[TopicMatch]:
    """Detect conflict signals for each matched pair. Mutates matches in place.

    Conflict types (DRAGged/Conflicts framework):
    - complementary: different angle, no contradiction
    - opinion: subjective disagreement
    - outdated: newer source supersedes older
    - factual: concrete disagreement (numbers, processes)
    """
    for match in matches:
        # Find the existing chunk by slug
        existing_chunk = _find_chunk_by_slug(existing_chunks, match.topic_slug)
        if not existing_chunk:
            continue

        new_chunk = new_chunks[match.new_chunk_index]
        existing_text = existing_chunk.get("content", "")
        new_text = new_chunk.get("content", "")

        signals = []

        # Date comparison
        date_signal = _check_date_conflict(existing_text, new_text)
        if date_signal:
            signals.append(date_signal)

        # Number comparison
        number_signal = _check_number_conflict(existing_text, new_text)
        if number_signal:
            signals.append(number_signal)

        # Negation/opposition language in new source
        negation_signal = _check_negation_signals(new_text)
        if negation_signal:
            signals.append(negation_signal)

        match.conflict_signals = signals
        match.conflict_type = _classify_conflict(signals)

    return matches


def _find_chunk_by_slug(chunks: list[dict], target_slug: str) -> dict | None:
    """Find a chunk whose heading slugifies to the target."""
    for chunk in chunks:
        if slugify(chunk.get("heading", "")) == target_slug:
            return chunk
    return None


def _check_date_conflict(existing_text: str, new_text: str) -> str | None:
    """Detect temporal discrepancy between sources."""
    existing_years = set(_DATE_PATTERN.findall(existing_text))
    new_years = set(_DATE_PATTERN.findall(new_text))

    if existing_years and new_years:
        max_existing = max(int(y) for y in existing_years)
        max_new = max(int(y) for y in new_years)
        if max_new > max_existing:
            return f"temporal_newer({max_new}>{max_existing})"
        elif max_existing > max_new:
            return f"temporal_older({max_new}<{max_existing})"
    return None


def _check_number_conflict(existing_text: str, new_text: str) -> str | None:
    """Detect numerical discrepancy on same-unit measurements."""
    existing_nums = _NUMBER_PATTERN.findall(existing_text)
    new_nums = _NUMBER_PATTERN.findall(new_text)

    if not existing_nums or not new_nums:
        return None

    # Group by unit and check for mismatches
    existing_by_unit = {}
    for val, unit in existing_nums:
        unit_lower = unit.lower().rstrip("s")
        existing_by_unit.setdefault(unit_lower, set()).add(float(val))

    for val, unit in new_nums:
        unit_lower = unit.lower().rstrip("s")
        if unit_lower in existing_by_unit:
            new_val = float(val)
            for ex_val in existing_by_unit[unit_lower]:
                # >20% difference on same unit = potential conflict
                if ex_val > 0 and abs(new_val - ex_val) / ex_val > 0.20:
                    return f"number_mismatch({new_val}{unit}≠{ex_val}{unit_lower})"
    return None


def _check_negation_signals(new_text: str) -> str | None:
    """Detect negation/opposition language in new source."""
    hits = _NEGATION_SIGNALS.findall(new_text)
    # Only flag if negation density is notable (>2 per 100 words)
    word_count = len(new_text.split())
    if word_count > 0 and len(hits) / word_count > 0.02:
        return f"negation_dense({len(hits)}_signals)"
    return None


def _classify_conflict(signals: list[str]) -> str | None:
    """Classify conflict type from signals."""
    if not signals:
        return "complementary"

    for s in signals:
        if s.startswith("number_mismatch"):
            return "factual"
        if s.startswith("temporal_newer"):
            return "outdated"

    if any(s.startswith("negation_dense") for s in signals):
        return "opinion"

    return "complementary"


# ---------------------------------------------------------------------------
# Enrichment overlay writer
# ---------------------------------------------------------------------------


def write_enrichment_overlay(
    workspace: Path,
    domain: str,
    source_id: str,
    matches: list[TopicMatch],
    new_topics: list[dict],
    new_chunks: list[dict],
) -> Path:
    """Append an enrichment record to sources/{domain}/enrichments.json.

    Never overwrites — always appends to the enrichments array.
    """
    overlay_dir = workspace / "sources" / domain
    overlay_dir.mkdir(parents=True, exist_ok=True)
    overlay_path = overlay_dir / "enrichments.json"

    # Load existing or create new
    if overlay_path.exists():
        data = json.loads(overlay_path.read_text())
    else:
        data = {"enrichments": []}

    # Build record
    record = {
        "source_id": source_id,
        "ingested_at": datetime.now(timezone.utc).isoformat(),
        "matches": [
            {
                "topic_slug": m.topic_slug,
                "new_chunk_heading": m.new_chunk_heading,
                "match_confidence": m.match_confidence,
                "match_method": m.match_method,
                "conflict_signals": m.conflict_signals,
                "conflict_type": m.conflict_type,
                "source_passage": _extract_passage(new_chunks, m.new_chunk_index),
            }
            for m in matches
        ],
        "new_topics_proposed": new_topics,
    }

    data["enrichments"].append(record)
    overlay_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    return overlay_path


def _extract_passage(chunks: list[dict], index: int, max_len: int = 300) -> str:
    """Extract a representative passage from a chunk for the overlay."""
    if index >= len(chunks):
        return ""
    content = chunks[index].get("content", "")
    # First substantial sentence(s) up to max_len
    if len(content) <= max_len:
        return content
    # Find sentence boundary near max_len
    cut = content[:max_len].rfind(". ")
    if cut > 100:
        return content[: cut + 1]
    return content[:max_len] + "…"


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------


def enrich_domain(
    new_chunks: list[dict],
    existing_chunks: list[dict],
    workspace: Path,
    domain: str,
    source_id: str,
) -> dict:
    """Run the full enrichment pipeline for a new source on an existing domain.

    Args:
        new_chunks: Chunks from the new source
        existing_chunks: Chunks from the existing (first) source
        workspace: Workspace root
        domain: Domain slug
        source_id: Identifier for the new source (e.g., filename or URL hash)

    Returns:
        Summary dict with enrichment results.
    """
    # 1. Match topics
    matches, unmatched_indices = match_topics(existing_chunks, new_chunks)

    # 2. Detect conflicts
    detect_conflicts(matches, existing_chunks, new_chunks)

    # 3. Propose new topics from unmatched chunks
    new_topics = []
    for idx in unmatched_indices:
        chunk = new_chunks[idx]
        heading = chunk.get("heading", "")
        if not heading or len(chunk.get("content", "").split()) < 20:
            continue
        new_topics.append({
            "slug": slugify(heading),
            "title": heading,
            "source_id": source_id,
            "word_count": chunk.get("word_count", 0),
        })

    # 4. Write overlay
    overlay_path = write_enrichment_overlay(
        workspace, domain, source_id, matches, new_topics, new_chunks
    )

    # 5. Summary
    conflict_count = sum(1 for m in matches if m.conflict_type != "complementary")
    return {
        "matches": len(matches),
        "high_confidence": sum(1 for m in matches if m.match_confidence >= HIGH_CONFIDENCE),
        "candidates": sum(1 for m in matches if m.match_confidence < HIGH_CONFIDENCE),
        "conflicts_detected": conflict_count,
        "new_topics_proposed": len(new_topics),
        "unmatched_chunks": len(unmatched_indices),
        "overlay_path": str(overlay_path),
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> None:
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        print("Usage: python tools/enrich_from_source.py <existing-chunks.json> <new-chunks.json> --domain D --workspace W")
        print("\nMatches new source chunks against existing topics, detects conflicts,")
        print("and writes an enrichment overlay.")
        sys.exit(0)

    existing_path = Path(args[0])
    new_path = Path(args[1])

    workspace = Path("workspace")
    domain = "untitled"
    source_id = "source-2"

    if "--workspace" in args:
        workspace = Path(args[args.index("--workspace") + 1])
    if "--domain" in args:
        domain = args[args.index("--domain") + 1]
    if "--source-id" in args:
        source_id = args[args.index("--source-id") + 1]

    if not existing_path.exists():
        print(f"Error: {existing_path} not found", file=sys.stderr)
        sys.exit(1)
    if not new_path.exists():
        print(f"Error: {new_path} not found", file=sys.stderr)
        sys.exit(1)

    existing_chunks = json.loads(existing_path.read_text())
    new_chunks = json.loads(new_path.read_text())

    result = enrich_domain(new_chunks, existing_chunks, workspace, domain, source_id)

    print("✓ Enrichment complete:")
    print(f"  Matches:          {result['matches']} ({result['high_confidence']} high-confidence, {result['candidates']} candidates)")
    print(f"  Conflicts:        {result['conflicts_detected']}")
    print(f"  New topics:       {result['new_topics_proposed']}")
    print(f"  Overlay written:  {result['overlay_path']}")


if __name__ == "__main__":
    main()
