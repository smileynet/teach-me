---
id: "298"
title: "Topic: navigation-click-to-move (NavigationAgent3D pathfollowing + the wall contract)"
status: open
blocked_by: ["297", "300"]
priority: medium
validation_criteria:
  - "Lesson teaches NavigationRegion3D bake, NavigationAgent3D get_next_path_position, arrive-ramp + step-clamp, nav-is-independent-of-physics wall contract, input_ray_pickable"
  - "Runnable artifact: click_to_move_example.gd + scene, headless-import validated"
tags: ["content"]
---

# Topic: navigation-click-to-move (NavigationAgent3D pathfollowing + the wall contract)

Teach moving a character by clicking a destination: bake a navmesh, follow the path with
`NavigationAgent3D`, and stop cleanly on the target. Applies the movement math from #300.

> **Prereqs:** #297 (a skinned, animated character to move), #300 (the lerp/acceleration
> math), and `0015-physics-and-collision` (CharacterBody3D + move_and_slide, already
> taught). NavigationAgent3D click-to-move is the natural step above the movement primitive.

## Source

- `~/code/pnw-mystical-helper/design/examples/click_to_move.md` + `click_to_move_example.gd`
  — the worked design (arrive-ramp, step-clamp, the wall contract), all L4-cited, verified
  2026-09-05.

## What to teach

- **The path-follow model:** `NavigationAgent3D` is a *helper* — it never moves the body.
  Each frame read `get_next_path_position()` and move the body yourself.
- **Land on target, no oscillation** — two independent fixes: scene-side
  `target_desired_distance >= movement_speed / physics_ticks`; script-side arrive-ramp +
  step-clamp + zero-velocity-on-finish (the math is #300; here it's applied).
- **The wall contract (nav ⊥ physics):** walls must be handled in BOTH systems — bake into
  `NavigationRegion3D` (routes around) AND a `StaticBody3D` collider (stops the body). They
  don't talk to each other.
- **The #1 gotchas:** `input_ray_pickable = false` on walls (else pick ray hits them first);
  `NavigationMesh.agent_radius` ≈ capsule radius (else corner-clipping); snap clicks to the
  mesh with `NavigationServer3D.map_get_closest_point`.
- **Facing:** `Basis.looking_at` (−Z forward) + `Basis.slerp`, Y zeroed for yaw-only.
- **Forward pointer:** moving obstacles need the `velocity_computed` avoidance callback —
  static walls never do (out of scope; note it).

## Runnable artifact (ADR-0010)

`click_to_move_example.gd` + a scene with a baked navmesh + a wall — click to move, routes
around the wall, stops on the point. `godot --headless --import --quit` + `.gd`
compile-check. Downloadable final at `reference/code/navigation-click-to-move/`.

## Acceptance criteria

- [ ] Lesson teaches path-follow model, arrive/no-oscillation (both fixes), the wall contract, and the three gotchas (input_ray_pickable, agent_radius, map_get_closest_point)
- [ ] Diff-style or narrative-framed code building up click_to_move_example.gd (visual-teaching.md)
- [ ] Runnable artifact: scene + script, routes around a wall + stops on target, headless-import + compile validated; downloadable final under reference/code/
- [ ] Applies (does not re-derive) the #300 math; cross-links to #300
- [ ] Cites Godot nav docs + Reynolds steering paper
- [ ] `mise run verify` + check-topic-completeness pass; MAP.md gets lesson_file on completion

## Notes

- Nav-independent-of-physics is the mental model that prevents the most time-wasting bugs.
