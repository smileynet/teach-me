---
id: "302"
title: "Add albedo hue/luminance sanity oracle for baked toon textures"
status: done
blocked_by: []
priority: medium
tags: [mktoon, blender, tooling]
---

# Add albedo hue/luminance sanity oracle for baked toon textures

## Problem

Surfaced during #222 (2026-09-04). The palette-snap bake produced a muddy, near-black albedo
(red barrel → violet-gray, mean RGB 93,81,107) that rendered WORSE than raw PBR under the toon
shader. No gate caught it — the posterize/palette-snap/bake-export oracles validate the MATH
(floor-divide levels, luminance→slot, sRGB colorspace) but NOT the aesthetic OUTCOME. It was
caught only by manually reading pixels, late in the ticket.

Two measurable failure modes a sanity oracle can catch deterministically:
1. **Hue drift** — the baked albedo's dominant hue diverges from the source's (red→purple).
2. **Luminance crush** — the bake collapses into one dark slot (the barrel's 94%-in-slot-0 case),
   so the surface reads flat/black instead of cel-shaded.

## What to build

`tools/albedo-sanity-oracle.py` (stdlib + Pillow, matching the existing oracle pattern:
`--json`, exit 0/1/2, sidecar-driven). For each baked toon albedo it asserts, against its source:
- mean/dominant HUE within a tolerance of the source's dominant hue (hue preserved);
- luminance spread NOT collapsed to a single dark slot (e.g. not >X% of pixels in the darkest
  band, and mean luminance above a floor).
Sidecar records source path + expected hue family + thresholds. Wire into `mise run verify` for
the `test-scene/assets/toon-export/` bakes (or their committed reference copies).

## Acceptance criteria

- [x] `albedo-sanity-oracle.py` asserts hue-preserved + luminance-not-crushed vs source
- [x] Discriminates: FAILS on the muddy `Barrel_01_toon_albedo.png` (hue Δ99°, 95% dark, mean-lum 0.093), PASSES on the warm `Barrel_01_toon_albedo_warm.png` (hue Δ16°, 0% dark, mean-lum 0.205)
- [x] Structured JSON output + exit codes (0 pass / 1 fail / 2 error), sidecar-driven
- [x] Wired into `mise run verify`; verify EXIT 0 with the warm albedo as the shipped asset

## Resolution (2026-09-05)

Added `tools/albedo-sanity-oracle.py` (Pillow) — the aesthetic-outcome tier the math oracles
lacked. Measures a baked albedo's dominant hue (circular mean over saturated pixels) + luminance
distribution vs. its source, asserting: hue within `hue_tol_deg` (default 40°) of the source, and
not luminance-crushed (≤85% of pixels in the darkest of 6 slots, mean-lum ≥0.12). Sidecar-driven
(`albedo-sanity-sidecar.json`), wired into `verify`.

**Proven to discriminate** (the #222 before/after): muddy albedo FAILS all three (hue drift
red 5°→violet 267° Δ99°, 95% pixels darkest slot, mean-lum 0.093); warm albedo PASSES (Δ16°, 0%,
0.205). This is the gate that would have caught #222's muddy bake automatically instead of relying
on a manual pixel read. verify EXIT 0.

## Context

- The #222 muddy vs warm albedos are the natural test fixtures (warm reference copy committed at
  `library/godot-gamedev/reference/code/bake-and-export/Barrel_01_toon_albedo_warm.png`; the muddy
  one is regenerable via the pipeline / lives in the gitignored toon-export dir).
- Complements, not replaces, `palette-snap-oracle.py` (math) — this is the aesthetic-outcome tier.
- Root-cause detail: 94% of Barrel_01 diffuse pixels fall in the darkest luminance slot; a
  cool-shadow palette then snaps a warm asset muddy. See #222 Resolution.
