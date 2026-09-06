---
id: "314"
title: "Topic: animation-skins-and-morphs (skins/inverse-bind-matrices; samplers/channels; morph targets)"
status: open
blocked_by: ["310"]
priority: medium
validation_criteria:
  - "Lesson teaches skins (joints, inverse-bind-matrices = the WHY behind rest-pose + Export-Deform-Bones-Only), animation channels/samplers, interpolation (LINEAR/STEP/CUBICSPLINE), morph targets"
  - "Runnable artifact: oracle asserting skin IBM (MAT4/FLOAT/count>=joints) + morph weights==targets on a real skinned .glb (Wizard.glb); leads_to godot-3d-animation"
tags: ["content"]
---

# Topic: animation-skins-and-morphs (skins/inverse-bind-matrices; samplers/channels; morph targets)

Where the spec's subtlety lives — the skin/inverse-bind-matrix model is the *why* behind the
rest-pose and Export-Deform-Bones-Only gotchas that bite in every engine.

> **Prereqs:** #310 (anatomy); soft #311 (export). **`leads_to: godot-3d-animation`** (feeds #306).

## Source

`.scratch/research/gltf-standard.md` (skins/animation section) + `.scratch/research/gltf-glb-stdlib-parse.md`
(IBM assertions); Khronos glTF 2.0 skin/animation spec.

## What to teach

- **Skins:** joints + **inverse-bind-matrices** (why they exist — transform mesh from model space
  into each joint's space); why a skinned mesh **must export in rest/bind pose** (the spec-level
  answer to Blender's "Export Deformation Bones Only" gotcha, #311).
- **Animation:** channels (target node + path: translation/rotation/scale/weights) + samplers
  (input/output accessors + interpolation); **LINEAR / STEP / CUBICSPLINE** modes.
- **Morph targets:** primitive `targets` + mesh `weights`; "blend shapes"/"shape keys" as the same
  thing across tools.

## Runnable artifact (ADR-0010)

Oracle assertion (already in `tools/gltf-format-oracle.py`, extend for this lesson) on a **real
skinned `.glb`** (`test-scene/assets/quaternius-characters/Wizard.glb` — 1 skin, 17 animations):
skin has `inverseBindMatrices` whose accessor is MAT4/FLOAT with count ≥ joints; morph weights ==
targets. Downloadable at `reference/code/gltf-format/animation-skins-and-morphs/`.

## Acceptance criteria

- [ ] Lesson teaches skins + inverse-bind-matrices (as the WHY behind rest-pose export), animation channels/samplers + interpolation modes, and morph targets
- [ ] Explicitly connects the IBM/rest-pose model back to #311's Export-Deform-Bones-Only gotcha
- [ ] Runnable artifact: oracle asserting skin IBM (MAT4/FLOAT/count>=joints) + morph consistency on a real skinned .glb (Wizard.glb)
- [ ] leads_to godot-3d-animation recorded; the skin data is what #306's AnimationPlayer/library work consumes
- [ ] Cites the Khronos glTF skin/animation spec
- [ ] `mise run verify` passes; MAP.md gets lesson_file on completion

## Notes

- The deepest topic (scope: deep). Feeds both #305 t5 (Godot retarget) and #306 (animation).
