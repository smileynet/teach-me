# Blender → glTF export settings (game-ready) — reference card

The "minimal safe game export" preset for `File → Export → glTF 2.0`. Every row: the recommended
value + why + the failure mode if you get it wrong. Source: the Blender manual glTF exporter page
(`.references/blender-manual/manual/addons/scene_gltf2.rst`; published:
docs.blender.org/manual/en/latest/addons/import_export/scene_gltf2.html). **Game-export defaults
differ from Blender's UI defaults** — set these deliberately.

## Before you export (scene prep)

- **Apply Rotation & Scale** (`Ctrl+A`) on every object. Unapplied scale → wrong normals + bounding
  boxes in the viewer.
- Materials use **Principled BSDF** with **image textures** (or flat slider values) in the
  glTF-native channel layout — NOT procedural nodes (Noise/Voronoi are ignored on export).
- Base color / emissive images = sRGB; metal-rough / normal / occlusion images = **Non-Color**.

## Export dialog

| Section | Setting | Recommended | Why / failure if wrong |
|---------|---------|-------------|------------------------|
| Format | Format | **glTF Binary (.glb)** | One self-contained shipping file. Embedded (.gltf) is "least efficient." |
| Include | Limit to | **Selected Objects** (or Visible) | Scope filter — if *nothing* exports, this is usually the culprit. |
| Include | Cameras / Punctual Lights | off (game assets) | Baked cameras/lights fight the engine's own lighting. |
| Transform | **+Y Up** | **on** | Blender is Z-up, glTF is Y-up. Off → model loads rotated 90°/sideways (**#1 orientation bug**). |
| Data → Mesh | Apply Modifiers | **on** | The mesh you see isn't exported unless applied (armature/subsurf/mirror). |
| Data → Mesh | UVs / Normals / **Tangents** | **on** | Tangents needed for normal-mapped materials to light correctly downstream. |
| Data → Material | Materials | **Export** | `No Export` irreversibly **merges primitives** (loses slot info). |
| Data → Material | Images | **PNG** (or JPEG for web) | glTF requires PNG/JPEG; other formats auto-convert (slower). |
| Data → Compression | Draco / Meshopt | **off** unless the target loader supports it | Draco/Meshopt-on with a non-supporting loader is a **hard load failure**, not graceful degradation. |
| Data → Armature | Use Rest Position Armature | **on** | Exports the rest/bind pose as joint rest (rigged meshes must export in rest pose). |
| Data → Armature | Export Deformation Bones Only | **on** | Skips control/IK bones; smaller, cleaner skin. |
| Data → Skinning | Bone influences | **4** (or 8) | "Models may appear incorrectly with a value different to 4 or 8." |
| Animation | Mode | **Actions** | Each action → its own clip. **Unstashed actions silently do NOT export — stash/push-down to NLA.** |
| Animation | Sampling | **on** | "Do not sample animation can lead to wrong animation export." IK/constraints only survive as sampled keyframes. |

## The `KHR_materials_*` extension tier (viewer-dependent)

Non-default Principled inputs export as extensions the *consuming* viewer must support:
`KHR_materials_clearcoat / transmission / sheen / specular / volume / ior / anisotropy /
emissive_strength`, plus `KHR_materials_unlit`. Newer Blender also emits
`EXT_meshopt_compression`, `KHR_animation_pointer`, and `KHR_materials_dispersion`. A baseline glTF
viewer ignores extensions it doesn't understand (that's the graceful-degradation contract) — but
required extensions (`extensionsRequired`) it can't read will refuse to load.

_This card is the human counterpart to `make_cube_glb.py` (which builds the same clean layout with
the stdlib) and `export_cube.py` (which builds it in Blender)._
