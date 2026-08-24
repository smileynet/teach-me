# Gooch Shading — Code Files

Final-state shader file from [Lesson 10: Gooch Warm/Cool Shadows](../../lessons/0010-gooch-shading.html).

| File | Description |
|------|-------------|
| `gooch_banding.gdshader` | Configurable banding + Gooch warm/cool shadow tinting |

## What this adds over Lesson 9

Three new uniforms that replace scalar darkening with a color ramp:

| Uniform | Type | Default | Purpose |
|---------|------|---------|---------|
| `gooch_bright_color` | vec4 (source_color) | white | Warm-side tint for lit areas (white = natural albedo) |
| `gooch_dark_color` | vec4 (source_color) | (0.2, 0.25, 0.35) | Cool-side tint for shadow areas |
| `gooch_ramp_intensity` | float [0–1] | 0.5 | Blend between no tinting (0) and full color shift (1) |

## How it works

Instead of `ALBEDO * lit_factor` (scalar darkening), the shader computes:

```glsl
shadow_tint = mix(ALBEDO, ALBEDO * gooch_dark_color.rgb, intensity)
lit_tint = mix(ALBEDO, ALBEDO * gooch_bright_color.rgb, intensity)
toon_color = mix(shadow_tint, lit_tint, lit_factor)
```

The multiply against ALBEDO ensures the base color always shows through — Gooch tints, never replaces.

## Key insight

With `gooch_bright_color = white`, lit areas are always natural albedo (ALBEDO × white = ALBEDO). Only shadows get the cool tint. This "one-sided Gooch" is what most shipped toon games use.
