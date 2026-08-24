# Specular & Rim Lighting — Code Files

Final-state shader file from [Lesson 12: Specular & Rim Lighting](../../lessons/0012-specular-rim.html).

| File | Description |
|------|-------------|
| `specular_rim_banding.gdshader` | Full toon pipeline + flat specular (Blinn-Phong) + rim lighting (Fresnel) |

## What this adds over Lesson 11

Two additive highlight systems, both using the threshold-smoothstep pattern:

### Flat Specular

| Uniform | Range | Default | Purpose |
|---------|-------|---------|---------|
| `specular_enabled` | bool | false | Master toggle |
| `flat_specular_color` | color | white | Highlight color |
| `flat_specular_size` | 0–1 | 0.1 | Highlight size (bigger = larger) |
| `flat_specular_edge_smoothness` | 0–1 | 0.0 | Hard (0) vs feathered edge |
| `specular_intensity` | 0–2 | 1.0 | Brightness multiplier |

Formula: `smoothstep(1.0 - size - edge, 1.0 - size + edge, NdotH)` — threshold on Blinn-Phong half-vector.

### Rim Lighting

| Uniform | Range | Default | Purpose |
|---------|-------|---------|---------|
| `rim_enabled` | bool | false | Master toggle |
| `rim_color` | color | white | Rim glow color |
| `rim_size` | 0.5–8 | 2.0 | Fresnel power (higher = thinner rim) |
| `rim_smoothness` | 0–1 | 0.5 | Edge softness |
| `rim_intensity` | 0–2 | 1.0 | Brightness multiplier |

Formula: `smoothstep(0.5 - edge, 0.5 + edge, pow(1.0 - NdotV, rim_size))` — threshold on Fresnel.

## The reusable pattern

Both effects are `smoothstep(t-e, t+e, x)` with different inputs:
- Specular: x = NdotH (light-dependent, moves with light)
- Rim: x = pow(1-NdotV, n) (view-dependent, moves with camera)

## Composition

Both are **additive** (`toon_color +=`). They add brightness on top of the diffuse toon shading, allowing highlights brighter than the brightest diffuse band.
