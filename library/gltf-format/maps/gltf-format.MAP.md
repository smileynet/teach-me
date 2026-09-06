---
domain: gltf-format
description: "The glTF 2.0 open standard — JSON/binary anatomy, Blender export, engine import, PBR materials, skins & animation, and the extension/compression ecosystem, engine-agnostic"
generated: 2026-09-05
depth: 0
parent: null
leads_to: [godot-asset-pipeline, godot-3d-animation]
---

# glTF 2.0 — The Standard Under Every 3D Import

## Orientation

glTF is "the JPEG of 3D": a Khronos open standard for *delivering* runtime-ready 3D — a JSON scene graph plus binary geometry plus images — that Godot, Blender, three.js, Babylon, and Unity all speak. It is not an authoring format; it's the neutral exchange vessel between your DCC tool and your engine. This track teaches the standard itself — its anatomy, how a DCC exports it, how an engine imports it, its PBR material model, skins and animation, and the extension ecosystem — so that "why does my model look wrong across the round trip?" becomes a question you answer from the file, not guess at. It's deliberately engine-agnostic: the Godot specifics live in godot-asset-pipeline, which consumes this. Sources are the Khronos glTF 2.0 spec (ISO/IEC 12113:2022); sample assets are CC0.

## Topics

### gltf-anatomy-and-the-standard
- **id:** 01M1T33FPC4YTKKSXWH53N60PZ
- **title:** glTF Anatomy & the Standard
- **why:** Every later topic uses the node/mesh/accessor vocabulary — you can't reason about an export or import bug without the object model and the .glb container layout. Taught as a runnable minimal-complete file (a single indexed triangle) walked field-by-field, with the buffer→bufferView→accessor chain given its own weight.
- **scope:** deep
- **prereqs:** []
- **lesson_file:** 01-gltf-anatomy-and-the-standard.html

### authoring-and-blender-export
- **id:** 01M1T33FPCDS2WKNDKFFXGA5V0
- **title:** Authoring & Blender Export
- **why:** Export is where most "my model looks wrong" bugs are born — the spec's rules become concrete exporter actions, and the exporter silently drops anything not in a glTF-native layout (procedural nodes, arbitrary channel math).
- **scope:** substantial
- **prereqs:** [gltf-anatomy-and-the-standard]
- **lesson_file:** 02-authoring-and-blender-export.html

### consuming-gltf-engine-import
- **id:** 01M1T33FPC4J9RV8GM8H6GFDQC
- **title:** Consuming glTF — Engine Import
- **lesson_file:** 03-consuming-gltf-engine-import.html
- **why:** Bridges the standard to a real runtime (Godot as one consumer of many) without duplicating engine-specific mechanics — shows where engines honor vs diverge from the spec, and the "don't hand-edit imported data" contract.
- **scope:** substantial
- **prereqs:** [gltf-anatomy-and-the-standard]
- **leads_to:** [godot-asset-pipeline]

### materials-and-textures
- **id:** 01M1T33FPCNKMX0XXN715XJ7CT
- **title:** Materials & Textures
- **why:** Materials are the highest-fidelity-loss surface across the round trip, and sRGB-vs-linear color space per slot is the #1 silent bug. Covers the PBR metallic-roughness model, texture slots, ORM packing, and the KHR_materials_* extensions.
- **scope:** substantial
- **prereqs:** [gltf-anatomy-and-the-standard]

### animation-skins-and-morphs
- **id:** 01M1T33FPCSQ0QED2XH9HDPR9A
- **title:** Animation, Skins & Morphs
- **why:** Rigged/animated content is where the spec's subtlety lives — the skin/inverse-bind-matrix model is the answer to the rest-pose and Export-Deform-Bones-Only gotchas. Covers samplers/channels, interpolation modes, and morph targets.
- **scope:** deep
- **prereqs:** [gltf-anatomy-and-the-standard]
- **leads_to:** [godot-3d-animation]

### extensions-and-optimization
- **id:** 01M1T33FPCKCVXK5NMGDAR180Y
- **title:** Extensions & Optimization
- **why:** The ships-to-production layer — file size, GPU-ready textures, and how to extend the format (Draco, meshopt, KTX2, variants) without breaking baseline viewers. Closes with the Khronos glTF Validator and gltf-transform.
- **scope:** substantial
- **prereqs:** [gltf-anatomy-and-the-standard]
