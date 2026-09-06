# Code Files — Lesson 05: Animation, Skins & Morphs

The engine-agnostic companions to the lesson. A skinned mesh is stored once, in bind pose, and
re-posed through a matrix chain (`AnimatedPos = JointWorldMatrix · InverseBind · RestPos`); animation
drives joint transforms via channels + samplers; morph targets deform vertices by per-vertex deltas.
These files make each of those concrete on a real asset — no Godot, no Blender.

## Files

| File | Purpose |
|------|---------|
| `check_skin_animation.py` | Parse a rigged `.glb`/`.gltf`, print the skin + per-animation channel/sampler summary, and assert the contracts: skin IBM is MAT4/FLOAT/count≥joints, a skinned primitive has JOINTS_0+WEIGHTS_0, animation channels/samplers resolve, sampler input is a FLOAT SCALAR time accessor, interpolation ∈ {LINEAR, STEP, CUBICSPLINE}. |
| `make_tri_morph_glb.py` | Generate `morph_tri.glb` (stdlib only): a triangle with one morph target (a POSITION-delta lifting vertex 0) + `mesh.weights`. The minimal demonstration of morph deformation. |
| `morph_tri.glb` | The generated morph fixture (checked in so the lesson validates on a fresh clone). |

## Run it

```bash
python check_skin_animation.py Wizard.glb
# Parsed Wizard.glb:
#   skins: 1 (joints: [23])
#   animations: 17  channels: 1173  interpolation: LINEAR
#   morph targets present: False
#
# check_skin_animation: skin IBM + animation channels/samplers hold.
# (exit 0)

python make_tri_morph_glb.py            # regenerate morph_tri.glb
python check_skin_animation.py morph_tri.glb   # morph targets present: True
```

Exit codes: `0` = all contracts hold, `1` = a contract failed, `2` = not a glTF/GLB.

## The two deformations

| Kind | How it moves vertices | glTF data |
|------|-----------------------|-----------|
| **Skin** | Rigid joints re-pose shared geometry via the matrix chain | `skin.joints`, `inverseBindMatrices`, `JOINTS_0`/`WEIGHTS_0` |
| **Morph** | Per-vertex deltas blended by weights: `base + Σ weight[j]·target[j]` | `primitive.targets[]`, `mesh.weights` |

The inverse-bind-matrix only works if the geometry is in the **bind pose** the IBMs were computed for —
that is the spec-level reason a skinned mesh must export in rest pose (the "Export Deformation Bones Only"
/ apply-rest-pose gotcha).

## Validation

- Both `.py` files are syntax-gated by `tools/check-lesson-code.py` (`python -m py_compile`) — they ship
  as downloadable `data-file` blocks in the lesson, compiled in `mise run verify`.
- `morph_tri.glb` is validated by the domain oracle `tools/gltf-format-oracle.py` (it lights the oracle's
  morph `weights == targets` branch); the oracle also asserts skin IBM + animation channel/sampler
  integrity on the committed `Wizard.glb`.
- Claims cited against the Khronos glTF 2.0 spec (§3.7 skins, §5.5–5.8 animation, §3.7.2 morph targets)
  and the Khronos glTF skin tutorial.
