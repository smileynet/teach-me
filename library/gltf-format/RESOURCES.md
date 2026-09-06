# Resources

Verified sources for the glTF 2.0 learning workspace (from the #309 research pass, 2026-09-05).

| Source | Trust | Notes |
|--------|-------|-------|
| [glTF 2.0 Specification (Khronos)](https://registry.khronos.org/glTF/specs/2.0/glTF-2.0.html) | L2:verified | The governing spec (ISO/IEC 12113:2022). Object model, GLB layout, PBR, skins, animation. |
| [KhronosGroup/glTF (GitHub)](https://github.com/KhronosGroup/glTF) | L4:verified | Spec repo + sample models + extension registry. |
| [KhronosGroup/glTF-Tutorials](https://github.com/KhronosGroup/glTF-Tutorials) | L4:established | The teaching exemplar — anatomy-first, minimal-complete-file, worked-example-then-detail. |
| [Blender glTF 2.0 exporter manual](https://docs.blender.org/manual/en/latest/addons/import_export/scene_gltf2.html) | L4:verified | Export dialog, +Y-up, animation modes. (Some version mirrors 403 to bots — GitHub repo is the fallback.) |
| [KhronosGroup/glTF-Blender-IO](https://github.com/KhronosGroup/glTF-Blender-IO) | L4:verified | The exporter source of truth (Principled BSDF → glTF mapping). |
| [Godot: Available 3D formats (4.7)](https://docs.godotengine.org/en/stable/tutorials/assets_pipeline/importing_3d_scenes/available_formats.html) | L4:verified | Godot import side — cited by the consuming-glTF facet (points to godot-asset-pipeline). |
| [Godot GLTFDocument class ref](https://docs.godotengine.org/en/stable/classes/class_gltfdocument.html) | L4:verified | GLTFDocument → GLTFState → node tree; runtime + editor import. |
| [Khronos glTF Validator](https://github.com/KhronosGroup/glTF-Validator) | L4:established | Reference conformance checker — optional Tier-2 cross-check (npm library + Node wrapper). |
| [gltf-transform CLI](https://gltf-transform.dev/) | L5:reported | inspect/optimize/draco/meshopt — for the extensions-and-optimization facet only. |
