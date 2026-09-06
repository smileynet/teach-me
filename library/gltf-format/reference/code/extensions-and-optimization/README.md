# Code Files — Lesson 06: Extensions & Optimization

The engine-agnostic companions to the track's capstone. glTF grows through extensions, and one honest
split governs everything: `extensionsUsed` (present — a viewer MAY ignore) vs `extensionsRequired` (a
viewer MUST understand it, or per the spec SHOULD NOT load the asset). The single decision behind the
split: *does the core still render without this extension?* — no ⇒ required, yes ⇒ used-only.

## Files

| File | Purpose |
|------|---------|
| `check_extensions.py` | Parse a `.glb`/`.gltf`, print a per-extension table (class / required? / has-fallback?), and assert the contract: `extensionsRequired ⊆ extensionsUsed`; a compression extension used-but-not-required is an ERROR; a material extension marked required is a NOTE. |
| `make_required_ext_glb.py` | Generate `required_ext.glb` (stdlib): a triangle that declares `EXT_meshopt_compression` in both `extensionsUsed` and `extensionsRequired` — the correct placement for a no-fallback compression extension. |
| `required_ext.glb` | The generated declare-only fixture (checked in so the lesson validates on a fresh clone). |

## Run it

```bash
python check_extensions.py truck-green.glb
#   extension                          class        required?  has-fallback?
#   KHR_materials_unlit                material     yes        yes
#   KHR_texture_transform              other        no         —
#   NOTE: 'KHR_materials_unlit' is a material extension marked required — core metal-rough is a
#         valid fallback, so this needlessly rejects non-supporting viewers (legal, but review)
#
# check_extensions: extensionsRequired ⊆ used and every no-fallback extension is required.
# (exit 0)

python make_required_ext_glb.py                  # regenerate required_ext.glb
python check_extensions.py required_ext.glb      # compression ext correctly required → exit 0
```

Exit codes: `0` = contract holds, `1` = a contract error (e.g. a compression ext left optional), `2` = not a glTF/GLB.

## The contract

| Question: does the core still render without it? | Placement | Example |
|---|---|---|
| **Yes** — there's a fallback | `extensionsUsed` only (MAY ignore) | `KHR_materials_*` (falls back to metal-rough), `KHR_texture_transform` |
| **No** — the bytes are unreadable without a decoder | `extensionsUsed` **and** `extensionsRequired` (MUST support) | `KHR_draco_mesh_compression`, `EXT_meshopt_compression`, `KHR_texture_basisu` |

## Optimize (Tier-2, not in core verify)

Real compression comes from **gltf-transform** (`npx @gltf-transform/cli optimize`), applied in order:
prune/dedup → quantize → Draco/meshopt → KTX2 → gzip/brotli last. Conformance is checked by the **Khronos
glTF Validator** (`npx gltf-validator`) — validate first, optimize second. Both are Node tools; this
lesson's stdlib artifacts teach the *contract*, and these are noted as the real toolchain (skip-if-no-node).

## Validation

- Both `.py` files are syntax-gated by `tools/check-lesson-code.py` (`python -m py_compile`).
- `required_ext.glb` is validated by the domain oracle `tools/gltf-format-oracle.py` — it exercises the
  `extensionsRequired ⊆ extensionsUsed` assert and the compression-must-be-required classification.
- Claims cited against the Khronos glTF 2.0 spec (§3.2, §3.12) and the extension registry READMEs
  (KHR_draco_mesh_compression, EXT_meshopt_compression, KHR_texture_basisu, KHR_materials_variants).
