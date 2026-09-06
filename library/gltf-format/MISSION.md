# Mission: Understand the glTF 2.0 file format

## Why

glTF is the neutral exchange format between DCC tools (Blender) and engines (Godot,
three.js, Babylon, Unity). Most "my model looks wrong after export/import" bugs are
really glTF-format bugs — wrong color space, dropped material channels, a skeleton that
didn't export in rest pose. Understanding the standard itself makes those bugs readable
from the file rather than guessed at, and the knowledge transfers across every engine.

## Success looks like

- Can read a `.glb`/`.gltf` and explain its object graph (scenes → nodes → meshes →
  accessors → bufferViews → buffers) to a colleague
- Can diagnose why an exported asset looks wrong by inspecting the file (color space,
  material channels, skin/rest-pose, coordinate convention)
- Can advise on format choices (`.glb` vs `.gltf`+bin, Draco/meshopt, KTX2) and which
  `KHR_`/`EXT_` extensions are safe to rely on

## Constraints

- Engine-agnostic — teaches the standard, not one engine's importer (Godot specifics
  live in the godot-asset-pipeline domain, which consumes this)
- glTF 2.0 core (ISO/IEC 12113:2022); extension coverage snapshotted at authoring time
- Validation via stdlib GLB/JSON property oracles (+ optional Khronos glTF Validator)
