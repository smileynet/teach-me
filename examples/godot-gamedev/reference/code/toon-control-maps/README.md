# Toon Control Maps — code files

Downloadable artifacts for lesson 0018 (Authoring Toon Control Maps — Noise & Threshold).

## Files

| File | Purpose |
|------|---------|
| `control_maps.py` | Blender script that bakes the two maps `mk_toon_lite.gdshader` samples: a **tileable 256×1... 256×256 Non-Color noise map** (via the 4D-noise trick) and a **threshold map** derived from the Barrel_01 ARM texture's red (AO) channel. Text, not a binary `.blend` — diffable and re-runnable. Also writes `control-maps-sidecar.json` (measured properties) and doubles as the lesson's Tier-2 validator. |
| `toon_noise.png` | The baked 256×256 Non-Color tileable noise map. |
| `toon_threshold.png` | The baked threshold map (from ARM red = AO). |
| `control-maps-sidecar.json` | Bake-time measurements (dims, colorspace, edge-match, AO correlation) — the Tier-1 oracle reads this. |

## Setup (headless)

Build the noise node group and save a `.blend`:

```
blender -b --python control_maps.py -- --save control_maps.blend
```

Bake both maps + the sidecar into a directory:

```
blender -b --python control_maps.py -- --bake examples/godot-gamedev/reference/code/toon-control-maps
```

Validate the node wiring (used by the lesson's test tier):

```
blender -b --python control_maps.py -- --check
```

## What the maps do (mk_toon_lite.gdshader, in `light()`)

Both maps perturb the band-boundary position per-fragment, just before `floor()` banding:

```glsl
if (use_noise_map)     noise_bias     = (texture(noise_map, UV * noise_scale).r - 0.5) * noise_strength;
if (use_threshold_map) threshold_bias =  texture(threshold_map, UV * threshold_map_scale).r - 0.5;
float centered = clamp(wrapped - light_threshold - diffuse_threshold_offset + 0.5 + noise_bias + threshold_bias, 0.0, 1.0);
```

- **Noise** — the red channel, recentered to [-0.5, 0.5] and scaled by `noise_strength`
  (default **0.04**, range 0.0–0.25), jitters the band edge: straight toon seams become
  organic, hand-drawn wobbles. The band interior stays flat. Must be **tileable** (the map
  repeats across the surface) — baked with the 4D-noise trick so opposite edges match.
- **Threshold** — the red channel, recentered to [-0.5, 0.5] (**fixed magnitude — there is
  no `threshold_strength` uniform**; the map's own contrast is the control), shifts the
  shadow boundary per-pixel. Derived from AO: darker AO (deeper crease) → negative bias →
  shadow reached earlier → creases self-shade. "Free" spatial shadow variation from baked
  geometry.

The 1D lighting **ramp** is a *different* mechanism in `toon_ramp.gdshader`, not a
mk_toon_lite slot — see its own lesson (ramp band textures).

## Color space (important)

Both maps are **Non-Color** data (control signals, not sRGB imagery). The noise map is
generated Non-Color; the threshold map is derived from the ARM texture read as Non-Color.
Pin it explicitly — an sRGB decode would gamma-distort the control values and shift where
bands fall.

## Validation

- **Tier-1 (sidecar oracle):** `python tools/control-maps-oracle.py` — stdlib, reads the
  sidecar, asserts noise is 256×256 Non-Color and tileable and threshold tracks AO.
- **Tier-1 (drift check):** `python tools/control-maps-drift.py` — Pillow, re-measures the
  committed PNGs and confirms they still match the sidecar (catches hand-edits).
- **Tier-2:** `blender -b --python control_maps.py -- --check`.
- **Tier-3:** apply the maps to `mk_toon_lite` in the Godot test-scene and confirm the
  visible before/after effect (noise wobbles band edges; threshold deepens crease shadow).
