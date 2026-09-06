# Code Files — Lesson 02: Authoring & Blender Export

Downloadable artifacts for the `gltf-format` domain, lesson 02. The lesson teaches what survives a
DCC → glTF export; these files make the "clean export" concrete — a cube with a
`pbrMetallicRoughness` material + a base-color texture, buildable two ways (stdlib or Blender) plus
the settings card.

## Files

| File | Purpose |
|------|---------|
| `cube_metalrough.glb` | The committed artifact: a cube with a metal-rough material + embedded base-color PNG. The "clean export" the lesson teaches. Validates on a fresh clone with no Blender. |
| `make_cube_glb.py` | Generates `cube_metalrough.glb` with the Python **standard library only** (`struct`+`json`+`zlib` — the PNG too). No Blender, no Pillow. Run: `python make_cube_glb.py`. |
| `export_cube.py` | The **Blender (bpy) source** for the same asset — a Principled BSDF wired in the glTF-native layout, exported with the game-ready settings. Reproducible source; NOT committed as a `.blend`. |
| `export_notes.md` | The game-ready Blender glTF export-settings card (every setting + why + failure-if-wrong), sourced from the Blender manual. |

## Run / reproduce

```bash
# stdlib path (always works):
python make_cube_glb.py            # → cube_metalrough.glb

# Blender path (needs Blender):
blender -b --python-exit-code 1 --python export_cube.py -- --check       # assert the node graph
blender -b --python-exit-code 1 --python export_cube.py -- --bake .      # build + export the .glb
```

## Validation

- `cube_metalrough.glb` is gated by `tools/gltf-format-oracle.py` in `mise run verify` — asserting
  glTF-2.0 structure **and** (via the material-channel check) that `pbrMetallicRoughness` +
  `baseColorTexture` are present. `make_cube_glb.py` + `export_cube.py` are syntax-checked by
  `tools/check-lesson-code.py`.
- `export_cube.py`'s `--check` is an opt-in Tier-2 gate (real Blender); it SKIPs where Blender is
  absent. Not part of core `verify`.

Source: Blender manual glTF exporter (`.references/blender-manual/manual/addons/scene_gltf2.rst`) +
KhronosGroup/glTF-Blender-IO.
