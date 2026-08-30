# Outlines & Artistic Overlays — Code Files

Final-state shader files from [Lesson 13: Outlines & Artistic Overlays](../../lessons/0013-outlines-overlays.html).

| File | Description |
|------|-------------|
| `toon_outline_hull.gdshader` | Inverted-hull companion shader (apply as next_pass) |
| `overlays_banding.gdshader` | Full toon pipeline with hatching + sketch overlays |

## Outline Shader

Apply as **Next Pass** on your toon material (not as the primary material).

| Uniform | Range | Default | Purpose |
|---------|-------|---------|---------|
| `outline_color` | color | dark navy | Outline flat color |
| `outline_width` | 0–3 | 0.5 | Base width (artist units) |
| `outline_scale` | 0–4 | 1.0 | Global multiplier (LOD/zoom control) |
| `outline_clip_offset` | 0–1 | 0.0 | Removes outlines from thin geometry |

Render modes: `unshaded, cull_front, depth_draw_opaque`

## Overlay Uniforms (main shader)

### Hatching (shadow-weighted)

| Uniform | Range | Default | Purpose |
|---------|-------|---------|---------|
| `use_hatching_dark_map` | bool | false | Enable hatching |
| `hatching_dark_map` | sampler2D | — | Grayscale hatching pattern |
| `hatching_strength` | 0–1 | 0.15 | Visibility in full shadow |
| `hatching_scale` | 0.1–10 | 1.0 | UV tiling |

### Sketch (uniform)

| Uniform | Range | Default | Purpose |
|---------|-------|---------|---------|
| `use_sketch_map` | bool | false | Enable sketch overlay |
| `sketch_map` | sampler2D | — | Grayscale pencil/paper texture |
| `sketch_strength` | 0–1 | 0.08 | Overall visibility |
| `sketch_scale` | 0.1–10 | 1.0 | UV tiling |

## Pipeline order

Overlays apply AFTER Gooch shading, BEFORE specular/rim:
1. Gooch → toon_color (base color with warm/cool)
2. **Overlays** → toon_color *= mix(1.0, texture, weight) (darken only)
3. **Specular/Rim** → toon_color += highlight (brighten on top)

This ensures highlights punch through overlays cleanly.
