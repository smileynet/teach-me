# Code Files — Lesson 01: glTF Anatomy & the Standard

Downloadable artifacts for the `gltf-format` domain, lesson 01. These are the files the
lesson walks through — a minimal-but-complete glTF asset in both container forms, plus a
stdlib parser that proves the object model on a real file.

## Files

| File | Purpose |
|------|---------|
| `triangle.gltf` | The canonical Khronos minimal triangle — one indexed triangle, JSON + an embedded base64 `data:` buffer. The `.gltf` (text) container form. |
| `triangle.glb` | The same asset in the `.glb` (binary) container form: a 12-byte header + a JSON chunk + a BIN chunk holding the 44 bytes of geometry. Generated from `triangle.gltf`. |
| `read_glb.py` | A parser written with the Python **standard library only** (`struct` + `json`, no third-party deps). Parses either container form, prints the object graph, and **asserts** the structural contracts the lesson teaches. |

## Run it

```bash
python read_glb.py triangle.glb
python read_glb.py triangle.gltf
```

Expected: the object-graph summary (1 scene → 1 node → 1 mesh; 2 accessors → 2 bufferViews
→ 1 buffer) followed by `read_glb: all structural contracts hold.` Exit code 0.

## What the 44 bytes are

The buffer holds, little-endian:

| Offset | Bytes | Meaning |
|--------|-------|---------|
| 0 | `00 00  01 00  02 00` | 3 × `uint16` indices → `(0, 1, 2)` |
| 6 | `00 00` | 2 padding bytes (align the floats to a 4-byte boundary at offset 8) |
| 8 | 36 bytes | 9 × `float32` positions → `(0,0,0) (1,0,0) (0,1,0)` |

The accessor for the positions reads `VEC3 × count 3` → element size `4 bytes × 3 = 12`,
`12 × 3 = 36` = the bufferView's `byteLength`. The numbers close — that's the whole point.

## Validation

`triangle.gltf` and `triangle.glb` are checked by `tools/gltf-format-oracle.py` (in
`mise run verify`): magic/version, chunk layout, `asset.version == "2.0"`, and
accessor → bufferView referential integrity. `read_glb.py` is syntax-checked by
`tools/check-lesson-code.py` (py_compile). Source: Khronos glTF 2.0 spec + glTF-Tutorials.
