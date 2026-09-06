# Code Files — Lesson 04: Materials & Textures

The engine-agnostic companion to the lesson. glTF's material is a small, fixed JSON object; the one
thing the file *can't* tell an engine is the transfer function (sRGB vs linear) of each texture — that
is defined by the **slot** referencing the image (spec §3.6.3), not by the image bytes. These files make
that concrete on a real asset.

## Files

| File | Purpose |
|------|---------|
| `make_cube_orm_glb.py` | Generate `cube_orm.glb` (stdlib only — no Blender, no Pillow): a cube whose material uses a base-color image (sRGB) plus an ORM image (linear, R=occlusion/G=roughness/B=metalness) shared by the metallic-roughness and occlusion slots, plus a linear normal image. A real both-color-families asset. |
| `cube_orm.glb` | The generated fixture (checked in so the lesson validates on a fresh clone). |
| `check_material_colorspace.py` | Parse a `.glb`/`.gltf`, print the per-material slot→color-space table, and assert no image is used across an sRGB and a linear slot. |

## Run it

```bash
python make_cube_orm_glb.py         # regenerate cube_orm.glb

python check_material_colorspace.py cube_orm.glb
# Parsed cube_orm.glb:
#   CubeORM:
#     baseColorTexture           sRGB    → image 0
#     normalTexture              linear  → image 2
#     metallicRoughnessTexture   linear  → image 1
#     occlusionTexture           linear  → image 1
#
# check_material_colorspace: every image stays within one color-space family; no conflict.
# (exit 0)

python check_material_colorspace.py --json cube_orm.glb   # structured {status, metrics, errors}
```

Exit codes: `0` = no color-space conflict, `1` = an image crosses families, `2` = not a glTF/GLB.

## The rule

| glTF slot | Color space | Why |
|-----------|-------------|-----|
| `baseColorTexture`, `emissiveTexture` | **sRGB** | Color — must be sRGB-decoded to linear before lighting |
| `metallicRoughnessTexture`, `normalTexture`, `occlusionTexture` | **linear** | Data (roughness/metalness, tangent-space vectors, occlusion) — used as-is |

glTF has **no per-slot color-space flag**. The family is implied by the slot name — so the file can't
tell the engine, and a mistake is silent (no error, just subtly wrong output). The oracle's only genuine
failure is an image reused across both families (the engine can't decode the same bytes both ways).

## Validation

- Both `.py` files are syntax-gated by `tools/check-lesson-code.py` (`python -m py_compile`) — they ship
  as downloadable `data-file` blocks in the lesson, so they're discovered and compiled in `mise run verify`.
- `cube_orm.glb` is validated by the domain oracle `tools/gltf-format-oracle.py` (structural integrity +
  the color-space slot-conflict assertion) in `mise run verify`.
- Claims cited against the Khronos glTF 2.0 specification: §3.6.3 (ignore embedded colorspace; transfer
  function defined by the referencing object), §5.19–5.22 (per-slot color spaces, ORM channel packing).
