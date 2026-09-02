---
id: "286"
title: "concept_hints: topic-local salience ranking (fix per-topic differentiation)"
status: open
blocked_by: []
priority: high
tags: [source-ingest, content-quality]
---

# concept_hints: topic-local salience ranking (fix per-topic differentiation)

## Context

Surfaced by #176's full-corpus validation (3 domains × 10 topics) + an independent quality
review (`.scratch/reconcile-233/r-concept-review.md`). `tools/concept_hints.py` ranks concepts
by **global foundational-ness / frequency**, so within a domain nearly every topic surfaces the
SAME high-frequency domain vocabulary instead of the concepts specific to that topic:

- **rust**: 8/10 topics lead with `ownership, Rust, owner, single owner` — `smart-pointers-box-rc-arc`
  surfaces none of Box/Rc/Arc; `lifetimes`/`slices` look identical to `ownership-fundamentals`.
- **code-design**: 8/10 lead with `Complexity, cognitive load, design, software systems` —
  `choosing-names` surfaces nothing about naming; `comments-as-design-tool` nothing about comments.
- **shaders**: the two most-distinct topics (`triplanar-mapping-algorithm`, `world-position-and-varyings`)
  surface ZERO of their own vocabulary — both get the generic `shadow/light/step/toon shading`.

This is the exact "future improvement" #179 flagged as a known, non-blocking limitation for
#175's scope ("add a topic-importance signal alongside foundational-ness"). #176 confirms it is
significant enough at the per-topic level to fix: literal domain-relevance passes (~80-95%) but
topic-differentiation is only ~20-30% — the hints don't help write THAT specific lesson.

## What to build

1. **Topic-local salience ranking** (highest-leverage fix): score each concept by
   `freq_in_topic / freq_in_domain` (TF-IDF-style), not global frequency. This inverts the
   non-differentiation — topic-specific terms rise, pervasive domain terms fall.
2. **Fix domain-name leakage**: the current filter compares against the domain SLUG
   (`rust-fundamentals`), so `Rust` slips through in 8/10 topics. Stem/token-match the domain
   name (and common short forms) instead of exact-slug compare.
3. **Collapse restatement clusters**: `owner / single owner / ownership / Rust safety` occupy 4
   of 5 top slots for one concept — dedup should merge these harder.
4. **Minimum-salience floor + stoplist expansion**: drop tail entries scoring 0.033-0.05 that
   pad the top-5; add extraction noise (`important factor`, `difficulties`, `provide powerful`)
   to the generic stoplist.

## Acceptance criteria

- [ ] Concepts ranked by topic-local salience (freq_in_topic / freq_in_domain), not global freq
- [ ] Re-run the #176 corpus (3 domains × 10 topics): >60% of topics have a top-5 that includes
      at least one topic-specific concept absent from sibling topics (differentiation, not just
      domain-relevance)
- [ ] `smart-pointers-box-rc-arc` surfaces Box/Rc/Arc; `choosing-names` surfaces a naming concept;
      `triplanar-mapping-algorithm` surfaces triplanar/projection — spot-check the 3 worst cases
- [ ] Domain name (`Rust`, etc.) no longer appears as a top concept
- [ ] Existing concept-extraction tests still pass (46+); add a topic-differentiation regression test
- [ ] `mise run verify` passes

## References

- Validation evidence: `.scratch/reconcile-233/concept-digest.txt`, `r-concept-review.md`
- Prior limitation note: #179 "Known Limitation"; original quality fixes: #175
- Tool: `tools/concept_hints.py` (ranking in `compute_composite_score` + `generate_concept_hints`)
