---
id: "303"
title: "godot-validation skill: diagnose asset before re-capturing on wrong-looking output"
status: done
blocked_by: []
priority: low
tags: [skill, mktoon]
---

# godot-validation skill: diagnose asset before re-capturing on wrong-looking output

## Problem

Surfaced during #222 (2026-09-04). When the first capture looked wrong (dark/muddy barrel), the
reflex was to re-run the bake+capture with tweaked palette values — TWICE — before stepping back
to measure the input asset (hue/luminance) and find the real root cause. That's the "tweak and
retry" failure loop the global rules warn against, applied to visual validation specifically.

## What to build

Add a short rule to `.kiro/skills/godot-validation/SKILL.md` (near the "independent read is the
gate" / capture-loop guidance): after ONE capture whose output looks wrong, DIAGNOSE THE ASSET
before re-capturing — measure the input's hue/luminance (e.g. mean RGB, dominant hue, luminance
histogram) and check the shader params, rather than re-running the pipeline hoping for different
pixels. A wrong-looking render is usually an input/asset defect, not a capture flake.

## Acceptance criteria

- [x] `godot-validation` SKILL.md carries a "diagnose the asset before re-capturing" rule
      (1 failed wrong-looking capture → measure input, don't blind-retry)
- [x] References the concrete #222 case (muddy albedo = hue drift, caught by measuring mean RGB)

## Resolution (2026-09-05)

Added rule #6 to the "MCP Reliability" list in `.kiro/skills/godot-validation/SKILL.md` (right
after the reliable-capture-loop): after ONE wrong-looking capture, measure the input asset's mean
RGB / dominant hue / luminance histogram (or run `albedo-sanity-oracle.py`) before re-capturing —
a wrong render is usually an upstream asset defect, not a capture flake. Cites the #222 incident
(two wasted re-bakes before measuring revealed the red→violet hue drift + luminance crush) and
points at the #302 oracle that now automates the diagnosis.

## Context

- Cheap, one-paragraph skill edit. Complements #302 (the oracle that makes the diagnosis
  automatic) — this is the human/agent-process half.
- Two wasted re-bake iterations on #222 are the motivating incident.
