---
id: "297"
title: "Topic: runtime-skin-and-accessories (material_override skin swap + BoneAttachment3D)"
status: done
blocked_by: ["296"]
priority: medium
validation_criteria:
  - "Lesson teaches material_override / set_shader_parameter skin swap (shared-UV fact), duplicate() gotcha, BoneAttachment3D accessories"
  - "Runnable artifact: a scene swapping a Kenney skin at runtime, headless-import validated"
tags: ["content"]
---

# Topic: runtime-skin-and-accessories (material_override skin swap + BoneAttachment3D)

Change a character's look at runtime without touching the mesh or the animation graph:
swap the skin texture, and attach props to bones.

> **Prereqs:** #296 (an animated character to re-skin).

## Source

`pipeline_guide.md` §4 + `guide_sources.md` §4; `examples/animation_test.md` (skin-swap
section). L4-cited, verified 2026-09-05.

## What to teach

- **Why one skin fits any model:** the 53 Kenney skins share ONE UV layout — a deliberate
  authoring fact, not something Godot provides. State this explicitly (it's the load-bearing
  assumption).
- **Where the skin lives / where the swap applies:** a `StandardMaterial3D` whose
  `albedo_texture` is the skin PNG, applied via `MeshInstance3D.material_override` (null to
  revert). The efficient PNW hand-painted path: a `ShaderMaterial` +
  `set_shader_parameter`.
- **The gotcha:** shared `.tres` materials mutate every instance — `duplicate()` per
  instance. Magenta = format mismatch.
- **Accessories:** 39 props attach via `BoneAttachment3D` to a named bone — rigid props that
  follow the skeleton without being skinned in.

## Runnable artifact (ADR-0010)

A scene swapping between ≥2 Kenney skins at runtime (button or timer) + one accessory
bone-attached. `godot --headless --import` + `.gd` compile. Downloadable final under
`reference/code/runtime-skin-and-accessories/`.

## Acceptance criteria

- [x] [SUPERSEDED] Lesson teaches the shared-UV fact, material_override vs ShaderMaterial swap, the duplicate() gotcha, and BoneAttachment3D accessories
- [x] [SUPERSEDED] Runnable artifact: runtime skin swap (≥2 skins) + a bone-attached accessory, headless-import + compile validated; downloadable final under reference/code/
- [x] [SUPERSEDED] Distinguished from godot-mktoon (that track teaches shader *authoring*; this is runtime *swapping*)
- [x] [SUPERSEDED] Cites BaseMaterial3D/MeshInstance3D/BoneAttachment3D Godot docs
- [x] [SUPERSEDED] `mise run verify` + check-topic-completeness pass; MAP.md gets lesson_file on completion

## Notes

- Runtime skin swap is entirely untaught today (only shader authoring exists) — no overlap.

## Resolution (2026-09-05 — superseded by 4-track restructure)

Superseded by the godot-3d-animation track (character-authoring-skins-and-accessories topic). Scope: .scratch/tracks/3d-animation.md.
