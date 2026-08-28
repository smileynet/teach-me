---
id: "246"
title: "Lesson: Ramp Band Textures — 1D Lighting Ramps for toon_ramp.gdshader"
status: backlog
blocked_by: []
priority: medium
tags: ["mktoon", "blender"]
---

# Lesson: Ramp Band Textures — 1D Lighting Ramps for toon_ramp.gdshader

## Why this is its own topic (not part of #220)

The #220 code audit found the ramp does NOT belong with noise/threshold: it's a
DIFFERENT mechanism in a DIFFERENT shader. `mk_toon_lite.gdshader` has NO
`diffuse_ramp` slot — it colors bands via gooch. The ramp lives in
`toon_ramp.gdshader`, which REPLACES the floor-divide banding entirely with a 1D
texture lookup: `texture(diffuse_ramp, vec2(NdotL*0.5+0.5, 0.0)).r` as a scalar
light multiplier. So a ramp is an *alternative banding technique*, a sibling of
lesson 0004 (toon-banding), NOT a control map plugged into mk_toon_lite.

The MAP is a graph: this topic hangs off `toon-banding` (its real conceptual
prereq), not linearly after `toon-control-maps`. #220 is rescoped to the two maps
mk_toon_lite actually samples (noise + threshold).

## What to build

A lesson teaching how to author 1D ramp textures that drive `toon_ramp.gdshader`'s
texture-lookup banding, and when to choose a ramp over floor-divide banding.

### Lesson arc
1. The mechanism: `toon_ramp.gdshader` remaps NdotL to [0,1] and samples a 1D ramp
   as the lighting curve — the texture IS the light response (quote the real
   verbatim `light()` code).
2. Ramp vs floor-divide: a ramp gives per-step color + width control a uniform
   band count can't; floor-divide is cheaper and needs no asset. When to use each.
3. Design 3 ramp variants: hard-cel (constant steps), soft-gradient (blended),
   warm-cool (Gooch-like hue shift across the ramp).
4. Authoring: build the ramp as an 8×1 or 16×1 Non-Color strip (reuse the
   palette-snap 0017 Color-Ramp/strip technique — cross-link, don't duplicate).
5. Gotchas from research: multi-light ramp sampling stacks bands (accumulate then
   ramp once); normal maps perturb NdotL and blur strict seams; `hint_default_white`.

### Code deliverables
- 3 ramp textures (8×1 or 16×1 Non-Color): hard-cel, soft-gradient, warm-cool
- A diffable bpy bake/generate script (mirrors #218/#219 script-not-.blend pattern)
- README

### Exercise
"toon_ramp samples the ramp at vec2(NdotL*0.5+0.5, 0.0). A colleague authors a ramp
with a hard black→white step exactly at U=0.5 and is surprised the shadow terminator
lands at NdotL=0 (surface perpendicular to light), not at grazing angles. Explain the
NdotL→U remap and where they'd move the step to shade only steep-facing surfaces."

## Acceptance criteria
- [ ] Lesson file: `examples/godot-gamedev/lessons/blender-texture-prep/NN-ramp-band-textures.html` (number by build order)
- [ ] Teaches toon_ramp.gdshader's ACTUAL sampling (verbatim), remap explained
- [ ] Ramp vs floor-divide banding: when-to-use decision guidance
- [ ] 3 ramp variants created and shown driving toon_ramp on the barrel (Godot A/B)
- [ ] Reference files: 3 ramp textures + bake script + README in reference/code/ramp-band-textures/
- [ ] Tier-1 property oracle (ramp dims + monotonicity/step-count) wired into verify
- [ ] SR questions (3-5 cards)

## Prereqs / graph placement
- Conceptual prereq: `toon-banding` (0004) — ramp is an alternative to floor-divide banding
- Related: `palette-snap` (0017) shares the 1D-strip authoring technique (cross-link)
- MAP: add as a topic with prereqs [toon-banding]; it is a SIBLING of toon-control-maps,
  not downstream of it (the map is a graph, not a line)

## Research context (from #220 dispatch — see .scratch/subagent-raw/220-research-control-maps.md)
- Ramp/LUT canonical: Unity Toon Lighting Ramp; U = NdotL or half-Lambert NdotL*0.5+0.5
- Gotchas: multi-light band stacking; normal-map NdotL perturbation blurs seams
- toon_ramp.gdshader verbatim sample (from #220 code review): reads `.r`, hint_default_white,
  used as `DIFFUSE_LIGHT = max(DIFFUSE_LIGHT, ALBEDO*LIGHT_COLOR*ATTENUATION*lit)`
