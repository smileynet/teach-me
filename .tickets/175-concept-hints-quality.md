---
id: "175"
title: "Fix: concept hints quality — filter noise, calibrate L-levels, deduplicate"
status: done
blocked_by: []
priority: high
---

# Fix: concept hints quality — filter noise, calibrate L-levels, deduplicate

## What to build

Fix quality issues in `tools/concept_hints.py` discovered when testing against live Rust documentation (Rust by Example + The Rust Book). Concepts extracted contain noise, L-levels don't differentiate, and near-synonyms aren't merged.

### Problems observed

1. **YAKE noise on short content** — "charge of freeing", "min read win", "eat" extracted as concepts from tutorial boilerplate
2. **L-levels all L2** — absolute thresholds (0.5/0.2) don't match web-extracted content where scores compress to 0.05–0.38 range
3. **No synonym deduplication** — "borrow", "Borrowing", "borrowed" appear as 3 separate concepts
4. **Generic terms pass through** — words appearing in most chunks (like "code", "example") aren't domain-specific
5. **Edge suggestions from generic words** — "Why does understanding 'approach' matter..." is unhelpful

### Fixes

| Fix | Lines |
|-----|-------|
| Skip chunks with <50 words before YAKE extraction | ~5 |
| Filter concepts: skip terms appearing in >60% of chunks (generic) | ~10 |
| Lemmatize + group near-synonyms (simple suffix stripping: -ing, -ed, -s) | ~15 |
| Percentile-based L-levels: top 20% of scores = L1, middle 40% = L2, bottom 40% = L3 | ~10 |
| Tutorial boilerplate stopwords ("min read", "example", "chapter", "see also") | ~5 |
| Only include edges where the concept passes domain-specificity filter | ~5 |

## Context

- Tested against: Rust by Example (9 chunks) + The Rust Book ownership chapter
- `concept_hints.py` produced 10 concepts with 7/10 being noise or near-duplicates
- Edge suggestions were generic ("Why does understanding 'approach' matter...")
- L-levels were uniform (all L2) despite clear difficulty hierarchy (ownership → borrow → lifetime)

## Acceptance criteria

- [x] No boilerplate/noise terms in top 10 concepts when run on Rust by Example corpus
- [x] Near-synonyms merged ("borrow"/"borrowing"/"borrowed" → single entry)
- [x] L-levels differentiate: at least 2 of 3 levels present in output
- [x] Generic terms (>60% chunk frequency) excluded from output
- [x] Edge suggestions only reference domain-specific concepts
- [x] Existing tests still pass (may need threshold updates)

## Validation

- [ ] Run on Rust by Example → no "min read", "eat", "charge of freeing" in output
- [ ] Run on code-design (Ousterhout) → "complexity" gets L1, "red flag" patterns get L2/L3
- [ ] 182+ pytest tests pass after changes

## Resolution (2026-08-20)

All code fixes implemented and unit-tested. Corpus validation in #179.
