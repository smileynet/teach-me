---
id: "216"
title: "Blender texture prep pipeline — rebake PBR textures to toon-friendly style for mktoon shader"
type: feature
status: open
priority: high
blocked_by: []
parent: "186"
tags: [mktoon, blender]
---

# Blender texture prep pipeline — rebake PBR textures to toon-friendly style for mktoon shader

## Problem

Our test-scene assets use photorealistic PBR textures (Poly Haven CC0). The mktoon shader track teaches authored toon shading — but **no texture assets are actually connected to any shader in any scene**. All toon-specific texture slots (noise_map, hatching_dark_map, threshold_map, diffuse_ramp) are empty. The `mktoon_test.tscn` uses flat color only (`use_albedo_texture = false`).

More fundamentally: photorealistic textures fight the toon look. PBR albedo textures have continuous gradients, high-frequency noise, and micro-detail that overwhelms the discrete banding regions the shader creates.

### Research findings (2026-08-26)

**Key insight from industry research:** AAA toon games (Guilty Gear, Genshin Impact) do NOT convert PBR textures — they use purpose-built hand-painted textures from scratch with custom channel-packed control maps (ILM maps). However, for indie/learning workflows with existing PBR assets, the research identifies four viable strategies:

| Strategy | Quality | Effort | Dynamic lighting? |
|----------|---------|--------|-------------------|
| A. Keep PBR albedo, toon lighting in shader | Good | Low | ✅ Yes |
| B. Posterize + palette snap albedo in Blender | Better | Medium | ✅ Yes (bake color only) |
| C. Hand-paint toon control maps (ILM/shadow) | Best | High | ✅ Yes |
| D. Bake entire toon look (Combined pass) | Fixed look | Medium | ❌ No (baked lighting) |

**Our approach: Strategy A+B hybrid.** Keep dynamic lighting (the shader handles banding), but prep textures in Blender to reduce noise and snap colors to a limited palette. Additionally, author the toon-specific control maps that `mk_toon_lite.gdshader` already declares uniforms for but nobody populates.

### What the shader already expects (from review)

`mk_toon_lite.gdshader` declares these texture uniforms that are currently EMPTY:
- `noise_map` — breaks up band edges (tileable)
- `hatching_dark_map` — cross-hatching overlay in shadows (tileable)
- `sketch_map` — pencil texture overlay (tileable)
- `drawn_map` — hand-drawn texture overlay
- `threshold_map` — per-pixel shading boundary shift
- `normal_map` — surface normals (Poly Haven `_nor_gl_` maps exist but aren't wired)
- `diffuse_ramp` — 1D gradient for banding (no ramp textures exist at all)

## What to build

A two-part pipeline:

### Part 1: Albedo simplification (Blender)

Take PBR albedo textures and reduce their complexity:
1. **Posterize** — `floor(color * N) / N` in shader nodes (N = band count matching toon shader)
2. **Palette snap** — Color Ramp with Constant interpolation, or 1D palette texture lookup
3. **Bake Emit pass** — captures simplified color without lighting influence
4. **Export** — simplified albedo replaces the original in Godot

### Part 2: Toon control map authoring (Blender + Godot)

Create the missing toon-specific textures:
1. **Ramp texture** — 1D gradient texture (5-8px wide) defining band colors
2. **Noise map** — tileable organic noise for band edge variation
3. **Threshold map** — derive from PBR AO channel (shadow bias per-pixel)
4. **Smooth normals** — bake from mesh for outline extrusion (already documented in toon-outlines)

### Target assets

Start with existing test-scene Poly Haven assets:
- Barrel_01 (organic shape, wood grain — tests posterization on natural surfaces)
- Camera_01 (hard surface, multi-material — tests zone-based simplification)
- Lantern_01 (metal + emissive — tests material separation)

### Deliverables

- MAP.md for `blender-texture-prep` domain
- Blender node group: "Toon Prep" (posterize + palette snap, reusable)
- Simplified albedo textures for all 3 Poly Haven assets
- Ramp textures (1D) for configurable_banding and mk_toon_lite
- Noise map (tileable, organic)
- Threshold map derived from Barrel_01's AO channel
- Updated `mktoon_test.tscn` with all texture slots populated
- Before/after screenshots under mk_toon_lite shader

## Acceptance criteria
This is the EPIC/tracking ticket for the blender-texture-prep track. Concrete lesson deliverables (node groups, ramp/noise/threshold textures) are owned by the child lesson tickets #217-222 — do NOT rebuild them here. This ticket owns the shared track infrastructure (MAP, test-scene wiring) and tracks overall completion.

- [x] MAP.md created for `blender-texture-prep` domain under godot-gamedev
- [x] `mktoon_test.tscn` wired: albedo texture ON, normal map connected (shared fixture for all lessons)
- [x] Before/after + progressive-isolation screenshots captured (shared lesson assets)
- [x] Validated raking light angle for visible toon bands (shared fixture)
- [ ] #217 texture-audit lesson complete
- [ ] #218 albedo-posterize lesson complete (owns "Toon Prep" node group)
- [ ] #219 palette-snap lesson complete
- [ ] #220 toon-control-maps lesson complete (owns ramp/noise/threshold textures)
- [ ] #221 bake-and-export lesson complete (owns glTF round-trip)
- [ ] #222 wiring-the-shader lesson complete (owns final mktoon_test population)
- [ ] Track validated end-to-end: a PBR asset flows through the full pipeline to a toon-prepped Godot render

## Context

- **Parent track:** godot-mktoon (ticket #186)
- **Branches from:** toon-banding (lesson 0004) + configurable-banding (0009)
- **Related expansion opp:** `blender-smooth-normals-pipeline` in godot-toon-shaders MAP
- **Test-scene location:** `D:\code\teach-me\test-scene\`
- **Existing PBR assets:** `test-scene/assets/polyhaven/` (Barrel_01, Camera_01, Lantern_01)
- **Existing shaders:** `test-scene/shaders/reference/mk_toon_lite.gdshader` (full reference, ~270 lines)
- **Critical gap:** ALL toon texture uniforms are declared but NONE are populated in any scene
- **Blender bake constraint:** EEVEE cannot bake — must use Cycles with Emit pass for color-only

## Implementation notes (from shader + scene analysis, 2026-08-26)

### Wiring textures into mktoon_test.tscn (prerequisite spike)

The scene needs these edits to show "before" state (raw PBR under toon shader):
1. Add ext_resources for `Barrel_01_explosive_diff_1k.jpg` (uid://bifq8ujd57bgd) and `_nor_gl_1k.jpg` (uid://hdeqeffdyg2n)
2. Set `shader_parameter/use_albedo_texture = true` + assign texture
3. Set `shader_parameter/use_normal_map = true` + assign normal map
4. Wire outline shader as `next_pass` SubResource (currently loaded but dangling)
5. Update `load_steps` from 5 to 8

### Critical color space requirement

`albedo_texture` uniform has `source_color` hint — Godot auto-converts sRGB→linear on sample. Without this, colors appear washed out in Forward+ renderer. The `normal_map` uniform does NOT have `hint_normal` — may need adding for correct RGTC compression and blue channel reconstruction.

### Shader safety model

All 9 texture samplers are guarded by `use_*` booleans (all default `false`). Textures are NEVER sampled unless explicitly toggled on. This means:
- Safe to assign textures without visual change until toggle is flipped
- Pattern-overlay maps (hatching/sketch/drawn) are multiplicative → white (1.0) = identity
- Threshold/noise maps are centered at 0.5 → white (1.0) creates non-neutral +0.5 bias if toggled on without proper texture

### Known problems to document (from research)

| Artifact | Cause | Solution in our pipeline |
|----------|-------|--------------------------|
| Shadow speckle/chattering | Normal map micro-detail crosses threshold per-pixel | Flatten normals (lesson 0015 will show this) |
| Visual noise / "busy" look | High-frequency albedo detail overwhelms flat bands | Posterize + palette snap (lessons 0016-0017) |
| Band edge instability | Mesh topology creates lumpy shadow boundaries | Noise map bias softens edges (lesson 0018 control maps) |
| AO creating dirty flat regions | AO noise quantized alongside lighting | Use AO as threshold_map AFTER quantization (lesson 0018) |

## Research references

- `.memory/research/mktoon-texture-prep/toon-texture-pipelines.md` — industry approaches (Guilty Gear ILM maps, Genshin, Malt)
- `.memory/research/mktoon-texture-prep/blender-bake-nodes.md` — specific node setups, bake settings, addon list
- `.memory/research/mktoon-texture-prep/mktoon-texture-requirements.md` — what toon shaders expect vs generate procedurally
- `.memory/research/mktoon-texture-prep/existing-test-scene-review.md` — current state of test-scene assets and shader uniforms
- `.memory/research/mktoon-texture-prep/mk-toon-lite-analysis.md` — full shader uniform/usage analysis
- `.memory/research/mktoon-texture-prep/mktoon-scene-analysis.md` — scene structure, material state, wiring needed
- `.memory/research/mktoon-texture-prep/godot-texture-import.md` — color space hints, import flags, Poly Haven gotchas
- `.memory/research/mktoon-texture-prep/toon-texture-problems.md` — 8 specific PBR+toon artifacts with causes/solutions

## Resolved questions

| Question | Answer | Source |
|----------|--------|--------|
| Rebake entire look or just simplify albedo? | **Simplify albedo only** — shader handles lighting procedurally | MK.Toon texture requirements research |
| Dedicated addon or node group? | **Node group** — addons add dependency; nodes are portable | Blender bake nodes research |
| Normals in vertex colors or texture? | **Texture maps for normals** (standard tangent-space). Vertex colors reserved for outline smooth normals (separate concern). | Existing toon-outlines lesson pattern |
| What about roughness/metallic? | **Discard entirely** — toon shaders use `specular_disabled` render mode; roughness/metallic irrelevant | mk_toon_lite shader review |
| AO channel useful? | **Yes** — extract from ARM texture R channel → use as threshold_map seed | Test-scene review (ARM = R:AO, G:Roughness, B:Metallic) |
