---
id: "220"
title: "Lesson: Authoring Toon Control Maps — Ramp, Noise, Threshold (0018)"
type: feature
status: open
priority: high
blocked_by: ["217"]
parent: "216"
tags: [mktoon, blender]
---

# Lesson: Authoring Toon Control Maps — Ramp, Noise, Threshold (0018)

## What to build

A substantial lesson teaching how to create the toon-specific control textures that `mk_toon_lite.gdshader` expects but nobody provides. These maps don't replace albedo — they tell the shader HOW to shade.

### Lesson arc

1. Introduce the concept: control maps are artist instructions to the shader. They're small (ramp: 8×1, noise: 256×256 tileable, threshold: same res as albedo) and reusable across assets.
2. **Ramp texture** — create a 1D gradient (8×1 or 16×1 pixels) that defines the band-to-color mapping. Show how the shader samples it: `texture(diffuse_ramp, vec2(NdotL, 0.5))`. Design 3 ramp variants: hard-cel, soft-gradient, warm-to-cool (Gooch-like).
3. **Noise map** — create a tileable organic noise texture (Blender's noise texture node → bake). Show how the shader uses it: adds to NdotL before quantization, creating organic edge variation. Compare different noise frequencies.
4. **Threshold map** — extract from existing AO channel (ARM texture R channel from Poly Haven). Show how the shader uses it: per-pixel bias on the shadow boundary. Darker AO = earlier shadow. This gives "free" spatial shadow variation without hand-painting.
5. Demonstrate each map's visual effect independently (before/after toggling each slot)

### Key concept

> Control maps are small, cheap textures that give artists per-pixel authority over shader behavior. They don't define color — they define WHERE and HOW the shader applies its effects. One noise map + one ramp can transform a generic toon shader into a distinctive style.

### Code deliverables

- 3 ramp textures (8×1): hard-cel, soft-gradient, warm-cool
- 1 tileable noise map (256×256) baked from Blender procedural noise
- 1 threshold map derived from Barrel_01 ARM texture R channel
- Blender file showing the bake setup for each

### Exercise

"The mk_toon_lite shader has a `noise_intensity` uniform defaulting to 0.3. Predict: what happens if you set it to 0.0 vs 1.0 with the same noise map? Which gives the more 'hand-painted' look and why?"

## Acceptance criteria

- [ ] Lesson file: `examples/godot-gamedev/lessons/blender-texture-prep/04-toon-control-maps.html`
- [ ] 3 ramp textures created and working with toon_ramp.gdshader
- [ ] Noise map created (tileable, 256×256) and demonstrated in mk_toon_lite
- [ ] Threshold map extracted from AO and demonstrated
- [ ] Each map shown independently with before/after
- [ ] Explains shader sampling code for each map type
- [ ] SR questions generated (3-5 cards)
- [ ] Reference files: actual texture assets in reference/code/toon-control-maps/

## Research context

**From MK.Toon requirements research:**

Toon-specific control maps (often tool-generated):
| Texture Slot | Purpose |
|-------------|---------|
| Ramp Texture (1D) | Defines light-to-dark band colors. MK.Toon includes a "Ramp Creator" tool. |
| Threshold Map | Per-pixel shading shift (like MToon's `shadingShiftTexture`) |
| Outline Width Map | Per-vertex outline control (grayscale) |

What's procedural vs authored:
- Procedural: banding, specular, rim, shadow color, outline = all computed in shader
- Authored: albedo, normal, shade color texture, ramp, threshold = artist provides

**From toon-texture-pipelines research:**

Guilty Gear ILM map channel packing:
- R: specular mask (which pixels reflect)
- G: shadow offset (light-independent painted shadows) ← this IS a threshold map
- B: specular size control
- A: inner line mask

MToon spec channel packing:
- R = shadingShiftTexture (threshold/shadow boundary shift)
- G = outlineWidthMultiplyTexture
- B = uvAnimationMaskTexture

**From existing-test-scene review:**

mk_toon_lite.gdshader uniform declarations (all EMPTY in scenes):
- `uniform sampler2D noise_map` — used in fragment() to bias NdotL before banding
- `uniform sampler2D diffuse_ramp` — alternative to floor-divide: texture lookup banding
- `uniform sampler2D threshold_map` — shifts shadow boundary per-pixel

ARM texture packing (Poly Haven): R=AO, G=Roughness, B=Metallic
- AO channel directly usable as threshold map base (darker = deeper shadow bias)
- Roughness/Metallic channels irrelevant (shader uses specular_disabled)

**From blender-bake-nodes research:**

For noise map baking:
- Use Blender's procedural Noise Texture node (type: fBM, scale ~4-8 for tileable)
- Connect to Emission shader → bake Emit pass at 256×256
- Set image to Non-Color data (it's a control map, not sRGB)
- Ensure tileability: use modulo UV or Blender's "Seamless" noise option (via Musgrave)
