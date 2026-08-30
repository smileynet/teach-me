# Bake & Export — code files

Downloadable artifacts for lesson 0019 (Emit Bake & glTF Export — Blender to Godot).

## Files

| File | Purpose |
|------|---------|
| `bake_export.py` | Blender script that chains Posterize RGB (0016) → Palette Snap B (0017) → Cycles **Emit** bake of the Barrel_01 albedo → **glTF export** (`Barrel_01_toon.glb`). Writes `bake-export-sidecar.json`. Also runs a Tier-2 `--check`. |
| `Barrel_01_toon_albedo.png` | The baked toon-prepped albedo (1024×1024, sRGB). |
| `Barrel_01_toon.glb` | The exported mesh + material (albedo only; no lights, cameras, or control maps). |
| `bake-export-sidecar.json` | Bake/export facts the Tier-1 oracle asserts. |

## Setup (headless)

Bake the albedo, export the glTF, write the sidecar:

```
blender -b --python bake_export.py -- --bake library/godot-gamedev/reference/code/bake-and-export
```

Validate the bake/export setup (Tier-2 gate, part of `mise run verify:blender`):

```
blender -b --python bake_export.py -- --check
```

## Why Emit (the key concept)

A Combined/Diffuse bake bakes **scene lighting into the texture**. Under Godot's dynamic
toon shader that produces *double* shadows (baked + live). **Emit** captures what the
material outputs *before* lighting touches it — the one bake type safe for dynamic toon
shading. `bake_export.py` wires the prep chain into an **Emission** shader and bakes
`type="EMIT"`.

## Why the glTF is albedo-only (the gotcha)

glTF color space is **slot-driven**, not a per-image flag. Godot imports a texture in the
`baseColorTexture` slot as **sRGB** and one in `normalTexture` as **linear** — automatically.
But a **control/data map** (the noise/threshold from lesson 0018) has no correct glTF slot:
route it through `baseColorTexture` and Godot sRGB-decodes it, corrupting the control values.
And a `.glb`-embedded texture has no separate `.import` file to fix the color space later.

So this export contains the **albedo only**. The control maps ship as standalone Non-Color
PNGs (`reference/code/toon-control-maps/toon_noise.png`, `toon_threshold.png`) and are wired
into the Godot material separately. `mk_toon_lite`/`configurable_banding` sample them directly.

## Color space

- Baked albedo → **sRGB** (color data). Godot's glTF importer flags `baseColorTexture` sRGB
  automatically — no manual fix needed.
- Control maps → **Non-Color** (data). Kept out of the glTF precisely so they aren't
  sRGB-decoded.

## Validation

- **Tier-1** `python tools/bake-export-oracle.py` — stdlib; asserts albedo sRGB 1K, glTF
  excludes lights/cameras, control maps not embedded.
- **Tier-2** `mise run verify:blender` (runs `bake_export.py --check`).
- **Tier-3a** `godot --headless --editor --import --quit` on the `.glb` → imports clean;
  inspect the material's albedo texture flags (sRGB).
- **Tier-3b** (manual) visual before/after under `configurable_banding` (raw PBR vs baked).
