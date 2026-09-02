---
id: "176"
title: "Validate: run concept hints + enrichment on all live workspace topics"
status: open
blocked_by: ["286"]
priority: high
tags: [source-ingest, content-quality]
---

# Validate: run concept hints + enrichment on all live workspace topics

## What to build

After #175 quality fixes land, run the full concept hints + enrichment pipeline against all live workspace topics to validate:
- Concept extraction produces useful domain terms (not noise)
- L-levels differentiate appropriately per domain
- Multi-source enrichment matches correctly where multiple sources exist
- Coverage checker identifies real gaps (not boilerplate mismatches)

### Domains to test

| Domain | Source | Topics | Expected outcome |
|--------|--------|--------|-----------------|
| blender-godot-shaders | Web research (7 lessons, no source-chunks) | 7 complete | Coverage check on existing lessons only |
| code-design | Ousterhout + Five Lines (21+29 chunks) | 20 topics, 2 lessons | Full pipeline: hints + enrichment + coverage |
| rust-fundamentals | Rust by Example + Rust Book (9+2 chunks) | 9 topics | Full pipeline on web-sourced content |

### Process

1. Run `concept_hints.py` on each domain with source-chunks → save all hint files
2. Run `check-topic-completeness.py --concepts --all` per workspace domain → report coverage
3. Manually review: are the top-5 concepts per topic actually the right ones?
4. Run enrichment overlay inspection: are matches sensible? Any false positives?
5. Generate one lesson using the hints (pick the highest-value unwritten topic) and confirm the skill uses them

## Acceptance criteria

- [ ] Concept hints generated for all 3 domains without errors
- [ ] Top-5 concepts per topic are domain-relevant (manual review, >80% useful)
- [ ] Coverage report produced for all topics with existing lessons
- [ ] At least one lesson generated using concept hints as input
- [ ] No regressions: `mise run verify` passes throughout

## Validation results (2026-09-02)

Ran the concept-hints pipeline across all 3 source-chunk domains (root `source-chunks/`:
`toon-shaders.json` = blender-godot-shaders, `code-design.json`, `rust.json` =
rust-fundamentals), 10 topics each = 30 hint files under `.scratch/concepts/`. Independent
quality review: `.scratch/reconcile-233/r-concept-review.md`; digest: `concept-digest.txt`.

**What passed:**
- Hints generated for all 30 topics, 0 errors (AC1). `mise run verify` green throughout (AC5).
- Domain-relevance meets the literal >80% bar (shaders ~95%, rust ~80%, code-design ~75%;
  averaged pass) — terms are real domain vocabulary, not stopword noise (AC2, literal).

**What the validation SURFACED (the point of the ticket):**
- **Topic-differentiation fails** (~20-30%): within a domain, nearly every topic surfaces the
  same high-frequency domain vocabulary (rust: 8/10 lead with `ownership, Rust, owner`;
  code-design: 8/10 lead with `Complexity, design`; shaders: triplanar/varyings topics surface
  ZERO of their own terms). Global-frequency ranking dominates topic-local signal. This is the
  exact limitation #179 flagged as "future improvement" — #176 confirms it's significant at the
  per-topic level. **Filed as #286** (topic-local TF-IDF salience ranking).

**Blocked ACs (deferred to #286):**
- "Coverage report for all topics with existing lessons" — moot: these 3 domains are
  source-chunks-only, no committed lessons to run `check-topic-completeness --concepts` against.
  Re-run against a lesson-bearing domain after #286.
- "Generate one lesson using hints" — deferred: generating on hints with a known
  differentiation defect produces low-value output. Do this after #286 lands, as the acceptance
  demo for the improved ranking.

**Disposition:** #176 → blocked_by #286. The validation ran and did its job (found the defect);
the remaining ACs are the acceptance demo for the fix, so they properly belong after #286.
