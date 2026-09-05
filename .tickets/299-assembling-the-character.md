---
id: "299"
title: "Topic: assembling-the-character (wire controller + skin + nav into the Character scene)"
status: done
blocked_by: ["296", "297", "298"]
priority: medium
validation_criteria:
  - "Lesson wires CharacterBody3D controller feeding skin velocity.length() + travel() calls into the full Character scene"
  - "Runnable artifact: the complete assembled Character scene, headless-import validated"
tags: ["content"]
---

# Topic: assembling-the-character (wire controller + skin + nav into the Character scene)

The capstone: combine everything into one working Character — a click-to-move controller
that feeds the animation skin and wears a chosen skin. This is the domain's final product;
its artifact is the complete assembled scene.

> **Prereqs:** #296 (animation), #297 (skin), #298 (navigation) — all three seams meet here.

## Source

`pipeline_guide.md` "Putting it together — the Character scene"; the two example docs +
their `.gd` files.

## What to teach

- **The assembled scene:**
  ```
  Character (CharacterBody3D)        # the click-to-move controller (#298)
  ├─ <imported base model>           # MeshInstance3D + Skeleton3D (#294/#295)
  │   └─ AnimationPlayer              # clip libraries merged (#296)
  ├─ AnimationTree                    # state machine (#296)
  ├─ NavigationAgent3D                # path following (#298)
  ├─ CollisionShape3D
  └─ (skin script owns the AnimationTree; controller feeds intent)
  ```
- **The wiring contract:** each physics frame the controller sets a nav target + moves the
  body (#298), feeds the skin `velocity.length()` for the locomotion blend (#296), calls
  `attack()`/`jump()` on events, and the skin's texture is swapped for the chosen look
  (#297). The controller NEVER touches `parameters/` — the skin/controller split is what
  makes assembly clean.
- Everything is assembled in-engine from separately-imported pieces (ADR-0001).

## Runnable artifact (ADR-0010)

The complete Character scene: click to move, character walks/runs (speed-blended), routes
around walls, plays actions, wearing a swapped skin. `godot --headless --import` + `.gd`
compile; visual confirmation of the assembled behavior. Downloadable final under
`reference/code/assembling-the-character/`.

## Acceptance criteria

- [x] [SUPERSEDED] Lesson wires the controller + skin + nav into the full Character scene per pipeline_guide.md, teaching the intent-feeding contract (no direct parameters/ access)
- [x] [SUPERSEDED] Runnable artifact: complete Character scene (move + animate + skin), headless-import + compile validated; downloadable final under reference/code/
- [x] [SUPERSEDED] Explicitly integrates #296/#297/#298 (references, doesn't re-teach)
- [x] [SUPERSEDED] `mise run verify` + check-topic-completeness pass; MAP.md gets lesson_file on completion

## Notes

- Final lesson of the domain — its artifact is the complete product (ADR-0010).

## Resolution (2026-09-05 — superseded by 4-track restructure)

Superseded: the single-track 'assemble the character' capstone is gone. Each of the 4 tracks now has its own capstone (e.g. godot-3d-animation's character-authoring lesson is the animation-side assembly home). Scope docs: .scratch/tracks/*.md.
