# Configurable Banding — Code Files

Final-state shader file from [Lesson 9: Configurable Toon Banding](../../lessons/0009-configurable-banding.html).

| File | Description |
|------|-------------|
| `configurable_banding.gdshader` | Production banding with floor-divide quantization, smoothness blend, scale control, and threshold centering |

## Uniforms

| Uniform | Range | Default | Purpose |
|---------|-------|---------|---------|
| `light_bands` | 1–9 (int) | 4 | Number of discrete brightness levels |
| `light_bands_scale` | 0–1 | 0.5 | How dramatic the shading is (0=flat, 1=full range) |
| `light_threshold` | 0–1 | 0.5 | Where the light/dark midpoint sits |
| `diffuse_threshold_offset` | -1–1 | 0.0 | Fine-tune threshold shift |
| `diffuse_smoothness` | 0–1 | 0.0 | Blend between hard bands (0) and smooth gradient (1) |
| `albedo_color` | color | white | Flat base color |
| `albedo_texture` | sampler2D | — | Optional texture map |
| `use_albedo_texture` | bool | false | Toggle texture on/off |

## Quick presets

| Look | bands | smoothness | scale | threshold |
|------|-------|-----------|-------|-----------|
| Bold comic | 3 | 0.0 | 1.0 | 0.5 |
| Soft anime | 4 | 0.2 | 0.7 | 0.5 |
| Ink wash | 6 | 0.5 | 0.3 | 0.4 |
| Dramatic shadow | 2 | 0.0 | 1.0 | 0.7 |

## Render mode

Uses `specular_disabled` — Godot's built-in PBR specular is turned off. Custom toon specular is added in Lesson 12.
