# Wrapped Lighting & Noise Bias — Code Files

Final-state shader file from [Lesson 11: Wrapped Lighting & Noise Bias](../../lessons/0011-wrapped-lighting-noise.html).

| File | Description |
|------|-------------|
| `wrapped_noise_banding.gdshader` | Configurable banding + Gooch + wrapped lighting + noise threshold perturbation |

## What this adds over Lesson 10

Two independent techniques that break geometric perfection:

### Wrapped Lighting

| Uniform | Range | Default | Purpose |
|---------|-------|---------|---------|
| `wrapped_lighting` | 0–1 | 1.0 | Enable/amount of wrap (0=standard Lambert) |
| `wrapped_lighting_scale` | 0–1 | 0.35 | How much wrap contributes to final result |

Formula: `NdotL * (1.0 - wrap) + wrap` — raises the floor of NdotL from 0 to the wrap value. At defaults (effective wrap 0.35), the darkest areas never go below 35% lit.

### Noise Bias

| Uniform | Range | Default | Purpose |
|---------|-------|---------|---------|
| `use_noise_map` | bool | false | Enable noise perturbation |
| `noise_map` | sampler2D | — | Grayscale noise texture (red channel used) |
| `noise_strength` | 0–0.25 | 0.04 | Amount of per-pixel threshold variation |
| `noise_scale` | 0.1–10 | 1.0 | UV tiling for noise texture |

Formula: `(texture.r - 0.5) * noise_strength` — small signed offset added to the centering formula before quantization. Perturbs WHERE band boundaries fall, not brightness values.

## Key insight

- Wrapped lighting changes **how much of the surface is lit** (shifts the terminator)
- Noise changes **where band boundaries wiggle** (per-pixel threshold offset)
- Both apply BEFORE quantization — they affect the input to floor(), not the output
