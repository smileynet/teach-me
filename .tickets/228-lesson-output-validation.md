---
id: "228"
title: "Automated fragment-compile + output-correctness validation for lessons"
status: open
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

- [ ] Part A: fragment-compile check runs on all lessons, integrated into verify
- [ ] Part B: golden-transcript fixtures for all reference stories, replay+diff in verify
- [ ] Part C: lessons 01/02/04 audited for self-loop read counts, fixes applied
- [ ] Part D: re-enterable-location choices audited for stickiness
- [ ] Meta-lesson added to ink authoring steering/guidance
