---
id: "328"
title: "godot-asset-pipeline topic 6: rigged-meshes-and-skeletons"
status: open
blocked_by: ["305", "326"]
validation_criteria:
  - "Lesson 06: from clean static imports → 'an animated mesh breaks the static rules' → Godot skeleton/BoneMap/retarget mechanics: rest-pose export, Export-Deform-Bones-Only gotcha, SkeletonProfileHumanoid, Rest Fixer. Skin/rest-pose WHY lives in gltf-format (prose link). Character-agnostic (generic rigged arm). Soft-prereq topic 3. Lands at a rigged mesh that imports+animates right"
  - "Runnable artifact (two-bone rigged .glb + looping clip + BoneMap) + asset:validate-gd L6 assertion (Skeleton3D+AnimationPlayer, loop_mode set, mesh not pre-deformed)"
  - "Reference doc + SR cards + glossary JSON; passes mise run verify"
tags: ["content"]
---

# godot-asset-pipeline topic 6: rigged-meshes-and-skeletons

## Context

Track spiral topic 6 (#305). win → complication → resolution → win. Prereq topic 4 (soft topic 3).
Shrunk post gltf-format split — the skin/inverse-bind/rest-pose *why* lives in gltf-format
`animation-skins-and-morphs`; this is the Godot-side mechanics. Design:
`.scratch/proposals/305-godot-asset-pipeline-setup.md`.

## What to build

- **Start from the win**: "You can import *static* assets cleanly (collision, LOD, all of it)."
- **Harder case**: "You bring in an *animated* mesh and the static rules break — wrong shading,
  broken deformation."
- **Resolve**: what changes with a skeleton — rest/T-pose export (not bone-deformed); the
  Export-Deform-Bones-Only gotcha; AnimationPlayer generation; `-loop` revisited; skeleton
  retargeting (BoneMap + SkeletonProfileHumanoid, Bone Renamer, Rest Fixer / Overwrite Axis).
  Character-agnostic — a generic two-bone rigged "arm", not a named character.
- **Land back**: a rigged mesh that imports and animates correctly.
- Prose link: builds on gltf-format `animation-skins-and-morphs`.

## Acceptance criteria

- [ ] Lesson `06-rigged-meshes-and-skeletons.html` in the spiral shape
- [ ] Runnable artifact (two-bone rigged `.glb` + looping clip + BoneMap) + `asset:validate-gd` L6 assertion (Skeleton3D+AnimationPlayer, `loop_mode` set, mesh not pre-deformed)
- [ ] Reference doc + SR cards + glossary JSON
- [ ] Passes `mise run verify`
