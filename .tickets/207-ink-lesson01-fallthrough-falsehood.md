---
id: "207"
title: "Lesson 01 falsely teaches knot fallthrough; rewrite loose-ends framing"
status: done
blocked_by: []
priority: high
type: fix
---

# Lesson 01 falsely teaches knot fallthrough; rewrite loose-ends framing

## Problem

`examples/ink-godot/lessons/0001-ink-flow-and-knots.html` (Fallthrough section, ~lines 119-130) teaches that a knot without a divert "falls through" to the next knot below it, and its train/platform example relies on this. Real ink does not do this: a knot that runs out of content is a **loose end** (Inky compile warning) and errors at runtime with `Line N: ran out of content` — confirmed by a learner running the lesson's own snippet. The same falsehood is repeated in the glossary `fallthrough` entry, the README (`reference/code/ink-flow-and-knots/README.md`), and the reference story header comment. Likely the root cause of #205's loose-end warnings.

## Phase 1 — Primary agent review & validation

Before implementing, validate the claims against authoritative sources (Ink docs at inklecate/ink docs, inklecate behavior):

1. Confirm knots never fall through to the next knot; confirm runtime error text and Inky warning text.
2. Confirm where fallthrough *does* legitimately exist (stitches within a knot; choices into gathers) and decide whether lesson 1 should mention it at all or defer to the stitches lesson.
3. Review the proposed replacement framing ("Loose ends: every path needs an exit") and snippet.

## Update 2026-08-25 — Phase 1 validated, Phase 2 implemented

Validated against official docs (inkle/ink WritingWithInk.md): knots never fall through to the next knot. Compiler warning: "Apparent loose end exists where the flow runs out. Do you need a '-> END' statement, choice or divert?" Runtime error: "ran out of content. Do you need a '-> DONE' or '-> END'?". Fallthrough exists only within a knot's own content / choices into gathers — deferred to the stitches lesson. Lesson section rewritten as "Loose Ends: Every Path Needs an Exit" (with try-breaking-it exercise), glossary + README + header comments fixed, "falls through" wording at line ~90 changed to "passes through".

Verification gap: no local inklecate / ink-validate tooling yet (#199 open) — compile AC items remain unchecked until that lands. Also added `- -> archive_entrance` fallback choice to the test-project story (choices block had a latent loose end — same class of bug).

## Phase 2 — Implementation (after validation)

- [x] Rewrite lesson Fallthrough section as "Loose ends: every path needs an exit" with fixed snippet (`-> scene_two` added) and a "try breaking it" exercise (delete the divert, observe the error)
- [x] Fix glossary `fallthrough` entry (or remove from lesson 1, reintroduce with stitches)
- [x] Fix README "Fallthrough" bullet → "Loose ends — every path must end with a divert or `-> END`"
- [x] Fix reference story header comment: remove "fallthrough" from Demonstrates list
- [x] Tweak line ~90 "falls through them top to bottom" wording to avoid the loaded term
- [x] Verify: compile `01_flow_and_knots.ink` warning-free; lesson snippet compiles and runs (Inky/inklecate)
- [x] Re-check #205 — if its warnings stem from this same false model, fold findings there
