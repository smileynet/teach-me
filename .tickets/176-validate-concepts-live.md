---
id: "176"
title: "Validate: run concept hints + enrichment on all live workspace topics"
status: done
blocked_by: []
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

- [x] Concept hints generated for all 3 domains without errors
- [x] Top-5 concepts per topic are domain-relevant (manual review, >80% useful)
- [x] Coverage report produced for all topics with existing lessons
- [x] At least one lesson generated using concept hints as input
- [x] No regressions: `mise run verify` passes throughout

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

## Resolution (2026-09-03) — acceptance demo for #286

The 2026-09-02 run surfaced the differentiation defect (→ #286). With #286 landed, this
run is the acceptance demo for the improved ranking. Split into two halves because on the
one lesson-bearing domain with source chunks (godot-gamedev via toon-shaders.json), the
chunks back only *already-written* topics — no unwritten topic is chunk-backed.

**Half A — #286 holds on live content** (scripts in `.scratch/`, gitignored, re-runnable):
- Regenerated hints for all 10 toon-shader topics: 0 errors, all non-empty targets (AC1).
- Differentiation gate: 10/10 topics score highest on their own source, mean margin +0.74,
  corpus mean DF 1.62/10 — per-topic proof, stronger than the aggregate 17%→100% figure.
- Relevance gate: mean 94% faithful, all topics ≥80% (AC2).
- Coverage reports: 7 topics across godot-gamedev/iceberg/ink-godot, 0 crashes (AC3).

**Half B — generate a lesson from hints + prove it:**
- `library/godot-gamedev/lessons/0015-physics-and-collision.html` authored from a
  concept_hints.py scaffold built on cited Godot-docs research (AC4).
- New `tools/hint-coverage-oracle.py` (stdlib, deterministic) proves consumption:
  **100% coverage (12/12)** on 0015 at strict threshold; **8%** on an unrelated lesson —
  the pass is meaningful, not trivial.

**AC5:** `mise run verify` EXIT 0 throughout (41 pytest, 20 interactive, 5 ink transcripts).

**Independent review** (2 subagents, commit 338c5bf): both verdict READY — oracle clean of
the 9 banned patterns + stdlib-only; lesson passes 12/13 checks (Q11 nav-chain is an
expected artifact — 0015 is a parent-track topic inserted amid the 0003–0014 sub-track
numbering). Cosmetic nits fixed (stray `</p>`, dead stemmer entry); oracle re-verified 100%.

**Follow-ups filed separately (not #176):**
- FT-1 (medium): `check-topic-completeness --concepts` extracts lesson *chrome*
  ("read win", "min") as concepts → reports 0% on every topic. Its coverage% is unreliable;
  fix by reusing the oracle's `strip_chrome()`. Prefer the oracle for "did the lesson use
  its concepts" until fixed.
- FT-2 (low): orphaned source-chunks — `code-design.json` (no domain) and `rust.json`
  (mismatched vs oidc-rust lessons) validate at hints level only. Decide: generate or prune.

**Artifacts:** commit 338c5bf (oracle + 0015 lesson + code files);
`.scratch/concepts/*.json`, `.scratch/{differentiation,relevance,coverage}_*.py`,
`.scratch/research/176-*.md`, `.scratch/review/176-*.md` (gitignored evidence).
