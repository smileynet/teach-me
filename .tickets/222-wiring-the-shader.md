---
id: "222"
title: "Lesson: Wiring It All Up — Populate mk_toon_lite in Godot (0020)"
type: feature
status: open
priority: high
blocked_by: ["221"]
parent: "216"
---

# Lesson: Wiring It All Up — Populate mk_toon_lite in Godot (0020)

## What to build

A substantial lesson that closes the loop: take all exported textures and wire them into the full mk_toon_lite shader in Godot. Before/after proof that the pipeline works end-to-end.

### Lesson arc

1. Import the toon-prepped glTF into the test-scene project
2. Create a ShaderMaterial using mk_toon_lite.gdshader
3. Wire each texture slot one at a time, showing the visual effect of EACH addition:
   - `albedo_texture` → simplified albedo (posterized + palette-snapped)
   - `normal_map` → original Poly Haven normal map (keep detail for shadow contour)
   - `noise_map` → tileable noise from lesson 0018
   - `threshold_map` → AO-derived threshold from lesson 0018
   - `diffuse_ramp` → warm-cool ramp from lesson 0018
4. Compare: flat color (current mktoon_test) → simplified albedo → full control maps
5. A/B comparison: same mesh with raw PBR textures under StandardMaterial3D vs toon-prepped under mk_toon_lite
6. Document the "recipe" — which slots are essential (albedo, noise, ramp) vs optional (threshold, hatching, sketch)
7. Apply to a second asset (Camera_01 or Lantern_01) to prove generalizability

### Key concept

> A toon shader without populated texture slots is like a synthesizer with all knobs at zero — technically working but producing nothing distinctive. Each control map you author gives you one more axis of artistic control over how light interacts with the surface.

### Code deliverables

- Updated `mktoon_test.tscn` (or new scene) with all texture slots populated
- Material .tres resource with full shader parameter configuration
- Before/after screenshots (minimum 3: flat color, simplified albedo only, full control maps)

### Exercise

"Your artist hands you a new asset. Rank these texture prep steps from 'essential' to 'polish': (A) create ramp texture, (B) posterize albedo, (C) author threshold map, (D) connect normal map, (E) create noise map. Explain your ranking."

## Acceptance criteria

- [ ] Lesson file: `examples/godot-gamedev/lessons/blender-texture-prep/06-wiring-the-shader.html`
- [ ] `mktoon_test.tscn` updated with populated texture slots (committed to test-scene)
- [ ] Progressive screenshots: each slot added one at a time
- [ ] Full A/B comparison: PBR (StandardMaterial3D) vs toon-prepped (mk_toon_lite)
- [ ] Minimum 2 assets demonstrate the pipeline (Barrel + one other)
- [ ] "Essential vs optional" texture slot guide
- [ ] SR questions generated (3-5 cards)
- [ ] Visual validation: rendered in Godot editor, not just assumed correct

## Research context

**From existing-test-scene review:**

Current state of mktoon_test.tscn:
- Uses `mk_toon_lite.gdshader` on Barrel_01
- `use_albedo_texture = false` (flat orange color only)
- NO texture maps assigned to any uniform
- Default banding: 4 bands, 0.5 scale/threshold

mk_toon_lite.gdshader texture uniforms (all empty):
```gdshader
uniform sampler2D albedo_texture : source_color;
uniform sampler2D normal_map : hint_normal;
uniform sampler2D noise_map;
uniform sampler2D threshold_map;
uniform sampler2D hatching_dark_map;
uniform sampler2D sketch_map;
uniform sampler2D drawn_map;
uniform sampler2D dissolve_map;
uniform sampler2D vertex_animation_map;
```

**From MK.Toon requirements research:**

Essential vs optional (based on MK.Toon and UTS analysis):
| Priority | Slot | Why |
|----------|------|-----|
| Essential | albedo_texture | Defines the surface color |
| Essential | diffuse_ramp OR band parameters | Defines the shading style |
| High | noise_map | Breaks mechanical-looking band edges |
| Medium | normal_map | Adds surface detail to shadow contours |
| Medium | threshold_map | Spatial shadow variation without hand-painting |
| Optional | hatching/sketch/drawn | Artistic overlay effects |
| Optional | dissolve_map | VFX only (not always-on) |

**From toon-texture-pipelines research:**

Key validation insight:
- "Don't trust visual validation on pixel-art assets" (AGENTS.md) — use 1K+ PBR textures
- Our pipeline converts those 1K PBR textures to toon-friendly and validates under the actual shader
- Visual confirmation in Godot editor is non-negotiable (compiles ≠ correct)

Normal map gotcha:
- Normal maps can SOFTEN toon band edges (the perturbed normal creates gradual NdotL transition)
- This is documented in MK.Toon: "seamlessly integrated normal mapping into the stylized lighting"
- May need to reduce normal intensity or quantize AFTER normal perturbation
- Worth documenting as a decision point in the lesson
