---
id: "300"
title: "Topic: movement-math-lerp-acceleration (the math behind lerp / move_toward / arrive-ramp)"
status: open
blocked_by: ["293"]
priority: medium
validation_criteria:
  - "Lesson teaches the MATH fundamentals: linear interpolation, move_toward vs lerp (fixed-step vs asymptotic), acceleration/arrive-ramp, forward-Euler overshoot + step-clamp, stopping-distance formula"
  - "Grounded in click_to_move math; runnable artifact demonstrates each concept (headless or Playwright-checkable)"
tags: ["content"]
---

> **Prereqs:** 0002-gdscript-fundamentals (needs #293 domain scaffold). This is the
> conceptual prereq for `navigation-click-to-move` (#298).

# Topic: movement-math-lerp-acceleration (the math behind lerp / move_toward / arrive-ramp)

Teach the **math fundamentals** underneath the movement code — so the learner understands
*why* click-to-move works, not just how to copy the script. This is the conceptual
foundation for `navigation-click-to-move` (#298): that lesson applies these formulas; this
one derives them. Requested explicitly so the implementation lessons rest on understood
fundamentals rather than pattern-matching.

## Source

- `~/code/pnw-mystical-helper/design/examples/click_to_move.md` — the worked movement math,
  with L4 Godot citations + Craig Reynolds' steering paper (red3d.com/cwr/steer/gdc99).
- `click_to_move_example.gd` — the ready-made final-state artifact these formulas produce.

## What to teach (the math, each tied to its code use)

1. **Linear interpolation (`lerp`).** `lerp(a, b, t) = a + (b - a) * t`. Why it's
   *asymptotic* (approaches but never reaches the target) and **frame-rate dependent** when
   used as `lerp(current, target, k * delta)` — the classic "eases in, never arrives" trap.
2. **`move_toward` vs `lerp`.** `move_toward(a, b, step)` moves a **fixed amount** and
   clamps at `b` — it actually *reaches* the target and never overshoots. The decision:
   `move_toward` when you must land exactly (stop on the clicked point); `lerp` for smooth
   asymptotic follow. This is the core "when to use which" of the lesson.
3. **Acceleration + the arrive-ramp.** Persistent `_current_speed` nudged each frame toward
   a desired speed = acceleration. Outside `arrive_distance`: full speed. Inside: ramp
   linearly to ~0 (`max_speed * distance / slowing_distance`) — Reynolds' "Arrive"
   behavior vs naive "Seek" (the moth-around-a-lightbulb oscillation).
4. **Forward-Euler integration + overshoot.** `position += velocity * delta` can step PAST
   the target in one frame, flip direction, and oscillate. The **step-clamp**: if this
   frame's step would overshoot, shrink it to land exactly. Why discrete time-stepping
   causes this and why the clamp fixes it.
5. **Stopping-distance formula.** `d = v² / (2a)` — sizing `arrive_distance` from
   `movement_speed` + `acceleration` (defaults 6 / 8 → ~2.25 m). Connect the kinematics to
   the tuning knob.

## Pedagogy (visual-teaching.md)

- Math is a strong candidate for **inline SVG diagrams**: a lerp-vs-move_toward convergence
  plot, the arrive-ramp speed-vs-distance graph, an overshoot/step-clamp before/after. Use
  `tools/draw-diagram.py` / hand SVG with `var(--svg-*)` colors.
- The in-lesson exercise tests the **decision** (near-transfer + misconception probe):
  "A colleague used `lerp(pos, target, 0.1)` to stop on a clicked point; the character
  never quite arrives and drifts. Why does lerp fail here, and what lands it exactly?"
- SR questions carry the formulas/gotchas (stopping-distance, frame-rate dependence).

## Runnable artifact (ADR-0010)

A small Godot scene/script (or a headless-runnable `.gd`) that demonstrates each concept —
e.g. a marker easing to a target three ways (lerp, move_toward, arrive-ramp) so the
difference is observable. Validated by `godot --headless --import --quit` + `.gd`
compile-check. Downloadable final at `reference/code/movement-math-lerp-acceleration/`.

## Acceptance criteria

- [ ] Lesson derives lerp, move_toward, acceleration/arrive-ramp, Euler overshoot + step-clamp, and the stopping-distance formula — each tied to its use in click-to-move
- [ ] "When to use which" decision callout: move_toward (land exactly) vs lerp (smooth follow)
- [ ] At least one inline SVG visualizing the math (var(--svg-*) themed, accessible)
- [ ] In-lesson exercise is a near-transfer misconception probe (why lerp fails to land)
- [ ] Runnable artifact demonstrating each ease, headless-import + compile validated; downloadable final under reference/code/
- [ ] Cites Godot docs (move_toward, CharacterBody3D) + Reynolds steering paper
- [ ] `mise run verify` + check-topic-completeness pass; MAP.md gets lesson_file on completion

## Notes

- This is the "understand the fundamentals" ticket — keep the framing conceptual/derivational,
  not a code walkthrough. The application lives in #298.
