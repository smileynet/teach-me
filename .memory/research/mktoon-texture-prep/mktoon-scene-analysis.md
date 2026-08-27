# MKToon Test Scene Analysis

## Scene Structure (`scenes/mktoon_test.tscn`)

```
MKToonTestScene (Node3D)
├── Camera3D — positioned at (0, 1.2, 2.5), angled ~20° down, 50° FOV
├── DirectionalLight3D — angled, shadow_enabled=true
└── Barrel (instance of Barrel_01_1k.gltf)
    └── Barrel_01 (MeshInstance3D) — material_override = ShaderMaterial_mktoon
```

The scene instances the Poly Haven Barrel_01 glTF model and overrides its material with an inline ShaderMaterial using the `mk_toon_lite.gdshader`.

## External Resources

| ID | Type | Path |
|---|---|---|
| 1_barrel | PackedScene | `res://assets/polyhaven/Barrel_01/Barrel_01_1k.gltf` |
| 2_shader | Shader | `res://shaders/reference/mk_toon_lite.gdshader` |
| 3_outline | Shader | `res://shaders/reference/mk_toon_lite_outline.gdshader` (loaded but NOT used) |

**Note:** The outline shader is loaded as an ext_resource but never referenced by a SubResource or node. It's dead weight in this scene currently.

## Current Material Configuration (ShaderMaterial_mktoon)

### Parameters that ARE set:

| Parameter | Value | Purpose |
|---|---|---|
| `albedo_color` | Color(0.85, 0.65, 0.4, 1.0) | Flat orange-tan base color |
| `use_albedo_texture` | **false** | Textures OFF — flat color only |
| `light_bands` | 4.0 | 4 discrete lighting steps |
| `light_bands_scale` | 0.5 | Moderate band contribution |
| `light_threshold` | 0.5 | Midpoint light/dark split |
| `diffuse_threshold_offset` | 0.0 | No offset |
| `diffuse_smoothness` | 0.0 | Hard band edges (no blend) |
| `wrapped_lighting` | 1.0 | Wrap enabled |
| `wrapped_lighting_scale` | 0.35 | Moderate wrap effect |
| `gooch_bright_color` | White | Gooch lit side |
| `gooch_dark_color` | Color(0.2, 0.25, 0.35, 1) | Cool blue-gray shadow |
| `gooch_ramp_intensity` | 0.5 | Moderate Gooch influence |

### Parameters NOT set (using shader defaults):

| Feature group | Key parameters | Default state |
|---|---|---|
| **Albedo texture** | `albedo_texture`, `albedo_texture_intensity` | No texture assigned |
| **Normal map** | `use_normal_map`, `normal_map`, `normal_map_intensity/scale` | Disabled |
| **Threshold map** | `use_threshold_map`, `threshold_map`, `threshold_map_scale` | Disabled |
| **Noise map** | `use_noise_map`, `noise_map`, `noise_strength/scale` | Disabled |
| **Hatching** | `use_hatching_dark_map`, `hatching_dark_map`, `hatching_strength/scale` | Disabled |
| **Sketch** | `use_sketch_map`, `sketch_map`, `sketch_strength/scale` | Disabled |
| **Drawn** | `use_drawn_map`, `drawn_map`, `drawn_strength/scale` | Disabled |
| **Dissolve** | `dissolve_enabled`, all dissolve params | Disabled |
| **Specular** | `specular_enabled`, all specular params | Disabled |
| **Rim** | `rim_enabled`, all rim params | Disabled |
| **Iridescence** | `iridescence_enabled`, all iridescence params | Disabled |
| **Vertex animation** | `vertex_animation_enabled` | Disabled |
| **Outline** | (separate shader, not wired as next_pass) | Not applied |

## Available Textures (Barrel_01 from Poly Haven)

Located at `assets/polyhaven/Barrel_01/textures/`:

| File | Size | Purpose | Import mode |
|---|---|---|---|
| `Barrel_01_explosive_diff_1k.jpg` | 175 KB | Diffuse/albedo | VRAM compressed (s3tc), mipmaps on |
| `Barrel_01_explosive_nor_gl_1k.jpg` | 181 KB | Normal map (OpenGL format) | VRAM compressed, `compress/normal_map=1`, mipmaps on |
| `Barrel_01_explosive_arm_1k.jpg` | 238 KB | AO/Roughness/Metallic packed | VRAM compressed, mipmaps on |

All textures are already properly imported by Godot (`.import` files exist with correct settings).

## glTF Material Definition

The original Barrel_01 glTF defines a PBR material with:
- `baseColorTexture` → `Barrel_01_explosive_diff_1k.jpg`
- `normalTexture` → `Barrel_01_explosive_nor_gl_1k.jpg`
- `metallicRoughnessTexture` → `Barrel_01_explosive_arm_1k.jpg`

These are standard Poly Haven 1K PBR textures — exactly what the steering docs recommend for shader validation (not low-res flat-color).

## Project Configuration (project.godot)

- **Main scene:** `res://scenes/shader_test.tscn` (not this scene — this is a secondary test)
- **Engine version:** Godot 4.7
- **Rendering config:** No explicit rendering overrides (using Godot defaults)
- **Autoloads:** `_mcp_game_helper` (godot_ai plugin for remote control)
- **No import defaults section** — each texture uses per-file import settings

## Existing Materials in `materials/`

| File | Shader | Purpose |
|---|---|---|
| `toon_bands_mat.tres` | `toon_bands.gdshader` | Simple 3-band, no texture |
| `toon_bands_outline_test.tres` | (outline shader) | Outline test |
| `toon_bands_with_outline.tres` | `toon_bands.gdshader` + `next_pass` outline | Combined toon+outline |
| `toon_outline_mat.tres` | (outline shader) | Standalone outline |
| `toon_outline_test.tres` | (outline shader) | Outline variant |
| `toon_outline_screen_test.tres` | (screen-space outline?) | Screen-space variant |

None of these use the `mk_toon_lite.gdshader` — the mktoon material is only defined inline in the scene file.

## What Changes Are Needed to Wire Textures

### 1. Enable albedo texture

In the ShaderMaterial_mktoon sub_resource, add:
```
shader_parameter/use_albedo_texture = true
shader_parameter/albedo_texture = ExtResource("<new_ext_resource_id>")
shader_parameter/albedo_texture_intensity = 1.0
```

Add ext_resource pointing to:
```
[ext_resource type="Texture2D" uid="uid://bifq8ujd57bgd" path="res://assets/polyhaven/Barrel_01/textures/Barrel_01_explosive_diff_1k.jpg" id="4_diff"]
```

### 2. Enable normal map

```
shader_parameter/use_normal_map = true
shader_parameter/normal_map = ExtResource("<normal_ext_resource_id>")
shader_parameter/normal_map_intensity = 1.0
shader_parameter/normal_map_scale = 1.0
```

Add ext_resource:
```
[ext_resource type="Texture2D" uid="uid://hdeqeffdyg2n" path="res://assets/polyhaven/Barrel_01/textures/Barrel_01_explosive_nor_gl_1k.jpg" id="5_nor"]
```

### 3. Wire the outline shader as next_pass

Currently the outline shader is loaded but unused. To apply it:
- Create a second SubResource using the outline shader
- Set `next_pass` on the main material to reference it

```
[sub_resource type="ShaderMaterial" id="ShaderMaterial_mktoon_outline"]
shader = ExtResource("3_outline")
shader_parameter/outline_color = Color(0.0078, 0.0549, 0.0863, 1.0)
shader_parameter/outline_width = 0.5
```

Then on the main material:
```
next_pass = SubResource("ShaderMaterial_mktoon_outline")
```

### 4. Update load_steps

Currently `load_steps=5`. Adding 2 texture ext_resources + 1 outline sub_resource = `load_steps=8`.

### 5. ARM texture (optional, not directly supported)

The mk_toon_lite shader does NOT have roughness/metallic/AO uniforms — it's a toon shader that deliberately ignores PBR metallic workflow. The ARM texture (`Barrel_01_explosive_arm_1k.jpg`) is not usable here. This is expected: toon shading replaces PBR lighting, not augments it.

## Summary of Current State

**The scene is a minimal test scaffold.** It loads the barrel mesh and applies the mktoon shader with flat color only. The PBR textures exist and are imported correctly, but none are wired to the shader's texture uniforms. The outline shader is loaded but dangling.

This is a deliberate "phase 1" setup — flat color confirms the toon banding/Gooch shading works. Phase 2 (wiring textures) would validate that the shader handles real-world UV-mapped albedo and normal maps correctly, which is the honest validation the steering docs require.
