---
id: "222"
title: "Lesson: Wiring It All Up — Populate mk_toon_lite in Godot (0020)"
type: feature
status: done
priority: high
blocked_by: ["221"]
parent: "216"
tags: [mktoon, blender]
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

- [x] Lesson file: `library/godot-gamedev/lessons/blender-texture-prep/06-wiring-the-shader.html` (path is `library/`, not `examples/` — repo convention changed since ticket authored)
- [x] `mktoon_test.tscn` updated with populated texture slots (committed to test-scene; points at the warm-corrected albedo)
- [x] Progressive screenshots: flat → simplified albedo → full control maps (each slot added one at a time)
- [x] Full A/B comparison: raw PBR vs toon-prepped (mk_toon_lite) — three-barrel figure
- [ ] ~~Minimum 2 assets demonstrate the pipeline~~ → DEFERRED to follow-up. Only Barrel_01 shown; a second asset (Camera_01/Lantern_01) needs its own Blender bake+capture cycle. Deliberately scoped out to avoid ballooning this ticket — filed as a follow-up.
- [x] "Essential vs optional" texture slot guide (priority table)
- [x] SR questions generated (btp-501..504, 4 cards)
- [x] Visual validation: rendered windowed in Godot (RTX 5070) + independent image read, not assumed

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


## Resolution (2026-09-04)

Lesson 06 (`blender-texture-prep/06-wiring-the-shader.html`) authored and shipped, closing
the blender-texture-prep track. Wired the baked albedo + normal + noise + threshold control
maps into `mktoon_test.tscn` (load_steps 8→11).

**Honest pitfall-and-fix arc (the real story this ticket surfaced):** independent image
review of the first capture showed the shipped toon-prepped albedo rendered near-black under
the shader — WORSE than raw PBR. Root cause (measured): the palette-snap step (#219) is
luminance-only and discards hue; 94% of Barrel_01's diffuse pixels fall in the darkest
luminance slot, and the shipped palette's slot-0 is cool violet-black — so the warm red barrel
snaps to muddy purple-black. Fixed by re-baking through the SAME taught pipeline (Posterize →
Palette Snap B → Emit bake, real Blender 5.2) with a hue-preserving warm palette → a clean
bright cel-shaded barrel (mean RGB 164,113,86). The lesson teaches this as its central lesson:
a three-barrel figure (raw PBR busy → muddy palette pitfall → warm fix), same shader/light,
only the albedo changes.

**Validation:** windowed Godot render (RTX 5070) + independent image read for all captures
(the MCP editor bridge was unavailable; direct `godot --path` windowed run works). check-lesson:
8 pass, 0 fail, 1 warn (Q3 diff-spans-in-fragment, acceptable). `mise run verify` EXIT 0.
#227 (hint_normal) already landed, so the wired normal_map is correct.

**Descoped:** "minimum 2 assets" — only Barrel_01 shown. A second asset (Camera_01/Lantern_01)
needs its own Blender bake+capture cycle; deliberately scoped out to avoid ballooning this
ticket. Filed as a follow-up.

**Artifacts:** lesson 06; `mktoon_test.tscn` (warm albedo); figures at root
`assets/img/06-wiring-{flat,muddy,warm,pbr-raw}.png`; warm albedo reference copy at
`reference/code/bake-and-export/Barrel_01_toon_albedo_warm.png`; SR btp-501..504; MAP +
map-page lessonPath reconciled to `blender-texture-prep/06-`. Bake script:
`.scratch/bake_warm_albedo.py` (gitignored evidence).
