---
id: "161"
title: "Spike: TF-IDF vs YAKE keyword Jaccard for cross-source topic matching"
status: done
blocked_by: []
priority: low
---

# Spike: TF-IDF vs YAKE keyword Jaccard for cross-source topic matching

## Question to answer

For cross-source topic matching (given topic T from source A, find the best-matching topic in source B), which approach produces better matches — YAKE keyword Jaccard, TF-IDF cosine similarity, or a combination? When does each fail?

## Context

- YAKE is already in the codebase (`extract_keywords_per_chunk`) — tested on single-source concept extraction (#149)
- TF-IDF would require scikit-learn (new dependency)
- The use case is different from #149: matching *across* two independently-chunked sources on the same domain, not building a dependency graph within one source
- Concern: YAKE has no corpus-level weighting — common terms (e.g., "data", "configuration") may cause false positive matches

## Approach

1. **Select test corpus** — pick 2 existing example workspace sources that overlap (e.g., two documents about the same domain with shared and distinct topics). If none exist, create a small fixture with ~8 chunks each, deliberate overlap (3-4 shared topics, 4-5 unique to each).

2. **Build ground truth** — manually label which topics from source A match which topics in source B (exact match, partial overlap, no match).

3. **Implement both matchers in a scratch script:**
   - **YAKE Jaccard:** `extract_keywords_per_chunk` on each source → Jaccard similarity on normalized keyword sets per topic pair
   - **TF-IDF cosine:** `TfidfVectorizer` on chunk content → cosine similarity matrix across sources
   - **Hybrid:** YAKE pre-filter (Jaccard > 0.1) → TF-IDF verification on candidates

4. **Evaluate:**
   - Precision: what % of proposed matches are correct?
   - Recall: what % of true matches are found?
   - Threshold sensitivity: how do results change at 0.3/0.5/0.7 cutoffs?
   - False positive analysis: what causes bad matches?

## Evaluation criteria

| Metric | Acceptable | Good |
|--------|-----------|------|
| Precision @ best threshold | ≥70% | ≥85% |
| Recall @ best threshold | ≥60% | ≥80% |
| False positives from generic terms | Identified and documented | Eliminated by approach |
| Threshold stability | One threshold works for test corpus | Works across 2+ corpora |

## Acceptance criteria

- [x] Ground truth labeled for test corpus (which topics match across sources)
- [x] YAKE Jaccard scores computed for all topic pairs
- [x] TF-IDF cosine scores computed for all topic pairs
- [x] Side-by-side comparison with precision/recall at multiple thresholds
- [x] Recommendation: which to use for #141, with evidence
- [x] If TF-IDF wins: confirm scikit-learn is acceptable (size, install, license)
- [x] Results written to `.scratch/spikes/tfidf-vs-yake.md`

## Result

**TF-IDF dominates; YAKE alone is insufficient; hybrid (TF-IDF + YAKE boost) is best (F1=0.93).**

YAKE fails at cross-source matching because it has no corpus-level weighting — domain-ubiquitous terms like "kubernetes" match everything equally. TF-IDF's IDF component solves this exactly. scikit-learn is already installed (BSD, no torch). See `.scratch/spikes/tfidf-vs-yake.md` for full findings.

## Validation

- **Reproducibility:** `.venv/bin/python .scratch/spikes/tfidf_vs_yake_spike.py` runs without error and produces consistent quantitative results
- **Ground truth quality:** Test corpus manually labeled with 4 exact matches, 3 partial overlaps across 8-chunk sources
- **Comparison completeness:** All three approaches (YAKE, TF-IDF, hybrid) evaluated at multiple thresholds with precision/recall/F1
