---
domain: godot-asset-pipeline
description: "Get 3D assets in and out of Godot — Godot's import mechanics: the happy-path first import, format decision, sidecars & reimport, name-suffix hints, LOD, rigged meshes/skeletons, and round-trip hygiene"
depth: 0
parent: null
leads_to: [godot-3d-animation]
---

# Godot Asset Pipeline — Getting 3D In and Out of Godot

## Orientation

This track teaches Godot's side of the 3D asset pipeline: how a model authored in a DCC tool
(Blender, etc.) becomes a running, correct Godot scene — and, when needed, how it comes back out. It
is deliberately Godot-import-*mechanics*-specific: the glTF standard itself (anatomy, the export
spec, skins) lives in the engine-agnostic `gltf-format` track, which this one consumes. The track is
built happy-path-first: topic 1 is the pure win — one model in, rendered, zero decisions — and every
later topic takes that standing win and widens it to one harder case (formats, version control,
collision, performance, rigging, round-trip), always landing back at a working result. Assets are
CC0 (Kenney); the source→glTF path is real end-to-end via the `make-blend` / `export-godot-glb`
tools.

## Topics

### first-import-happy-path
- **id:** 01M1Y84DVVEAZXWJKH6X3DSC49
- **title:** First Import — The Happy Path
- **why:** The pure early win: drop one neutral prop into Godot and see it render, correctly, with zero decisions. Establishes the one thing beginners trip on — import ≠ instance (Godot imports a copy into its own format; it appears in the game only once you drag it into the scene tree). Every later topic builds on this standing success.
- **scope:** substantial
- **prereqs:** []
- **lesson_file:** 01-first-import-happy-path.html

### format-decision-and-import-verify
- **id:** 01M1Y84DVV579KX00T4MXXWFA4
- **title:** Format Decision & Import Verify
- **why:** From the win: "but what about FBX / .blend / OBJ, and why did one come in wrong?" The format decision for Godot (glTF recommended, FBX via ufbx, .blend direct, OBJ/DAE limits) plus the Blender export prep (backface culling, normals, origin) that makes an import correct on purpose. Builds in prose on gltf-format's anatomy + engine-import topics.
- **scope:** substantial
- **prereqs:** [first-import-happy-path]
- **lesson_file:** 02-format-decision-and-import-verify.html

### import-process-and-sidecars
- **id:** 01M1Y84DVVH9Q6R0XT575K96BB
- **title:** Import Process & Sidecars
- **why:** From a working prop: "I edited the source and nothing updated / I committed the wrong files / a teammate's checkout broke." What import generates — the .import sidecar (commit it) vs the .godot/imported cache (don't) — UID, auto-reimport on source change, and ResourceLoader vs FileAccess. Lands back at the same prop, now safe to iterate on and share.
- **scope:** substantial
- **prereqs:** [format-decision-and-import-verify]
- **lesson_file:** 03-import-process-and-sidecars.html

### import-dock-and-name-suffixes
- **id:** 01M1Y84DVVBPTBD56KK38H7E5C
- **title:** Import Dock & Name Suffixes
- **why:** From a working visual prop: "it's just a mesh — it needs collision, or a modeling-only helper needs stripping." The three customization interfaces plus the name-suffix vocabulary by asset role (-col/-convcol/-colonly, -occ, -navmesh, -noimp, -rigid, -loop). Decision callout: triangle-vs-convex-vs-primitive collision, with OMI glTF-physics as an alternative. Lands at a game object that still renders.
- **scope:** deep
- **prereqs:** [import-process-and-sidecars]
- **lesson_file:** 04-import-dock-and-name-suffixes.html

### lod-and-import-optimization
- **id:** 01M1Y84DVVSPZ33ZE8PBQDQ1BV
- **title:** LOD & Import Optimization
- **why:** From a working game object: "fill a scene with it and the framerate tanks." Automatic mesh-LOD (meshoptimizer) on import, threshold/bias, HLOD visibility ranges, occlusion, and collision-shape performance. Decision callout: LOD-or-not and which collision shape, by asset role. Lands at the same object, performant at scale.
- **scope:** substantial
- **prereqs:** [import-dock-and-name-suffixes]
- **lesson_file:** 05-lod-and-import-optimization.html

### rigged-meshes-and-skeletons
- **id:** 01M1Y84DVVACKGVT23AEXS43N2
- **title:** Rigged Meshes & Skeletons
- **why:** From clean static imports: "an animated mesh breaks the static rules — wrong shading, broken deformation." Godot's skeleton/BoneMap/retarget mechanics — rest-pose export, the Export-Deform-Bones-Only gotcha, SkeletonProfileHumanoid, Rest Fixer. The skin/inverse-bind why lives in gltf-format. Lands at a rigged mesh that imports and animates correctly.
- **scope:** deep
- **prereqs:** [import-dock-and-name-suffixes]
- **soft_prereqs:** [import-process-and-sidecars]
- **lesson_file:** 06-rigged-meshes-and-skeletons.html

### reimport-and-round-trip-hygiene
- **id:** 01M1Y84DVVA9AT98SZHJ7MB9EJ
- **title:** Reimport & Round-Trip Hygiene
- **why:** From "can get assets in": "the source keeps changing, and sometimes I need it back out." The iterate loop, reimport-multiple, changing importer, the reverse direction (exporting a Godot scene to glTF via GLTFDocument) and its limits, and UID stability. Decision callout: .blend-direct vs committed-glTF team tradeoff. Lands at a mature round-trip.
- **scope:** substantial
- **prereqs:** [import-process-and-sidecars]
- **soft_prereqs:** [rigged-meshes-and-skeletons]
- **lesson_file:** 07-reimport-and-round-trip-hygiene.html
