# Albedo Posterization — code files

Downloadable artifacts for lesson 0016 (Albedo Posterization in Blender Nodes).

## Files

| File | Purpose |
|------|---------|
| `posterize_rgb.py` | Blender script that builds the reusable **"Posterize RGB"** shader node group (Method A: `Multiply(N) → Floor → Divide(N)` over RGB). Text, not a binary `.blend` — diffable and re-runnable. |

## Setup (GUI)

1. Blender → **Scripting** workspace → open `posterize_rgb.py` → **Run Script**.
2. In any material, **Add → Group → "Posterize RGB"**.
3. Wire an **Image Texture** into the group's `Color` input and the group's `Color` output into **Base Color** (or an Emission for a flat preview/bake).
4. Set the group's **Levels** input to your band count (2–16). Match your toon shader's `color_levels` for visual harmony.

## Setup (headless)

Build and save a `.blend` containing the group:

```
blender -b --python posterize_rgb.py -- --save posterize_rgb.blend
```

Validate the node group is wired correctly (used by the lesson's test tier):

```
blender -b --python posterize_rgb.py -- --check
```

## The math

The group computes `floor(color * N) / N` component-wise — the same operation
`test-scene/shaders/posterize_albedo.gdshader` does in-shader (`color_levels = N`).
This truncating form tops out at `(N-1)/N` (white is never reached). The lesson
also teaches the canonical round-to-nearest, endpoint-inclusive form
`floor(color * (N-1) + 0.5) / (N-1)` (preserves both black and white); both are
verified by `tools/posterize-oracle.py`.

## Color space (important)

Set the input Image Texture's **Color Space** deliberately:
- **sRGB / Color** — decoded to linear before the math; bands cluster in shadows.
- **Non-Color** — quantizes stored values; perceptually even bands.

Blender auto-guesses (sRGB for PNG/JPG); pin it explicitly for reproducible output.
