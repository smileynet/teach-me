---
id: "296"
title: "Topic: animation-tree-state-machines (BlendSpace1D locomotion + travel() actions)"
status: open
blocked_by: ["295"]
priority: medium
validation_criteria:
  - "Lesson teaches AnimationPlayer->AnimationTree->AnimationNodeStateMachine, BlendSpace1D idle/walk/run, travel() action states, callback_mode=PHYSICS"
  - "Runnable artifact: animation_test_skin.gd + scene validated by godot --headless --import"
tags: ["content"]
---

# Topic: animation-tree-state-machines (BlendSpace1D locomotion + travel() actions)

Wire the imported clips into a driveable animation graph: merge the libraries, build an
`AnimationNodeStateMachine`, blend idle→walk→run, and fire one-shot actions. This is the
canonical home for AnimationTree in teach-me (godot-gamedev's `animation-and-audio` stays
2D/AnimationPlayer-focused — coordinate, don't duplicate).

> **Prereqs:** #295 (exported clips to merge).

## Source

`pipeline_guide.md` §3 + `guide_sources.md` §3; `examples/animation_test.md` +
`animation_test_skin.gd` (the ready-made final-state artifact, patterned on
godot_node_essentials AstronautSkin3D). All L4-cited, verified 2026-09-05.

## What to teach

- **Merge libraries:** each clip file imported as an `AnimationLibrary` → Manage
  Animations → Load/Add Library onto ONE `AnimationPlayer`; Make Unique → Save `.tres`.
- **The runtime chain:** `AnimationPlayer` → `AnimationTree` (`anim_player`, `active=true`,
  `callback_mode = PHYSICS`) → `tree_root = AnimationNodeStateMachine`.
- **Locomotion:** a nested `AnimationNodeBlendSpace1D` steered by one float
  (`parameters/Move/blend_position`) — idle 0 → walk 1 → run 2.
- **Actions:** dedicated states with **At-End** transitions back to Move, fired with
  `playback.travel("Attack")`. Cache `_playback = tree["parameters/playback"]`.
- **The skin/controller split:** a *skin* node owns the AnimationTree and exposes intent
  (`set_speed()`, `attack()`, `jump()`, `current_state()`); the controller never touches
  `parameters/` — this is what lets #298's controller drive it. Advance Condition (bool) vs
  Advance Expression (data-driven) vs `travel()` (event-driven).

## Runnable artifact (ADR-0010)

`animation_test_skin.gd` + an `animation_test` scene (character + AnimationTree +
DebugUI slider/buttons). The 7 acceptance checks in `animation_test.md` are the visual
proof; headless: `callback_mode = MANUAL`, `advance(delta)`, assert `get_current_node()`.
`godot --headless --import` + `.gd` compile. Downloadable final under
`reference/code/animation-tree-state-machines/`.

## Acceptance criteria

- [ ] Lesson teaches library merge, the AnimationPlayer→AnimationTree→StateMachine chain, BlendSpace1D locomotion, travel() action states, the IDLE-vs-PHYSICS callback_mode tradeoff, and the skin/controller split
- [ ] Runnable artifact: animation_test_skin.gd + scene, idle/walk/run blend + attack/jump actions, headless-import + compile validated; downloadable final under reference/code/
- [ ] Coordinated with godot-gamedev animation-and-audio to avoid duplication (this is the canonical AnimationTree home)
- [ ] Cites AnimationTree/StateMachine/BlendSpace1D Godot docs
- [ ] `mise run verify` + check-topic-completeness pass; MAP.md gets lesson_file on completion

## Research-backed content notes (from #293 dispatch — see `.scratch/research/char-animationtree.md`)

- **`callback_mode_process = PHYSICS` is a TRADEOFF, not a default.** It syncs animation with
  `move_and_slide()`, BUT **open bug #104198**: it makes *skeletal* animation choppy under
  physics interpolation. Teach the choice — PHYSICS to track physics movement; IDLE for
  smooth skeletal visuals — as a Decision callout, not a blanket prescription. `[L6 — #104198]`
- **`travel()` silently teleports on unconnected states** → at low FPS the per-`_physics_process`
  `travel()` calls out-race a one-shot `travel("Attack")`, and transitions "randomly" drop.
  Fix: connect states properly (or `start()` to force). Maintainer-diagnosed, Godot 4.3.
- **The SM must be `start()`-ed before `travel()`** (else null); fetch playback once via the
  correct nested `parameters/…/playback` path.
- **Prefer Advance Expression over Advance Condition** — Condition can't express negation
  (`!x` never fires); Expression needs the Advance Expression Base Node set + is case-sensitive.
- **Sync Mode enum** (None/Independent/Cyclic Mutable/Cyclic Constant): Cyclic Mutable is ideal
  for walk/run loop phase alignment. Verify the exact minor version where the 4-value enum
  landed against the target Godot before teaching cyclic modes (open Q).

## Notes

- The skin/controller split is the seam #297 (skin swap) and #299 (assembly) build on.
