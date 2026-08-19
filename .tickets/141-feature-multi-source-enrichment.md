---
id: "141"
title: "Feature: multi-source enrichment — compound new sources into existing topics with conflict surfacing"
status: open
blocked_by: ["140"]
---

# Feature: multi-source enrichment

## What to build

When a user provides a second source on a topic that already has lessons, compound the new material into existing content rather than replacing it. Uses an overlay architecture: raw sources are immutable, enrichments form a separate append-only layer consumed at lesson generation time.

### Architecture

**Three-layer separation:**
1. Raw layer — `sources/{domain}/raw-{source_id}.*` (immutable)
2. Chunks layer — `source-chunks/{domain}-{source_id}.json` (per-source, never merged)
3. Enrichment overlay — `sources/{domain}/enrichments.json` (append-only log)

**Topic matching (two-stage pipeline):**
- Stage 1: `rapidfuzz.fuzz.token_sort_ratio` on headings (≥75) + TF-IDF cosine on bodies (≥0.50)
- Stage 2: For ambiguous candidates (heading 75–90), `difflib.SequenceMatcher` on body as tiebreaker
- No sentence-transformers (torch constraint)

**Conflict detection (heuristic, lightweight):**
- Date comparison (newer supersedes older)
- Number extraction + comparison on matched sections
- Negation/opposition signals (regex: "not", "unlike", "contrary to", "however")
- Conflict type taxonomy (DRAGged/Conflicts framework): complementary, opinion, outdated, factual

**Enrichment record:**
```json
{
  "source_id": "paper-b",
  "ingested_at": "2026-08-18T10:00:00Z",
  "matches": [{
    "topic_slug": "table-format-metadata",
    "match_confidence": 0.87,
    "match_method": "heading_exact+tfidf_body",
    "conflict_signals": ["number_mismatch"],
    "new_claims": ["..."],
    "source_passage": "..."
  }],
  "new_topics_proposed": []
}
```

**Lesson integration (skill-level, not scripted):**
- Per-claim source badges (not just per-section)
- Typed conflict callouts: "Source A (2023) says X; Source B (2025) says Y — likely updated data"
- Corroboration prompt: "Why might these sources differ?" (per DISC hypothesis — conflict triggers deeper processing)
- Questions additive, never replace existing

### New files
- `tools/enrich_from_source.py` — matching + conflict detection + overlay writing
- `tests/test_enrich_from_source.py`

### Modified files
- `tools/ingest_source.py` — detect existing domain, route to enrich mode
- `tools/map_parser.py` — add `sources` field to Topic dataclass
- `.kiro/skills/teach/SKILL.md` — instruction for consuming enrichment overlay

### New dependency
- `rapidfuzz` (MIT, C++ backend, no torch)

## Acceptance criteria

- [ ] Detect when new source covers existing domain (chunks + MAP already exist)
- [ ] Route to enrich mode instead of overwriting
- [ ] Two-stage topic matching: heading fuzzy + TF-IDF body verification
- [ ] Conflict signal detection: dates, numbers, negation heuristics
- [ ] Conflicts classified by type (complementary/opinion/outdated/factual)
- [ ] Enrichment overlay written as append-only JSON log (sources never mutated)
- [ ] New questions added with provenance to new source; existing questions preserved
- [ ] Unmatched chunks proposed as new topics in MAP.md
- [ ] Works for web-researched topics too (second ingest adds depth)
- [ ] Teach skill consumes overlay to produce per-claim attribution + typed conflict callouts

## Validation

- [ ] Ingest same domain twice with overlapping content → overlay created, originals untouched
- [ ] Ingest conflicting source (different numbers/dates) → conflict signals detected
- [ ] `mise run verify` passes after changes
- [ ] Unit tests cover: matching thresholds, conflict heuristics, overlay append behavior

## Research basis

- Matching: rapidfuzz token_sort ≥85 strong, ≥75 candidate (Mixpeek 2026, arXiv hybrid framework 2025)
- Conflicts: DRAGged/Conflicts taxonomy (Cattan et al. 2025), heuristic signals sufficient for teaching (NLI caps at 65% even with frontier LLMs)
- Pedagogy: DISC hypothesis (Braasch et al.) — conflict triggers sourcing behavior; Documents Model Framework (Perfetti/Rouet/Britt) — claim-level attribution builds intertext models
- Architecture: Karpathy LLM Wiki overlay pattern (2026), W3C PROV-DM append-only principle
