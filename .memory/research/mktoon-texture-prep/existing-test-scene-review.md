# Existing Test-Scene & MKToon Shader Review

Date: 2026-08-26

## Project Structure (test-scene/)

A Godot 4.7 project used for validating lesson shaders. Key directories:

```
test-scene/
├── assets/
│   ├── polyhaven/          — PBR models (Barrel_01, Camera_01, Lantern_01) with 1K textures
│   ├── kaykit-dungeon/     — Low-poly dungeon pieces (walls, pillars, stairs) with flat textures
│   ├── kenney-retro-urban/ — Low-poly urban kit (walls, trucks, trees, roads)
│   ├── kenney-mini-chars/  — Low-poly characters
│   └── quaternius-characters/ — Higher-poly characters (Knight, Viking, Wizard)
├── shaders/
│   ├── *.gdshader          — All lesson shaders (copied from examples/godot-gamedev/reference/code/)
│   ├── reference/          — mk_toon_lite.gdshader + mk_toon_lite_outline.gdshader
│   └── validation/         — test_posterize_bands.gdshader, test_albedo_default.gdshader
├── scenes/
│   ├── mktoon_test.tscn    — Barrel_01 with mk_toon_lite applied
│   ├── shader_test.tscn    — Basic shader testing
│   ├── combined_test.tscn  — Combined shader test
│   ├── outline_test.tscn   — Outline shader test
│   └── color_test.tscn     — Color simplification test
├── materials/              — Pre-configured .tres material resources
├── scripts/                — auto_capture.gd, capture_viewport.gd, capture_ab.gd
└── addons/godot_ai/        — MCP addon for programmatic control
```

## Poly Haven Assets (PBR, 1K resolution)

### Barrel_01
- **Mesh**: `Barrel_01.bin` + `Barrel_01_1k.gltf`
- **Textures**: `textures/Barrel_01_explosive_diff_1k.jpg`, `_nor_gl_1k.jpg`, `_arm_1k.jpg`

### Camera_01
- **Mesh**: `Camera_01.bin` + `Camera_01_1k.gltf`
- **Textures** (3 material groups):
  - body: `Camera_01_body_diff_1k.jpg`, `_nor_gl_1k.jpg`, `_arm_1k.jpg`
  - lens_body: `Camera_01_lens_body_diff_1k.jpg`, `_nor_gl_1k.jpg`, `_arm_1k.jpg`
  - strap: `Camera_01_strap_diff_1k.jpg`, `_nor_gl_1k.jpg`, `_arm_1k.jpg`

### Lantern_01
- **Mesh**: `Lantern_01.bin` + `Lantern_01_1k.gltf`
- **Textures**: `Lantern_01_brass_diff_1k.jpg`, `_nor_gl_1k.jpg`, `_arm_1k.jpg`

**Texture map types present:**
- `_diff_` = Diffuse/Albedo color
- `_nor_gl_` = Normal map (OpenGL format)
- `_arm_` = AO/Roughness/Metallic packed (R=AO, G=Roughness, B=Metallic)

## Shaders Already Written

### Core Banding Pipeline (progressive complexity)
| File | Lesson | Features |
|------|--------|----------|
| `toon_test.gdshader` | 01 Anatomy | Minimal flat magenta shader |
| `toon_bands.gdshader` | 03 Banding | Modulo-trick banding with wrap+steepness |
| `toon_smoothstep.gdshader` | 03 Banding | Smoothstep variant (not in final) |
| `toon_ramp.gdshader` | 03 Banding | Ramp texture lookup |
| `configurable_banding.gdshader` | 09 Configurable | Floor-divide quantization, smoothness, scale, threshold |
| `wrapped_noise_banding.gdshader` | 10 Wrapped+Noise | Adds wrap + noise map to configurable banding |
| `gooch_banding.gdshader` | 10 Gooch | Adds warm/cool color ramp |
| `specular_rim_banding.gdshader` | 12 Specular+Rim | Flat specular + rim lighting |
| `overlays_banding.gdshader` | 13 Overlays | Hatching + sketch map overlays |
| `vfx_toon.gdshader` | 14 VFX/Dissolve | Full shader with dissolve, vertex animation |

### Reference Shaders (mktoon)
| File | Description |
|------|-------------|
| `reference/mk_toon_lite.gdshader` | Full-featured toon shader (~270 lines). Includes: albedo texture, normal map, threshold map, noise map, hatching/sketch/drawn overlays, dissolve, specular, rim, iridescence, vertex animation, alpha clip, HSV adjustments, Gooch shading |
| `reference/mk_toon_lite_outline.gdshader` | Inverted-hull outline shader (cull_front, unshaded) |

### Outline Shaders
| File | Description |
|------|-------------|
| `toon_outline.gdshader` | Basic inverted hull |
| `toon_outline_screen.gdshader` | Screen-space edge detection |
| `toon_outline_smooth.gdshader` | Smooth outline variant |
| `toon_outline_jfa_pass.gdshader` | Jump Flood Algorithm outline |
| `toon_outline_colorid.gdshader` | Color ID pass |
| `toon_outline_colorid_detect.gdshader` | Color ID edge detection |
| `toon_outline_hull.gdshader` | Hull outline (lesson 13) |

### Color Simplification
| File | Description |
|------|-------------|
| `kuwahara_basic.gdshader` | Kuwahara filter |
| `posterize_screen.gdshader` | Screen-space posterization |
| `posterize_albedo.gdshader` | Albedo posterization |
| `palette_snap.gdshader` | Palette snapping |

### Triplanar
| File | Description |
|------|-------------|
| `triplanar_toon.gdshader` | Triplanar + toon banding |

## Texture Maps Referenced by Current Shaders

The shaders declare these sampler2D uniforms (what textures they CAN accept):

| Uniform | Used in | Purpose |
|---------|---------|---------|
| `albedo_texture` | All banding shaders | Base color map |
| `diffuse_ramp` | toon_ramp.gdshader | 1D gradient lookup for banding |
| `noise_map` | wrapped_noise, specular_rim, overlays, vfx_toon, mk_toon_lite | Break up band edges |
| `hatching_dark_map` | overlays, vfx_toon, mk_toon_lite | Cross-hatching in shadows |
| `sketch_map` | overlays, vfx_toon, mk_toon_lite | Pencil/sketch overlay |
| `drawn_map` | mk_toon_lite | Hand-drawn texture overlay |
| `normal_map` | mk_toon_lite | Normal mapping |
| `threshold_map` | mk_toon_lite | Per-pixel threshold variation |
| `dissolve_map` | mk_toon_lite, vfx_toon | Dissolve mask pattern |
| `vertex_animation_map` | mk_toon_lite, vfx_toon | Vertex displacement mask |

## What the mktoon_test Scene Uses

The `mktoon_test.tscn` scene:
- Uses `mk_toon_lite.gdshader` on the Barrel_01 model
- Sets `use_albedo_texture = false` (flat color only: warm orange `Color(0.85, 0.65, 0.4)`)
- Does NOT assign any texture maps (noise, hatching, normal, etc.)
- Uses default banding settings (4 bands, 0.5 scale/threshold)

## Gaps for Toon Texture Prep

### 1. No texture maps are actually assigned in scenes
The shaders declare uniforms for `noise_map`, `hatching_dark_map`, `sketch_map`, `normal_map`, `threshold_map`, `drawn_map`, and `dissolve_map` — but **no scene currently assigns actual texture resources to these uniforms**. The Poly Haven textures (diffuse, normal, ARM) exist but aren't wired up.

### 2. No albedo textures applied to toon shaders
The mktoon_test scene uses flat `albedo_color` only. None of the Poly Haven `_diff_` textures are applied to any toon shader material. The shaders support `use_albedo_texture = true` but it's never used in practice.

### 3. Missing toon-specific texture assets
- **Ramp textures**: `toon_ramp.gdshader` needs a `diffuse_ramp` texture — none exists in the project
- **Noise maps**: For breaking band edges — none provided as actual texture files
- **Hatching/sketch textures**: The shaders support them but no tileable hatching texture exists
- **Threshold maps**: For per-pixel threshold variation — none provided

### 4. Normal maps not tested with toon banding
The Poly Haven assets include `_nor_gl_` normal maps, and `mk_toon_lite` supports them, but no scene demonstrates normal mapping + toon banding together. This is important for showing how normal maps add surface detail to banded lighting.

### 5. ARM textures unused
The `_arm_` (AO/Roughness/Metallic) textures from Poly Haven aren't referenced by any toon shader. Since toon shaders use `specular_disabled` render mode, roughness/metallic channels are irrelevant — but the AO channel could be extracted for shadow enrichment.

### 6. No texture prep workflow documented
There's no documentation or script for:
- Converting PBR textures to toon-friendly formats
- Generating ramp textures programmatically
- Creating noise/hatching tileable textures
- Baking toon-appropriate threshold maps from PBR AO data

## Summary

The test-scene has solid **mesh variety** (PBR Poly Haven props + low-poly game assets) and a **complete shader progression** from basic banding through full mk_toon_lite. But the texture pipeline is empty — shaders declare texture uniforms that are never populated with actual textures in any scene. The gap is the **"texture prep" layer** between raw PBR assets and toon shader inputs.
