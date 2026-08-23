---
domain: godot-mktoon
description: "Build a production toon shader layer by layer — per-material authored NPR inspired by Esoteric Ebb's MK.Toon"
generated: 2026-08-23
depth: 1
parent: godot-gamedev
leads_to:
  - stylized-rendering
  - advanced-shader-effects
---

# Per-Material Toon Shading (MKToon)

## Orientation

Where the toon-shaders track simplifies lighting with post-process filters (outlines, Kuwahara), this track builds the look from scratch inside the material. Each surface gets its own shadow colors, band count, and artistic overlays — authored per-material, not filtered globally. The reference is a real shipped game (Esoteric Ebb, 838 materials using MK.Toon in Unity, ported to Godot).

This is the "authored shading" fork from `toon-banding`. You need to understand floor-based quantization (lesson 0004) before starting here.

## Topics

### configurable-banding
- **title:** Configurable Toon Banding
- **why:** The simple floor() from lesson 0004 is fixed — a production shader needs artist-facing controls for band count, smoothness blend, and intensity scale without changing code
- **scope:** substantial
- **prereqs:** [toon-banding]
- **lesson_file:** 0009-configurable-banding.html
- **status:** not-started

### gooch-shading
- **title:** Gooch Warm/Cool Shadows
- **why:** Black shadows look amateur — Gooch shading replaces them with a cool-to-warm color ramp that adds perceived depth without breaking the stylized look
- **scope:** substantial
- **prereqs:** [configurable-banding]
- **lesson_file:** 0010-gooch-shading.html
- **status:** not-started

### wrapped-lighting-noise
- **title:** Wrapped Lighting & Noise Bias
- **why:** Hard geometric terminators look CG — half-Lambert wrap softens the shadow boundary while noise texture bias adds organic irregularity that reads as hand-painted
- **scope:** substantial
- **prereqs:** [gooch-shading]
- **lesson_file:** 0011-wrapped-lighting-noise.html
- **status:** not-started

### specular-rim
- **title:** Specular & Rim Lighting (Threshold-Smoothstep)
- **why:** One reusable pattern — threshold + smoothstep — gives you both flat specular stamps (anime eye-catch lights) and Fresnel-based rim glow, adding dimension without breaking flat-color regions
- **scope:** substantial
- **prereqs:** [wrapped-lighting-noise]
- **lesson_file:** 0012-specular-rim.html
- **status:** not-started

### outlines-overlays
- **title:** Inverted-Hull Outlines & Artistic Overlays
- **why:** A companion outline shader (second material pass) completes the cel look, while hatch/sketch textures weighted by shadow add hand-drawn authenticity
- **scope:** substantial
- **prereqs:** [specular-rim]
- **lesson_file:** 0013-outlines-overlays.html
- **status:** not-started

### vfx-dissolve-vertex
- **title:** VFX Layer — Dissolve & Vertex Animation
- **why:** Map-based dissolve with glowing borders and vertex displacement (sine, bounce, noise with stutter) are the runtime effects that bring toon-shaded characters to life in cutscenes and gameplay
- **scope:** substantial
- **prereqs:** [outlines-overlays]
- **lesson_file:** 0014-vfx-dissolve-vertex.html
- **status:** not-started

## Expansion Opportunities

Subtopics that could become full topics if the track grows:

- **color-grading-per-material** — brightness, saturation, contrast, hue rotation applied in fragment() before lighting (surfaced in: MKToon analysis)
- **iridescence** — Fresnel-based additive color shift for magical/fantasy materials (surfaced in: MKToon analysis, structurally identical to rim)
- **threshold-maps** — per-pixel bias textures for painterly shadow boundaries (surfaced in: MKToon portability spec)
- **screen-space-vs-object-space-outlines** — trade-offs between the inverted-hull taught here and the screen-space approach from the sibling track (surfaced in: portability gap analysis)
