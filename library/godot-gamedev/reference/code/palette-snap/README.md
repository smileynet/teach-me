# Palette Snapping — code files

Downloadable artifacts for lesson 0017 (Palette Snapping — Color Ramp & 1D Lookup).

## Files

| File | Purpose |
|------|---------|
| `palette_snap.py` | Blender script that builds two reusable node groups — **"Palette Snap A (Ramp)"** (Method A: `RGB to BW → Color Ramp[CONSTANT]`) and **"Palette Snap B (LUT)"** (Method B: `RGB to BW → Combine XYZ → Image Texture[Closest]` on an N×1 palette strip). Text, not a binary `.blend` — diffable and re-runnable. |

## Setup (GUI)

1. Blender → **Scripting** workspace → open `palette_snap.py` → **Run Script**.
2. In any material, **Add → Group → "Palette Snap A (Ramp)"** or **"Palette Snap B (LUT)"**.
3. Wire your **posterized albedo** (an Image Texture, or the output of the "Posterize RGB" group from lesson 0016) into the group's `Color` input and the group's `Color` output into **Base Color** (or an Emission for a flat preview/bake).
4. Chain them: `Image Texture → Posterize RGB → Palette Snap` is the combined **Toon Prep** flow.

## Setup (headless)

Build and save a `.blend` containing both groups (palette strip packed):

```
blender -b --python palette_snap.py -- --save palette_snap.blend
```

Validate both node groups are wired correctly (used by the lesson's test tier):

```
blender -b --python palette_snap.py -- --check
```

## When to use which

- **Method A (Ramp)** — quick, visual, GUI-editable. Best when hand-tuning a look with a handful of colors.
- **Method B (LUT)** — scales to a shared palette across many assets, and keeps the palette **swappable at runtime**: sample the same N×1 strip in a Godot shader instead of baking it in (see `reference/code/color-simplification/palette_snap.gdshader` for the runtime nearest-color counterpart).

## The math

Both methods map luminance to a palette slot: `idx = clamp(floor(lum * N), 0, N-1)`.
Method B then samples the strip at the texel **center** `(idx + 0.5) / N` with
**Closest** interpolation — center-sampling avoids the off-by-one that border-sampling
(`idx / N`) risks when a luminance lands a hair below a texel boundary. The
luminance→slot mapping, the k/N boundaries, and the center-vs-edge sampling claim are
all verified by `tools/palette-snap-oracle.py`.

Palette (6-color warm-toon, darkest→lightest) is defined once in `palette_snap.py`
and mirrored in the oracle. Band count and palette count are independent: the shader
sets how many bands; the palette sets which colors those bands show.

## Color space (important)

The **palette strip** (Method B's N×1 image) is created as **Non-Color** so the
authored sRGB swatches aren't view-transformed on lookup. Sample it with **Closest**
(never Linear) so adjacent swatches never blend. The source albedo Image Texture's
color space follows the same rule taught in lesson 0016.
