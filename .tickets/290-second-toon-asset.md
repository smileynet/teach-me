---
id: "290"
title: "Demo blender-texture-prep pipeline on a second asset (Camera_01 or Lantern_01)"
status: open
blocked_by: []
priority: low
parent: "216"
tags: [mktoon, blender]
---

# Demo blender-texture-prep pipeline on a second asset (Camera_01 or Lantern_01)

## Why

Descoped from #222 (lesson 06). That lesson proved the full toon-prep pipeline end-to-end on
Barrel_01 (raw PBR → posterize → palette-snap → Emit bake → wire into mk_toon_lite), including
the palette-hue pitfall and its fix. Its "minimum 2 assets" AC was deliberately deferred to
avoid ballooning the ticket: a second asset needs its own Blender bake + windowed capture cycle.

Camera_01 and Lantern_01 are multi-material (harder than the single-material barrel) — good
for showing the pipeline generalizes, and for surfacing per-material palette choices.

## What to build

Run the same pipeline on Camera_01 (hard-surface, multi-material) OR Lantern_01 (metal +
emissive) and add a short "generalizes to other assets" section or figure to lesson 06 (or a
sibling note). Confirm the hue-preserving-palette lesson holds — pick a palette matched to the
asset's hue family, verify the toon render is clean (not muddy) via windowed capture + an
independent image read.

## Acceptance criteria

- [ ] Second asset run through posterize → palette-snap → Emit bake with a hue-matched palette
- [ ] Windowed Godot render + independent image read confirms a clean cel look (not muddy)
- [ ] Lesson 06 (or sibling) updated with the second-asset result
- [ ] `mise run verify` EXIT 0

## Context

- Assets: `test-scene/assets/polyhaven/Camera_01/`, `test-scene/assets/polyhaven/Lantern_01/`
- Pipeline: `.scratch/bake_warm_albedo.py` (from #222) is a starting template — parametrize the palette per asset
- Gotcha (from #222): luminance-only palette snap discards hue; match the palette to the asset's dominant hue AND luminance distribution, or the surface collapses dark/muddy
