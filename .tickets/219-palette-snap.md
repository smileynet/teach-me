---
id: "219"
title: "Lesson: Palette Snapping — Color Ramp and 1D Lookup (0017)"
type: feature
status: in_progress
priority: high
blocked_by: ["218"]
parent: "216"
tags: [mktoon, blender]
---

# Lesson: Palette Snapping — Color Ramp and 1D Lookup (0017)

## What to build

A substantial lesson teaching palette snapping — mapping every pixel to the nearest color in an artist-chosen palette. This is the art-direction step that gives unified style across assets.

### Lesson arc

1. Problem statement: posterization reduces band COUNT but doesn't control which colors survive. A 4-level barrel might posterize to ugly mid-tones nobody chose.
2. Method A: Color Ramp with Constant interpolation — convert to grayscale, map through a ramp with palette colors at specific positions. Quick, visual, editable.
3. Method B: 1D palette texture lookup — create a tiny (5×1 or 8×1) palette image, sample with Closest interpolation. More scalable for shared palettes across assets.
4. Method C: mention Dynamic Color Palette addon (DCP) — UV-driven palette approach with Godot 4 shader export. Reference only, not the core workflow.
5. Design the palette: show how to pick colors that work with toon banding (warm shadows, cool midtones, saturated highlights — or whatever the art direction calls for)
6. Build combined node group: Posterize → Palette Snap (composable with lesson 0016's group)
7. Bake the result via Emit pass

### Key concept

> Posterization asks "how many colors?" Palette snapping asks "which colors?" Together they transform any PBR albedo into a texture that looks intentionally designed rather than algorithmically crushed.

### Code deliverables

- Blender node group: "Palette Snap" (input: Color; output: Snapped Color; params: palette texture or ramp)
- Example palette: 6-color warm-toon palette suitable for Barrel_01 wood tones
- Combined "Toon Prep" group chaining Posterize → Palette Snap

### Exercise

"You have a 6-color palette. Your toon shader uses 4 bands. Should the palette count match the band count? Why or why not? What happens when they mismatch?"

## Acceptance criteria

- [ ] Lesson file: `examples/godot-gamedev/lessons/blender-texture-prep/03-palette-snap.html`
- [ ] Two methods taught (Color Ramp + 1D texture lookup) with when-to-use guidance
- [ ] Palette design principles explained (not just technique)
- [ ] Node group created: "Palette Snap" (reusable)
- [ ] Combined "Toon Prep" group demonstrated (Posterize + Palette Snap)
- [ ] Before/after: raw albedo → posterized → palette-snapped (3-way comparison)
- [ ] SR questions generated (3-5 cards)

## Research context

**From blender-bake-nodes research:**

Method A — Color Ramp with Constant Interpolation:
- Convert texture to grayscale (RGB to BW node)
- Feed into Color Ramp with interpolation set to Constant
- Place color stops at desired positions using palette colors
- Direct mapping from luminance → palette color

Method B — 1D Palette Texture with Closest Interpolation:
- Create small image (5×1 or 8×1 pixels), each pixel = palette color
- Image Texture node → Closest interpolation (not Linear!)
- Feed posterized grayscale as UV coordinate lookup
- Acts as a color lookup table (CLUT)

Method C — Dynamic Color Palette Add-on (DCP):
- Generates HSV color palette texture + PBR data map
- All faces share one material; color by UV position
- Exports Godot 4 spatial shaders: `dcp_multicol.gdshader`, `dcp_singlecol.gdshader`
- Supports runtime palette blending
- Source: https://extensions.blender.org/add-ons/dynamic-color-palette/

Method D — Nearest-Color Node Group:
- Euclidean distance in RGB space to each palette color
- Complex node tree (impractical >5 colors without OSL scripting)
- Source: BSE #280223

**From toon-texture-pipelines research:**
- "Palette snapping at bake time freezes the result — can't change palette later"
- For runtime palette swaps: keep palette texture separate, do lookup in Godot shader
- DCP addon demonstrates this pattern with Godot export

## Researched decisions (2026-08-28, subagent research + code audit)

**Canonical palette source:** hand-authored fixed art-directed 6-color warm-toon
palette (Barrel_01 wood tones). Extraction-from-image is a one-line "Alternative"
pointer, not the taught path (keeps the lesson single-axis; the point is INTENTIONAL
color choice).

**Verified Blender 5.x API** (de-risks the artifact):
- Method A: `ShaderNodeValToRGB` (Color Ramp), `interpolation='CONSTANT'`, driven by
  `ShaderNodeRGBToBW`. Blender 4.3+ uses unified `ShaderNodeSeparateColor` (not
  Separate RGB/HSV) if hue-keying.
- Method B: `ShaderNodeTexImage`, `interpolation='Closest'` (required), N×1 palette
  strip indexed by `Combine XYZ(X=luminance, Y=0.5, Z=0)`. GOTCHAS to pin in lesson:
  set palette strip Color Space = **Non-Color** (avoid sRGB shifting swatches);
  X-mapping `(index+0.5)/N` vs `index/N` off-by-one — resolve empirically in Tier-3.

**Prior art to reuse (not duplicate):** `reference/code/color-simplification/palette_snap.gdshader`
is the existing GODOT runtime nearest-color shader (Oklab argmin). #219 builds the
BLENDER-node counterpart; reuse the concept + Oklab distance as the oracle's
perceptual-distance reference.

**Exercise answer (grounded):** band count and palette count are INDEPENDENT axes.
Shader sets bands; palette sets which colors bands sample. Palette>bands → extra
swatches never sampled; palette<bands → bands collapse/muddy; equal → cleanest.
Adding palette colors does NOT add bands.

**Palette-design principles to teach:** HSB not RGB; value-first; hue-shift ~15–20°/step
(highlights warmer, shadows cooler); saturation peaks midtone; temperature contrast
creates volume.

**Discrepancies fixed:** MAP `lesson_file` is stale `0017-palette-snap.html` → correct to
`blender-texture-prep/03-palette-snap.html` (matches AC + per-domain NN-slug convention).
Display title "Lesson 17", file `03-` (mirrors how 0016 does it). In-page `data-file`
block is simplified; full artifact on disk is richer — mirror 0016.

**Validation (3-tier, reuse #218 infra):** Tier-1 `tools/palette-snap-oracle.py`
(Blender-free, wired into verify); Tier-2 `blender -b --python palette_snap.py -- --check`;
Tier-3 emit-bake on Barrel_01 → assert output pixels ∈ palette set (also resolves the
X-mapping + Non-Color open items).
