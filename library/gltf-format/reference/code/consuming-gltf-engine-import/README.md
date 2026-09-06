# Code Files — Lesson 03: Consuming glTF & Engine Import

The engine-agnostic companion to the lesson. An engine doesn't "open" a glTF — it *translates*
the file's object graph into its own scene-node types, once, on import. `map_to_nodes.py` makes
that translation concrete: it parses a real asset with the standard library alone and prints the
engine scene tree the importer would build, then asserts the mapping contract.

## Files

| File | Purpose |
|------|---------|
| `map_to_nodes.py` | Parse a `.glb`/`.gltf` (stdlib only), print the Godot scene-node tree it imports into, and assert the mapping's referential-integrity contract. Engine-agnostic — no Godot needed. |

## Run it

Run it on a rigged, animated character (a mesh + a skin + 17 animations → a rich mapping):

```bash
python map_to_nodes.py Wizard.glb
# Parsed Wizard.glb:
#   Engine scene the importer would build (Godot node types, one consumer of many):
#     Node3D            x25   (one per glTF node; scene root)
#     MeshInstance3D    x1    (nodes carrying a mesh)
#     Skeleton3D        x1    (one per skin, + a Skin resource)
#     StandardMaterial3D x7   (one per glTF material)
#     Camera3D          x0
#     AnimationPlayer   x1    (holds all 17 glTF animation(s))
#
# map_to_nodes: every glTF concept maps to an engine node; the mapping holds.
# (exit 0)

python map_to_nodes.py --json Wizard.glb   # structured {status, metrics, errors}
```

Exit codes: `0` = parsed + all mapping asserts hold, `1` = an assert failed, `2` = not a glTF/GLB.

## The mapping

The node names use Godot's vocabulary because Godot is the lesson's worked example — but the *shape*
(one engine node per glTF concept, keyed by index) is universal. Unity glTFast literally keys a
`Dictionary<uint, GameObject>` by glTF node index; three.js exposes `gltf.scene`; Babylon builds
`TransformNode`s. Same dictionary everywhere.

| glTF concept | Engine node (Godot) |
|--------------|---------------------|
| node with `mesh` | `MeshInstance3D` |
| `skin` | `Skeleton3D` + a `Skin` resource |
| `material` | `StandardMaterial3D` |
| `camera` | `Camera3D` |
| `light` (KHR_lights_punctual) | `DirectionalLight3D` / `OmniLight3D` / `SpotLight3D` |
| all `animation`s | one `AnimationPlayer` |

## Validation

- `map_to_nodes.py` is syntax-gated by `tools/check-lesson-code.py` (`python -m py_compile`) — it
  ships as a downloadable `data-file` block in the lesson, so it is discovered and compiled in
  `mise run verify`.
- Its assertions are a subset of the referential-integrity checks the domain oracle
  `tools/gltf-format-oracle.py` already runs on the committed fixtures.
- Node-mapping claims cited against the local Godot docs (`.references/godot-docs/classes/class_gltfdocument.rst`,
  `class_gltfstate.rst`, `class_gltflight.rst`) and the Khronos glTF 2.0 specification.
