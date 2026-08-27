# mk_toon_lite.gdshader — Full Analysis

Source: `D:/code/teach-me/test-scene/shaders/reference/mk_toon_lite.gdshader`

## 1. Render Mode

```glsl
render_mode specular_disabled;
```

Disables Godot's built-in specular pipeline entirely. The shader implements its own flat specular via the `specular_enabled` toggle in `light()`.

## 2. All Uniform Declarations

### Scalar/Vector Uniforms (with defaults)

| Uniform | Type | Default | Hint |
|---------|------|---------|------|
| `albedo_color` | vec4 | `vec4(1.0)` | source_color |
| `use_albedo_texture` | bool | `false` | — |
| `albedo_texture_intensity` | float | `1.0` | hint_range(0.0, 1.0) |
| `light_bands` | float | `4.0` | hint_range(1.0, 9.0, 1.0) |
| `light_bands_scale` | float | `0.5` | hint_range(0.0, 1.0) |
| `light_threshold` | float | `0.5` | hint_range(0.0, 1.0) |
| `diffuse_threshold_offset` | float | `0.0` | hint_range(-1.0, 1.0) |
| `diffuse_smoothness` | float | `0.0` | hint_range(0.0, 1.0) |
| `use_threshold_map` | bool | `false` | — |
| `threshold_map_scale` | float | `1.0` | — |
| `use_normal_map` | bool | `false` | — |
| `normal_map_intensity` | float | `1.0` | hint_range(0.0, 2.0) |
| `normal_map_scale` | float | `1.0` | — |
| `wrapped_lighting` | float | `1.0` | hint_range(0.0, 1.0) |
| `wrapped_lighting_scale` | float | `0.35` | hint_range(0.0, 1.0) |
| `gooch_bright_color` | vec4 | `vec4(1.0)` | source_color |
| `gooch_dark_color` | vec4 | `vec4(0.2, 0.25, 0.35, 1.0)` | source_color |
| `gooch_ramp_intensity` | float | `0.5` | hint_range(0.0, 1.0) |
| `use_noise_map` | bool | `false` | — |
| `noise_strength` | float | `0.04` | hint_range(0.0, 0.25) |
| `noise_scale` | float | `1.0` | — |
| `use_hatching_dark_map` | bool | `false` | — |
| `hatching_strength` | float | `0.15` | hint_range(0.0, 1.0) |
| `hatching_scale` | float | `1.0` | — |
| `use_sketch_map` | bool | `false` | — |
| `sketch_strength` | float | `0.08` | hint_range(0.0, 1.0) |
| `sketch_scale` | float | `1.0` | — |
| `use_drawn_map` | bool | `false` | — |
| `drawn_strength` | float | `0.08` | hint_range(0.0, 1.0) |
| `drawn_scale` | float | `1.0` | — |
| `drawn_clamp_min` | float | `0.0` | hint_range(0.0, 1.0) |
| `drawn_clamp_max` | float | `1.0` | hint_range(0.0, 1.0) |
| `dissolve_enabled` | bool | `false` | — |
| `use_dissolve_map` | bool | `false` | — |
| `dissolve_amount` | float | `0.0` | hint_range(0.0, 1.0) |
| `dissolve_border_size` | float | `0.25` | hint_range(0.0, 1.0) |
| `dissolve_border_color` | vec4 | `vec4(1.0)` | source_color |
| `dissolve_map_scale` | float | `1.0` | — |
| `specular_enabled` | bool | `false` | — |
| `flat_specular_color` | vec4 | `vec4(1.0)` | source_color |
| `flat_specular_size` | float | `0.1` | hint_range(0.0, 1.0) |
| `flat_specular_edge_smoothness` | float | `0.0` | hint_range(0.0, 1.0) |
| `specular_threshold_offset` | float | `0.25` | hint_range(0.0, 1.0) |
| `specular_intensity` | float | `1.0` | — |
| `rim_enabled` | bool | `false` | — |
| `rim_color` | vec4 | `vec4(1.0)` | source_color |
| `rim_bright_color` | vec4 | `vec4(1.0)` | source_color |
| `rim_dark_color` | vec4 | `vec4(0.0, 0.0, 0.0, 1.0)` | source_color |
| `rim_size` | float | `2.0` | hint_range(0.0, 8.0) |
| `rim_smoothness` | float | `0.5` | hint_range(0.0, 1.0) |
| `rim_threshold_offset` | float | `0.25` | hint_range(0.0, 1.0) |
| `iridescence_enabled` | bool | `false` | — |
| `iridescence_color` | vec4 | `vec4(1.0)` | source_color |
| `iridescence_size` | float | `1.0` | hint_range(0.0, 8.0) |
| `iridescence_smoothness` | float | `0.5` | hint_range(0.0, 1.0) |
| `iridescence_threshold_offset` | float | `0.0` | hint_range(0.0, 1.0) |
| `vertex_animation_enabled` | bool | `false` | — |
| `vertex_animation_mode` | int | `0` | hint_range(0, 3, 1) |
| `vertex_animation_intensity` | float | `0.05` | — |
| `vertex_animation_frequency` | vec4 | `vec4(1.0, 1.0, 1.0, 0.0)` | — |
| `vertex_animation_stutter` | float | `0.0` | — |
| `use_vertex_animation_map` | bool | `false` | — |
| `vertex_animation_map_scale` | float | `1.0` | — |
| `alpha_clip_enabled` | bool | `false` | — |
| `alpha_cutoff` | float | `0.5` | hint_range(0.0, 1.0) |
| `brightness` | float | `1.0` | — |
| `saturation` | float | `1.0` | — |
| `contrast` | float | `1.0` | — |
| `hue` | float | `0.0` | — |

### Texture Sampler Uniforms (NO defaults — require assignment or use Godot's placeholder)

| Uniform | Hint | Guarded by |
|---------|------|-----------|
| `albedo_texture` | source_color | `use_albedo_texture` |
| `threshold_map` | — | `use_threshold_map` |
| `normal_map` | — | `use_normal_map` |
| `noise_map` | — | `use_noise_map` |
| `hatching_dark_map` | — | `use_hatching_dark_map` |
| `sketch_map` | — | `use_sketch_map` |
| `drawn_map` | — | `use_drawn_map` |
| `dissolve_map` | — | `use_dissolve_map` |
| `vertex_animation_map` | — | `use_vertex_animation_map` |

**Total: 9 texture samplers**, all guarded by boolean toggles.

## 3. How Each Texture Is Used

### fragment() textures

| Texture | Used in | What it does |
|---------|---------|--------------|
| `albedo_texture` | `fragment()` | Multiplies albedo_color.rgb by texture.rgb (weighted by `albedo_texture_intensity`). Also multiplies base.a by texture alpha. |
| `dissolve_map` | `fragment()` | Red channel compared against `dissolve_amount` — pixels below threshold are discarded. Pixels near the threshold get `dissolve_border_color` blended in. |
| `normal_map` | `fragment()` | Assigned directly to `NORMAL_MAP` with `NORMAL_MAP_DEPTH` set to intensity. UV scaled by `normal_map_scale`. |

### light() textures

| Texture | Used in | What it does |
|---------|---------|--------------|
| `noise_map` | `light()` | Red channel (centered at 0.5) added as bias to the diffuse threshold. Creates organic irregularity in shadow edge. |
| `threshold_map` | `light()` | Red channel (centered at 0.5) added as bias to diffuse threshold. Spatial variation of shadow placement. |
| `hatching_dark_map` | `light()` | Red channel multiplied into toon_color in shadow regions (weighted by `shadow_weight * hatching_strength`). Darkens shadowed areas with hatch texture. |
| `sketch_map` | `light()` | Red channel multiplied uniformly into toon_color (weighted by `sketch_strength`). Constant sketch overlay regardless of lighting. |
| `drawn_map` | `light()` | Red channel remapped via clamp_min/clamp_max range, then multiplied into toon_color (weighted by `drawn_strength`). Similar to sketch but with adjustable contrast. |

### vertex() textures

| Texture | Used in | What it does |
|---------|---------|--------------|
| `vertex_animation_map` | `vertex()` | Red channel used as a mask for vertex displacement intensity. Areas with dark pixels don't animate. |

## 4. Default Behavior When Textures Are NOT Assigned

Since every texture sampler is guarded by a `use_*` boolean (all defaulting to `false`), **unassigned textures are never sampled**. The shader safely skips all texture reads when toggles are off.

If a toggle were set to `true` WITHOUT assigning a texture, Godot would sample a **1x1 white placeholder texture** (the default for unassigned sampler2D in Godot 4.x). Effects:

| Texture | Effect if sampled but unassigned (white pixel = 1.0) |
|---------|------------------------------------------------------|
| `albedo_texture` | `mix(albedo_color, albedo_color * 1.0, intensity)` = no visible change (identity) |
| `threshold_map` | `1.0 - 0.5 = 0.5` bias added — shifts shadow edge significantly toward lit |
| `normal_map` | White (1,1,1) interpreted as normal = invalid normal map (would look like flat-ish normals pointing outward) |
| `noise_map` | `(1.0 - 0.5) * noise_strength` = constant positive bias, shifts all shadow edges slightly |
| `hatching_dark_map` | `1.0` = no darkening (identity multiply) |
| `sketch_map` | `1.0` = no darkening (identity multiply) |
| `drawn_map` | `1.0` after remap = no darkening (identity multiply) |
| `dissolve_map` | `1.0 > dissolve_amount` for any amount < 1.0, so nothing dissolves |
| `vertex_animation_map` | `1.0` mask = full animation everywhere (same as no mask) |

**Key insight:** The pattern-overlay textures (hatching, sketch, drawn) are multiplicative — a white (1.0) texture is identity. But threshold/noise maps are centered at 0.5, so a white (1.0) texture creates a non-neutral bias.

## 5. Boolean Toggles (Enable/Disable Features)

| Toggle | Default | What it guards |
|--------|---------|---------------|
| `use_albedo_texture` | `false` | Albedo texture sampling in fragment() |
| `use_threshold_map` | `false` | Threshold map sampling in light() |
| `use_normal_map` | `false` | Normal map assignment in fragment() |
| `use_noise_map` | `false` | Noise map bias in light() |
| `use_hatching_dark_map` | `false` | Hatching overlay in light() shadows |
| `use_sketch_map` | `false` | Sketch overlay in light() |
| `use_drawn_map` | `false` | Drawn overlay in light() |
| `use_dissolve_map` | `false` | Dissolve mask in fragment() |
| `use_vertex_animation_map` | `false` | Animation mask in vertex() |
| `dissolve_enabled` | `false` | Entire dissolve system (parent toggle) |
| `specular_enabled` | `false` | Custom flat specular in light() |
| `rim_enabled` | `false` | Rim lighting in light() |
| `iridescence_enabled` | `false` | Iridescence effect in light() |
| `vertex_animation_enabled` | `false` | Vertex displacement in vertex() |
| `alpha_clip_enabled` | `false` | Alpha cutoff discard in fragment() |

**Toggle hierarchy:**
- `dissolve_enabled` → `use_dissolve_map` (dissolve must be enabled first, THEN optionally use a map)
- `vertex_animation_enabled` → `use_vertex_animation_map` (animation must be active first)
- All other `use_*` toggles are independent

## 6. Architecture Summary

The shader implements a modular toon-shading pipeline:

```
vertex()  → Optional vertex animation (wave/noise displacement with optional mask map)
fragment() → Albedo (color × optional texture) → Dissolve → Alpha clip → Color adjustments → Normal map
light()   → Wrapped diffuse → Band quantization (with noise/threshold bias) → Gooch ramp → 
             Overlay textures (hatching/sketch/drawn) → Additive effects (rim/iridescence/specular)
```

**Design pattern:** Every optional feature follows the same convention:
1. Boolean toggle `use_X` or `X_enabled` (defaults to `false`)
2. Sampler/parameters declared adjacent
3. Feature code wrapped in `if (toggle)` block
4. Texture only sampled inside the guarded block

This means the shader compiles to a minimal path (just banded lighting with Gooch ramp) when all toggles are off, and features can be mixed freely.
