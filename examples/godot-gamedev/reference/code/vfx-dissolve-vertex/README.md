# VFX: Dissolve & Vertex Animation — Code Files

Final-state shader file from [Lesson 14: VFX — Dissolve & Vertex Animation](../../lessons/0014-vfx-dissolve-vertex.html).

This is the **complete MKToon shader** — the culmination of the 6-lesson per-material toon track (lessons 0009–0014). All features from every lesson are included and independently toggleable.

| File | Description |
|------|-------------|
| `vfx_toon.gdshader` | Complete 190-line toon shader with all features |

## Feature summary (by lesson)

| Feature | Lesson | Stage | Toggle |
|---------|--------|-------|--------|
| Configurable banding | 0009 | light() | always on |
| Gooch warm/cool | 0010 | light() | gooch_ramp_intensity > 0 |
| Wrapped lighting | 0011 | light() | wrapped_lighting_scale > 0 |
| Noise bias | 0011 | light() | use_noise_map |
| Hatching overlay | 0013 | light() | use_hatching_dark_map |
| Sketch overlay | 0013 | light() | use_sketch_map |
| Flat specular | 0012 | light() | specular_enabled |
| Rim lighting | 0012 | light() | rim_enabled |
| Dissolve | 0014 | fragment() | dissolve_enabled |
| Vertex animation | 0014 | vertex() | vertex_animation_enabled |

## Dissolve uniforms

| Uniform | Range | Default | Purpose |
|---------|-------|---------|---------|
| `dissolve_enabled` | bool | false | Master toggle |
| `use_dissolve_map` | bool | false | Map-based vs uniform fade |
| `dissolve_map` | sampler2D | — | Grayscale "burn order" |
| `dissolve_amount` | 0–1 | 0.0 | Progress (0=solid, 1=gone) |
| `dissolve_border_size` | 0–1 | 0.25 | Width of glowing edge |
| `dissolve_border_color` | color | white | Edge glow color |
| `dissolve_map_scale` | 0.1–10 | 1.0 | UV tiling |

## Vertex animation uniforms

| Uniform | Range | Default | Purpose |
|---------|-------|---------|---------|
| `vertex_animation_enabled` | bool | false | Master toggle |
| `vertex_animation_mode` | 0–3 | 0 | 0=off, 1=sine, 2=abs-sine, 3=noise |
| `vertex_animation_intensity` | 0–0.5 | 0.05 | Displacement amount |
| `vertex_animation_frequency` | vec4 | (1,1,1,0) | Phase speeds per axis |
| `vertex_animation_stutter` | 0–1 | 0.0 | Time quantization (0=smooth) |

## Companion outline shader

This shader does NOT include the outline pass. Apply `toon_outline_hull.gdshader` (from Lesson 13) as **Next Pass** on the same material for silhouette outlines.
