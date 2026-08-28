---
id: "221"
title: "Lesson: Emit Bake and glTF Export — Blender to Godot (0019)"
type: feature
status: done
priority: high
blocked_by: ["219", "220"]
parent: "216"
tags: [mktoon, blender]
---

# Lesson: Emit Bake and glTF Export — Blender to Godot (0019)

## Corrected decisions (2026-08-28, research + code audit)

**CORE INSIGHT (changes the scope): glTF exports ALBEDO ONLY; control maps stay separate.**
glTF color space is SLOT-driven, not a per-image flag (glTF spec, Godot conforms):
baseColorTexture→sRGB, normalTexture→linear. A control/data map (our noise/threshold)
routed through an sRGB slot gets sRGB-DECODED and corrupted — and `.glb`-embedded textures
have NO independent `.import` file to fix. So:
- Albedo (posterized+snapped) → Emit bake → glTF baseColorTexture → Godot auto-imports sRGB. ✓
- Control maps (noise/threshold from #220) → stay as standalone Non-Color PNGs referenced
  SEPARATELY in Godot, NOT embedded in the glTF. Teach WHY (the sRGB-slot trap) — this is
  the lesson's central gotcha. #221 reuses #220's control maps; it only bakes/exports albedo.

**Other findings:**
- Consolidated single `bake_export.py` feasible, but factory-reset + rebuild-groups per pass
  is mandatory (reset wipes node_groups). Reuse the .scratch bake recipe (absolute
  filepath_raw + file_format=PNG; the img.save relative-path gotcha).
- glTF export automation: `bpy.ops.export_scene.gltf(export_format='GLB',
  export_image_format='AUTO', export_materials='EXPORT', export_cameras=False,
  export_lights=False, use_selection=True)`. Blender 4.2+ uses `export_vertex_color` (enum),
  NOT `export_colors` (bool).
- Camera_01 IS a genuine 3-material asset → multi-material is a LIVE bake, not explain-only
  (lens = glass/transmission, no albedo texture — a real edge case).
- configurable_banding.gdshader is DIFFERENT from mk_toon_lite; has albedo_texture/
  use_albedo_texture uniforms; NO pre-wired barrel scene (Tier-3 needs scene setup).
- Export a NEW baked .glb (Barrel_01_toon.glb); don't overwrite the existing Poly Haven .gltf.

**Validation (4-tier):**
- Tier-1 sidecar oracle (bake-export-oracle.py, stdlib, in verify): baked albedo is sRGB 1K;
  glTF manifest has NO lights/cameras + expected material/texture; control maps NOT embedded.
- Tier-2: `bake_export.py --check` added to `verify:blender` (#252 gate — the payoff).
- Tier-3a (CI-able): `godot --headless --editor --import --quit` on the .glb → imports clean;
  inspect material texture flags (EditorScript) → albedo sRGB. Headless import proves LOAD,
  not color correctness (research: wrong-colorspace map imports "fine", looks wrong on screen).
- Tier-3b (manual/subagent): visual before/after under configurable_banding (raw PBR vs
  toon-prepped). Needs scene setup + godot_editor subagent. Fallback: Tier-3a + logged gap.

## What to build (ORIGINAL — see corrected decisions above)

A substantial lesson teaching the actual bake-and-export pipeline: capturing simplified textures via Cycles Emit pass and exporting a toon-ready glTF that Godot imports cleanly.

### Lesson arc

1. Why Emit bake? — Captures material color WITHOUT lighting. Combined/Diffuse bakes include scene lighting, which kills dynamic toon shading in Godot. Emit is the one safe bake type.
2. Bake setup in Cycles: add unconnected Image Texture node (selected), set bake type, configure margin/samples
3. Walk through the full bake for Barrel_01: posterized + palette-snapped albedo → Emit bake → saved PNG
4. Handle the multi-material case (Camera_01 has 3 materials) — bake each material's albedo to the same atlas or separate textures
5. Bake the control maps: noise (from procedural) and threshold (from AO extraction)
6. glTF export settings: what to include (mesh + textures), what to exclude (lights, camera, animations)
7. Godot import: verify textures load correctly, color space settings (sRGB for albedo, Non-Color/Linear for control maps)
8. Before/after: Barrel_01 with raw PBR diff vs toon-prepped diff, same configurable_banding shader

### Key concept

> The Emit bake captures what the material outputs BEFORE lighting touches it — the only bake type safe for dynamic toon shading. Any other bake type freezes lighting into the texture, making the toon shader fight baked shadows.

### Code deliverables

- Step-by-step bake settings table (samples, margin, color space per map type)
- glTF export preset for toon-ready assets
- Final texture set for Barrel_01: simplified albedo (1K), noise (256), threshold (1K)

### Exercise

"A colleague bakes using Combined pass with Direct lighting enabled. Their texture looks great in Blender but terrible in Godot under the toon shader — shadows are doubled. Why? What bake type should they use instead?"

## Acceptance criteria

- [x] Lesson file: `examples/godot-gamedev/lessons/blender-texture-prep/05-bake-and-export.html`
- [x] Complete bake settings reference (table format)
- [x] Barrel_01 baked: albedo (posterized+snapped) via Emit; noise+threshold were baked in #220 and stay SEPARATE (glTF is albedo-only — the corrected scope; lesson teaches why)
- [x] Multi-material workflow shown (Camera_01 3-material note incl. glass-lens edge case)
- [x] glTF export → Godot import verified (headless import clean; glb binary parsed: 1 material w/ baseColorTexture → sRGB, 0 cameras, no lights, albedo-only)
- [x] Before/after screenshot under configurable_banding shader (raw PBR vs baked toon albedo — clean textbook A/B)
- [x] Common pitfalls documented (Emit-not-Combined double-shadow; glTF slot-driven color space / control-maps-corruption; PNG-not-JPEG)
- [x] SR questions generated (3-5 cards) — btp-401..405

## Research context

**From blender-bake-nodes research:**

Bake settings reference:
| Setting | Value | Notes |
|---------|-------|-------|
| Render Engine | Cycles | EEVEE cannot bake |
| Bake Type | **Emit** | For color-only (no lighting) |
| Samples | 1-16 | Flat shading needs minimal samples |
| Margin | 4-16 px | Prevents UV seam artifacts |
| Selected to Active | Off | Self-bake (same mesh) |
| Direct/Indirect | N/A (Emit ignores) | Only Combined/Diffuse have these |
| Image Size | 1024 px | Match source resolution |
| Color Space | sRGB (albedo), Non-Color (control maps) | Set BEFORE baking |
| 32-bit Float | No (color), Yes (if precision needed) | |

Emit Pass Bake workflow:
1. Connect stylized/posterized material to Emission shader
2. Set Bake Type to Emit
3. OR: Bake Type = Diffuse with Direct and Indirect UNCHECKED
4. Result: pure material color, no lighting influence
5. Source: BSE #165175

**Critical constraint:** EEVEE cannot bake (as of Blender 4.x/5.x). Shader to RGB works in EEVEE viewport but NOT in Cycles bake. Workaround: replicate the effect with Cycles-compatible nodes (which we do — posterize uses Math nodes, not Shader to RGB).

**From toon-texture-pipelines research:**

RJean Lee's web export workflow (analogous to ours):
1. Design stylized material (using Cycles-compatible nodes only!)
2. UV unwrap
3. Switch to Cycles
4. Create unconnected Image Texture node (selected)
5. Bake Combined (for their unlit use case) — we use Emit instead
6. Save baked texture
7. Export .glb

Limitations documented:
- Screen-space effects cannot be baked
- EEVEE-only nodes break in Cycles baking
- Only surface shading portion bakeable — post-process must be recreated in target engine

**glTF export notes:**
- Poly Haven assets already use glTF (Barrel_01_1k.gltf)
- Blender's glTF exporter handles PBR maps natively
- For toon: we only export albedo (simplified) + normal (if keeping). ARM textures excluded.
- Set texture export to PNG (not JPEG — lossy compression adds noise back)

## Resolution (2026-08-28)

Lesson 0019 bake-and-export: consolidated bake_export.py chains Posterize->PaletteSnap->Emit bake albedo->glTF export (albedo-only; control maps stay separate Non-Color PNGs — the sRGB-slot gotcha). 4-tier validation: Tier-1 sidecar oracle (in verify), Tier-2 verify:blender --check, Tier-3a Godot headless import + glb-binary inspection, Tier-3b visual A/B under configurable_banding. Quiz + 5 SR cards, MAP regenerated. Completes the blender-texture-prep spine through export.
