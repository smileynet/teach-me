---
id: "286"
title: "concept_hints: topic-local salience ranking (fix per-topic differentiation)"
status: done
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

## RESEARCH REFRAME (2026-09-02) — goal is anchors+hooks, NOT pure distinctiveness

Two research passes (`.scratch/reconcile-233/r286-casual-learning.md`, `r286-salience.md`)
changed the objective. teach-me is an INTEREST-DRIVEN discovery tool (CONTEXT.md "casual
exploration posture"), not academic extraction — and the learning science says pure
per-topic distinctiveness is the WRONG sole goal:

- **Curiosity/interest follow an inverted-U with prior knowledge** (Loewenstein 1994; Kang
  2009; Donnellan 2022). A hint sparks only when the learner has enough footing to feel a
  gap. A maximally-distinctive/obscure term sits at the "know nothing" tail → no gap felt →
  inert. Pure distinctiveness surfaces exactly those inert terms (rarity ↔ obscurity).
- **The right 5-hint shape = 2-3 pervasive ANCHORS + 1-2 distinctive HOOKS.** Anchors
  supply the "I already know something here" footing that interest requires; hooks open the
  closeable gap. Anchors are NOT wasted coverage — they're the precondition for hooks to land.
- **The ticket's original `freq_in_topic/freq_in_domain` ratio is the worst form** for a
  ~10-chunk corpus: it's word-doc PMI, with unbounded rare-term over-weighting (a once-only
  term scores maximal on one observation). Must be smoothed + count-floored.

So the fix is NOT "rank by distinctiveness." It's: **keep a few high-in-topic anchors,
ADD a small number of distinctive hooks scored by a SMOOTHED salience with a count floor,
and gate everything so obscure single-mention noise can't fill slots.**

## What to build (revised)

1. **Two-band selection for the top-5** (replaces "rank purely by salience"):
   - **Anchors (≈3):** concepts with the highest presence WITHIN the topic's own chunks
     (topic document-frequency), regardless of domain-wide spread — the footing.
   - **Hooks (≈2):** concepts with the highest SMOOTHED salience — distinctive to this topic
     — subject to a minimum count/df floor so single-mention trivia can't qualify.
   - Ratio is a tunable (start 3:2); dedup so an anchor and hook aren't the same concept.
2. **Smoothed salience for the hook band** (NOT raw ratio): smoothed log-ratio
   `log((topic+α)/(topic_total+αV)) − log((rest+α)/(rest_total+αV))`, α≈0.1, gated by
   "appears in ≥2 of the topic's chunks OR raw count ≥2". Pure stdlib (`math.log`). (Weighted
   log-odds w/ Dirichlet prior is the gold standard but likely over-engineered at ~10 chunks
   — start with smoothed log-ratio; note the upgrade path.)
3. **Fix domain-name leakage**: token/stem-match the domain name (`rust` from
   `rust-fundamentals`), not exact-slug compare, so `Rust` stops appearing as a "concept".
4. **Harder restatement dedup + stoplist**: merge `owner`/`single owner`/`ownership`
   clusters; add extraction noise (`important factor`, `difficulties`, `provide powerful`).

## Acceptance criteria

- [x] Top-5 uses two-band selection: ~2 in-topic anchors + ~3 smoothed-salience hooks (n_anchors=2)
- [x] Hook salience is SMOOTHED (log-ratio w/ α) + tiebroken by YAKE's own intra-doc score (the real discriminator on single-chunk topics) — no raw ratio, no single-mention trivia
- [x] Re-run the #176 corpus (3 domains × 10 topics): **30/30 topics (100%)** have ≥1 distinctive concept absent from sibling topics, while still showing shared anchors — far exceeds the >60% bar
- [x] The 3 worst cases now surface a hook: `smart-pointers-box-rc-arc` → Smart pointers/ownership semantics; `lifetimes` → remain valid/long references; `triplanar-mapping-algorithm` → triplanar insight/major axis
- [x] Domain name (`Rust`, etc.) no longer appears as a top concept (0 hits across 30 topics)
- [x] Good cases don't regress (`smoothstep` → smoothstep/oblique angles; `slices` → Slices/contiguous sequence; `move-semantics` → ownership moves/binding)
- [x] Existing concept-extraction tests still pass (46); added 2 differentiation regression tests (48 total)
- [x] `mise run verify` passes

## Resolution (2026-09-02)

The fix required BOTH a ranking change AND an extraction-side change — ranking alone
plateaued at 57%. Root cause of the plateau (diagnosed empirically): the good hook
candidates (Box, Drop, NdotL) exist in extraction but have tiny GLOBAL foundational scores
(they're in 1 late chunk of ~10), so the candidate loop's global-top-N truncation dropped
them before the two-band selection ran.

**Changes:**
1. **Topic-aware candidate pool** (`concept_hints.py`, the decisive fix): build candidates
   from EVERY concept touching a target-topic chunk + the global top-40 — not just global
   top-N. This is what unblocked the stuck topics (Box/Drop now reach selection).
2. **Preserve YAKE's per-term score** (`extract_concepts.py`): added `yake_score` to the
   `Concept` dataclass (new field, default None — breaks 0 tests; `score` untouched so the
   range/sort tests hold), captured from the `_score` previously discarded at line 295 (min
   across chunks = YAKE's "best"), emitted in `to_json`. YAKE's score bakes in
   freq+position+casing, so it ranks Box/NdotL above generic connectives — the tiebreak the
   smoothed-salience tie was missing on single-chunk topics.
3. **Two-band selection** (`concept_hints.py`): 2 anchors (in-topic footing, with a >40%
   domain-pervasiveness cap so connectives can't win footing slots) + 3 hooks (smoothed
   salience → YAKE asc → concept-shaped → score → length).
4. **Domain-name token filter**: token/stem match, not exact-slug (`rust` from
   `rust-fundamentals`).

**Result:** topic differentiation 17% → **100%** (30/30), domain-name leakage eliminated,
good cases preserved. `pytest` 256 passed (+2 differentiation regression tests); `mise run
verify` EXIT 0. Evidence: `.scratch/reconcile-233/r286-extraction-*.md` (research+review),
verify script output.

Unblocks #176 (its coverage-report + generate-lesson ACs are the acceptance demo for these
now-differentiated hints).

## References

- Validation evidence: `.scratch/reconcile-233/concept-digest.txt`, `r-concept-review.md`
- Research (reframe): `.scratch/reconcile-233/r286-casual-learning.md` (anchors+hooks, inverted-U),
  `r286-salience.md` (smoothed log-ratio > raw ratio; count floor; weighted-log-odds upgrade path)
- Code reality: `.scratch/reconcile-233/r286-code-review.md` — salience computable from
  `Concept.defined_in/used_in` ∩ `target_indices`, NO change to extract_concepts.py; ranking
  is the sort at `concept_hints.py:353`; `assign_levels_by_percentile` is order-independent
  (main path); 46 tests, none assert sort order.
- Consumers: `.scratch/reconcile-233/r286-consumers.md` — output is ephemeral (`.scratch/`),
  no consumer keys off slot/order; invariants to keep: `level ∈ {L1,L2,L3}`, ≥1
  `relevant_to_target` survives truncation, top-level keys stable.
- Prior limitation note: #179 "Known Limitation"; original quality fixes: #175
- Tool: `tools/concept_hints.py` (ranking in `generate_concept_hints`, sort at line ~353)
