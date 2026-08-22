---
domain: godot-toon-shaders
description: "Implement toon/cel shading in Godot 4 — from spatial shader anatomy through discrete banding techniques to production lighting setups"
generated: 2026-08-19
depth: 1
parent: godot-gamedev
leads_to:
  - advanced-shader-effects
  - stylized-rendering
---

# Godot Toon Shaders

## Orientation

Toon (cel) shading replaces smooth realistic lighting with discrete brightness bands — the signature look of anime, comic-book games, and stylized 3D. In Godot 4, you achieve this entirely in the `light()` function of spatial shaders. This track takes you from understanding what a spatial shader IS through three production-ready banding approaches.

## Topics

### spatial-shader-anatomy
- **title:** Spatial Shader Anatomy
- **why:** Before writing toon lighting you need to understand the three shader entry points, what coordinate space each operates in, and how data flows between them
- **scope:** substantial
- **prereqs:** []
- **lesson_file:** 0003-spatial-shader-anatomy.html
- **status:** complete

### toon-banding
- **title:** Toon Banding
- **why:** The core technique — three approaches to turning continuous lighting into discrete bands, with trade-offs that determine your art direction options
- **scope:** substantial
- **prereqs:** [spatial-shader-anatomy]
- **lesson_file:** 0004-toon-banding.html
- **status:** complete

### triplanar-mapping
- **title:** Triplanar Mapping
- **why:** World-space texturing eliminates UV seams and stretching on surfaces like roads, walls, and terrain — essential for any scene with procedural or non-UV'd geometry
- **scope:** substantial
- **prereqs:** [spatial-shader-anatomy]
- **lesson_file:** 0005-triplanar-mapping.html
- **status:** complete

### toon-outlines
- **title:** Toon Outlines
- **why:** Outlines complete the cel-shading look — two families (inverted hull for per-object control, screen-space depth+normal for production quality) with different trade-offs that shipped games combine
- **scope:** substantial
- **prereqs:** [toon-banding]
- **lesson_file:** 0006-toon-outlines.html
- **status:** generated


## Expansion Opportunities

Subtopics surfaced during lesson development that could become full topics:

- **gradient-textures** — GradientTexture1D/2D, CurveTexture, procedural lookup tables, artistic gradient design (surfaced in: toon-banding)
- **shader-globals** — project-wide uniforms, when to use globals vs per-material params, performance implications, scene mood control (surfaced in: toon-banding)
- **multi-light-strategies** — additive vs max accumulation, light groups, per-light masks, toon-friendly light rigs (surfaced in: toon-banding exercise)
- **shadow-color-theory** — warm/cool temperature in stylized rendering, color scripts, ambient vs direct color relationships (surfaced in: toon-banding bonus)
