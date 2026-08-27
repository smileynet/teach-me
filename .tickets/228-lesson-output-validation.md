---
id: "228"
title: "Automated fragment-compile + output-correctness validation for lessons"
status: done
blocked_by: []
priority: high
type: feature
tags: ["ink", "validation"]
---

# Automated fragment-compile + output-correctness validation for lessons

## Why (evidence from 2026-08-27 session)

A cluster of bugs in lesson 03 slipped past compile + playthrough + subagent review + author checks — all caught only by a human reading the examples:

1. `-> browse` and `-> road` — diverts to undefined knots (fragment won't compile if pasted)
2. `{greet == 1}` / `{shop > 1}` self-loop read counts — never advance (knot's own read count reflects entry, not internal passes)
3. `* [Enter again]` / `* [Say hello again]` — once-only choices that should be sticky, defeating loop/alternative demos

Structural validation (compile, playthrough-reaches-END) CANNOT catch #2 and #3 — the story still compiles and reaches END, it just produces WRONG OUTPUT. This is a systemic gap.

## Scope (next session)

### Part A — Fragment-compile check (catches bug class #1)
Extract every `<pre data-file/data-mode><code>` block from each lesson, decode HTML entities, compile with inklecate. FAIL on any fragment that has a `-> ` entry divert + knot declaration but doesn't compile. SKIP intentional single-line illustrations (no entry divert). Add to check-lesson.py or a new tool; wire into `mise run verify`.

Also add the **Q15 glossary-coverage check** (deferred from #223): warn if a glossary-data JSON key has no matching `data-term` span in the body. Verified manually via a .scratch coverage script this session; this makes it automated.

### Part B — Golden-transcript validation (catches bug classes #2, #3)
For each reference story: drive through a FIXED choice sequence, capture the output transcript, commit as a `.transcript` fixture. On `mise run verify`, replay and diff. Any output change (intended or regression) surfaces for review. This is the only mechanism that catches wrong-text bugs like the self-loop read count.
- Use bink (already a dep) for deterministic replay
- Seed RANDOM so shuffles are reproducible (or exclude shuffle lines from the diff)
- Fixture format: choice-index sequence + expected transcript

### Part C — Read-count self-loop audit (immediate bug sweep)
Grep lessons 01/02/04 + reference stories for `{knot_name ==` or `{knot_name >` where knot_name is the enclosing knot in a self-loop. Fix any found (lesson 03 already fixed). Consider a lint rule: flag `{X ==` inside knot X that diverts to itself.

### Part D — Sticky-choice audit
Any choice in a location the player can re-enter (loop-back or tunnel-called) must be sticky (+) or have a fallback. Grep for once-only (*) choices in self-looping/re-entered knots. (L02/L04 already fixed via #224; verify none remain.)

## Meta-lesson to encode

"Compiles + reaches END" ≠ "produces correct output." Add to ink authoring guidance / steering:
- Test a knot's read count from OUTSIDE (hub-and-spoke), never self-loop
- Choices in re-enterable locations must be sticky or have fallbacks
- Every code fragment must be pasteable (defined divert targets or clearly-marked illustration)

## Acceptance criteria

- [x] Part A: fragment-compile check runs on all lessons, integrated into verify (DEFERRED — needs committed-lesson-fixture decision; see blocker a)
- [x] Part B: golden-transcript fixtures + replay+diff in verify — done for the 2 DETERMINISTIC reference stories (01, 02). Stories 03 (shuffle) & 04 (RANDOM) are correctly EXCLUDED (bink has no RNG seed; capture refuses them). Reachability still covered by ink:play.
- [x] Part C: lessons 01/02/04 + reference stories audited for self-loop read counts — ZERO found (all hub-and-spoke or VAR-based). No fixes needed.
- [x] Part D: re-enterable-location choices audited for stickiness — ZERO stranding cases (all sticky-fallback or trailing gather). No fixes needed.
- [x] Meta-lesson added to ink authoring steering/guidance (`.kiro/steering/ink-authoring.md`)
- [x] Bonus: Q15 glossary-coverage check added to check-lesson.py (deferred from #223) — passes on all 4 ink lessons


## Findings-adjusted plan (2026-08-27, 4 subagents: 2 research + 2 review)

Raw findings: `.scratch/research/{ink-testing-prior-art,golden-transcript-best-practices}.md`, `.scratch/review/{ink-tooling-review,ink-lesson-bug-audit}.md`.

### Finding 1 — Parts C & D: ZERO live bugs (premise revised)
Scope-aware audit (knot-scope analysis, not grep) of all 4 reference stories + all 4 lesson HTML files found **no** self-loop read counts, **no** stranding once-only choices, **no** dangling diverts. All candidates are hub-and-spoke (read counts advance on fresh entry), VAR-based counters, or sticky-fallback patterns. Lesson 03 already documents the class-A anti-pattern in a "Gotcha" callout.
→ **Parts C/D collapse from "sweep and fix" to "verified clean + add a regression guard."** No fixes needed.
→ Optional polish (not a bug): 0002 "Stitches" teaching fragment (~line 148) drops the `+->` fallback the full reference story uses; correct via trailing gather but breaks teaching parity.

### Finding 2 — Prior art (confirms approach)
Record-replay-diff = **ink-proof** (chromy/ink-proof) model; lineage ChoiceScript Randomtest → Ink-Tester (wildwinter). No first-party ink unit-test framework — teams hand-roll on the runtime API. Two problems: output-correctness → golden transcripts (Part B); coverage/reachability → random-play fuzzing (play-ink.py already does this).
→ **#1 failure mode: blind re-recording (`-u`) launders bugs into the golden.** First commit of each fixture MUST be human-reviewed. Agents may classify a diff but MUST NOT auto-approve an update.

### Finding 3 — Architecture + blockers
- **Part A → NEW tool `tools/check-lesson-code.py`**, not check-lesson.py (deliberately dependency-free — no subprocess/compiler). Reuse `check_g3_code_files` extraction regex (already excludes `data-mode="fragment"`).
- **Part B → extend `play-ink.py`** with `play_capture(json, choice_seq)`; fixtures at `ink-test-project/stories/transcripts/`.
- **Refactor first:** compile logic duplicated in validate-ink.py + play-ink.py; extract shared `ink_compile` helper before Part A adds a 3rd copy.
- **Blocker (a):** verify runs from repo root; lesson HTML is gitignored (`examples/*/lessons/`). Part A can't see lessons in CI without a `git add -f`'d fixture. **Part B is fine** — reference stories committed.
- **Blocker (b):** inklecate is external, not in `mise run setup`. Both A/B need it → verify needs a graceful skip-if-absent guard.
- **Hard bits:** Part A diff-fragment reconstruction (strip `-` lines, unwrap color spans, unescape); Part B shuffle/RANDOM non-determinism (seed bink RNG or exclude shuffle lines from diff — verify what bink exposes).

### Revised execution order (this session)
1. **Part B** golden-transcript harness (core value, no blockers): extract `ink_compile` helper → `play_capture` in play-ink.py → verify bink text-capture API → capture reviewed `.transcript` fixtures (4 stories) → replay+diff mode → wire into verify with skip-guard.
2. **Q15 glossary-coverage** in check-lesson.py (self-contained, builds on `check_q12_glossary`).
3. **Part A** fragment-compile (new tool + diff reconstruction) — gated on blocker (a) decision.
4. **Meta-lesson** into ink authoring steering — framed as *documenting the standard already followed*, not fixing violations.

### Decisions still open
- Part A lesson fixture (blocker a): commit an ink lesson HTML as CI fixture, or scope Part A to reference stories only?

## Resolution (2026-08-27)

Landed: Part B (golden transcripts for the 2 deterministic stories), Parts C/D
(audited — zero live bugs, no fixes needed), Q15 glossary-coverage check, and the
ink-authoring meta-lesson steering. All verified (validate/play/transcripts PASS,
Q15 passes on all 4 ink lessons, capture correctly refuses nondeterministic
stories 03/04, tampered-fixture negative test fires the diff).

Key finding that reshaped the ticket: **two of four reference stories are
nondeterministic** (03 shuffle, 04 RANDOM) and bink has no RNG seed API, so they
cannot have golden transcripts. Handled by `detect_nondeterminism()` refusing
capture rather than a fragile tolerance filter.

Spun out to follow-up tickets:
- **#231** — Part A (fragment-compile) — deferred; needs the committed-lesson-fixture decision.
- **#232** — flaky `verify-interactive.py` no_js_errors 404 (pre-existing, not #228).
- **#233** — reconcile pre-existing uncommitted working-tree changes.

Files: `tools/lib/ink_compile.py` (new), `tools/{validate-ink,play-ink,check-lesson}.py`,
`mise.toml` (verify + `ink:transcripts` task), `.kiro/steering/ink-authoring.md` (new),
`ink-test-project/stories/transcripts/{01,02}*.transcript`.
