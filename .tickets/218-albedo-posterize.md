---
id: "218"
title: "Lesson: Albedo Posterization in Blender Nodes (0016)"
type: feature
status: open
priority: high
blocked_by: ["217"]
parent: "216"
tags: [mktoon, blender]
---

# Lesson: Albedo Posterization in Blender Nodes (0016)

## What to build

A substantial lesson teaching floor-divide quantization in Blender's shader node editor — the same math that discretizes lighting in the toon shader, applied to texture colors.

### Lesson arc

1. Connect to prior knowledge: `floor(NdotL * N) / N` in the shader quantizes lighting → same math on albedo quantizes color
2. Build the posterize node chain step by step: Image Texture → Scale(N) → Floor → Scale(1/N)
3. Show the visual result on Barrel_01 albedo at N=4, N=8, N=16 — too few = loss of form, too many = still noisy
4. Introduce the +0.5/N offset trick to center bands (avoids dark-biased quantization)
5. Compare Method A (Vector Math Floor) vs Method B (Separate RGB + Greater Than) — when each is appropriate
6. Build a reusable node group ("Posterize RGB") with exposed N parameter
7. Connect to next lesson: posterization reduces count but doesn't control WHICH colors survive → palette snapping

### Key concept

> Posterization and toon banding are the same operation applied at different stages: one quantizes lighting in the shader, the other quantizes texture color in the prep stage. Matching their band counts produces visual harmony.

### Code deliverables

- Blender node group: "Posterize RGB" (input: Color, N; output: Posterized Color)
- Screenshot comparison: N=4, N=8, N=16 on Barrel_01 diff texture

### Exercise

"Your toon shader uses 4 bands. You posterize the albedo to 4 levels. The result looks flat and lifeless. Why? What N value would preserve enough texture detail while still harmonizing with 4-band shading?"

## Acceptance criteria

- [ ] Lesson file: `examples/godot-gamedev/lessons/blender-texture-prep/02-albedo-posterize.html`
- [ ] Node chain built step-by-step with code blocks showing Blender node connections
- [ ] Visual comparison at 3 band counts (screenshot or diagram)
- [ ] Node group created and documented (reusable)
- [ ] Explains offset trick (+0.5/N) with visual difference
- [ ] Connects floor-divide math to the same operation in configurable_banding.gdshader
- [ ] SR questions generated (3-5 cards)
- [ ] Reference code file: node group .blend or documented node setup

## Research context

**From blender-bake-nodes research:**

Method A — Math Floor (most common):
```
Image Texture → Vector Math: Scale(N) → Vector Math: Floor → Vector Math: Scale(1/N) → Base Color
```
- Colors range 0–N after multiply, floor cuts decimals, divide remaps to 0–1
- Source: BSE #304301

Method B — Separate RGB + Greater Than:
- For hard-edge posterization with manual per-channel threshold control
- Separate RGB → each channel through Math "Greater Than" → Combine RGB
- Source: BSE #101750

**From toon-texture-pipelines research:**
- Strategy D (Posterization): `color = floor(albedo * levels + 0.5) / levels`
- "Apply BEFORE lighting for color palette reduction; apply AFTER lighting for cel-shading bands"
- Quick stylization, good for prototyping; combine with stepped lighting for full cel look

**Key Blender constraint:**
- Shader nodes work in EEVEE viewport preview but baking requires Cycles
- For baking posterized result: use Emit pass (captures color without lighting influence)
- Set bake Samples to 1-16 (flat shading needs minimal samples)
