---
id: "217"
title: "Lesson: What Makes a Texture Toon-Unfriendly? (0015)"
type: feature
status: open
priority: high
blocked_by: []
parent: "216"
tags: [mktoon, blender]
---

# Lesson: What Makes a Texture Toon-Unfriendly? (0015)

## What to build

A lightweight orientation lesson that teaches learners to analyze PBR texture sets and identify what will fight toon shading — before they start fixing anything.

### Lesson arc

1. Show the Barrel_01 PBR textures under mk_toon_lite with default settings → "what looks wrong?"
2. Identify the three enemies: continuous gradients (noisy band edges), high-frequency detail (overwhelms flat regions), micro-detail normals (chattering shadows)
3. Explain which PBR channels matter for toon (albedo + normal) vs which to discard (roughness, metallic)
4. Show the AO channel as a hidden asset (future threshold_map)
5. Reference industry context: Guilty Gear and Genshin don't convert PBR — they author for toon from scratch. Our approach is the indie middle ground.

### Key concept

> PBR textures encode continuous physical properties. Toon shaders discretize lighting into bands. When continuous texture detail meets discrete shading, the texture wins — creating noise where the shader wants flat regions.

### Exercise

Show two textures side by side (one PBR-noisy, one simplified). Ask: "Which texture channels are creating problems under toon banding? What would you keep, discard, or simplify?"

## Acceptance criteria

- [ ] Lesson file: `examples/godot-gamedev/lessons/blender-texture-prep/01-texture-audit.html`
- [ ] Uses Barrel_01 diff + ARM textures as the primary example
- [ ] Diagram: PBR texture channels → which feed toon shader vs which are discarded
- [ ] Before screenshot: Barrel_01 with raw PBR diff under configurable_banding
- [ ] Identifies 3 specific problems (gradients, micro-detail, unnecessary channels)
- [ ] References the `mk_toon_lite.gdshader` uniform list (what slots need filling)
- [ ] SR questions generated (3-5 cards)

## Research context

**From toon-texture-problems research (8 specific artifacts):**

| # | Artifact | Cause | Visual description |
|---|----------|-------|-------------------|
| 1 | Shadow speckle/chattering | Normal map micro-detail pushes pixels across threshold | Salt-and-pepper noise at shadow boundaries |
| 2 | Visual noise / "busy" look | High-frequency albedo detail overwhelms flat bands | "Neither stylized nor realistic — just broken" (McKenney, Velan Studios) |
| 3 | Broken specular | Roughness variation → scattered highlights | "Wet/oily" appearance instead of clean cartoon lobe |
| 4 | TAA flickering | Hard step edges + temporal jitter = oscillation | Buzzing/shimmering on shadow edges per-frame |
| 5 | Dirty flat regions | AO noise quantized into what should be uniform areas | Speckly dark patches in shadow bands |
| 6 | Lumpy shadow edges | Mesh topology → lumpy normal interpolation | Shadow follows edge loops instead of clean shapes |
| 7 | Lumen/GI noise | Inherent GI noise visible in hard-banded output | Visible speckle in band interiors |
| 8 | Rim artifacts | Flat surfaces have poor NdotV variation | Rim light appears/disappears abruptly |

Key quote (Erik McKenney, Velan Studios 2019): "Be they hand-painted textures, high-poly sculpted height maps, or fully-procedural materials, too many small details detract from the stylized look. They create a noise frequency that is too high, and they distract from the key shapes of the model."

Key quote (Hyper3D docs): "Noisy normals shatter clean tone bands into speckle. Micro-detail belongs in realistic assets — for cel work, smooth surfaces and let the silhouette talk."

**From mk_toon_lite shader analysis:**
- All 9 texture samplers guarded by `use_*` booleans (default `false`)
- `render_mode specular_disabled` — roughness/metallic completely irrelevant
- Noise/threshold maps centered at 0.5 (bias operation, not multiplicative)
- Pattern-overlay maps (hatching/sketch/drawn) are multiplicative (1.0 = identity)
- The shader is designed for progressive opt-in: toggle features one at a time

**From mktoon-scene-analysis:**
- `mktoon_test.tscn` uses flat color only (`use_albedo_texture = false`)
- Barrel_01 textures exist and are properly imported (diff, nor_gl, arm)
- ARM texture R channel = AO (extractable as threshold_map)
- Outline shader loaded but not wired (dangling ext_resource)
- Lesson should reference the SPECIFIC UIDs for texture assignment

**From godot-texture-import research:**
- `source_color` hint REQUIRED on albedo in Forward+ (without it: washed out)
- mk_toon_lite already has `source_color` on albedo_texture ✓
- Normal map uniform lacks `hint_normal` — document this as potential issue
- Poly Haven `_nor_gl_` normals are OpenGL-format (Y+) — no inversion needed in Godot
