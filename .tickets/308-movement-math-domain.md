---
id: "308"
title: "Set up movement-math domain (engine-agnostic fundamentals track: MAP + Python oracles + validation gate)"
status: open
blocked_by: []
priority: medium
validation_criteria:
  - "movement-math.MAP.md exists with 6 topics + prereq edges (passes check-maps-forest)"
  - "Pure-Python property-oracle artifacts validated by check-lesson-code.py (py_compile) in verify; optional Godot mirrors"
  - "Standalone depth-0, engine-agnostic; leads_to godot-3d-navigation (click-to-move applies this math)"
tags: ["content"]
---

# Set up movement-math domain (engine-agnostic fundamentals track: MAP + Python oracles + validation gate)

Stand up the standalone **`movement-math`** teaching domain — the engine-agnostic math
underneath *any* engine's `lerp` / `move_toward` / `SmoothDamp` / steering helpers:
interpolation, delta-time correctness, constant-speed motion, easing, Euler integration, and
steering/arrival. One of four focused tracks split from the retired `godot-3d-character-pipeline`
(#293, closed) — and the one the user specifically asked for ("the math behind lerp/
acceleration so I understand the fundamentals behind the implementations").

**Setup/scaffold + proposal only — NO lessons.** Full scope + sources + artifacts + open Qs:
**`.scratch/tracks/movement-math.md`**.

## Domain shape

```yaml
domain: movement-math
description: "The math under game movement — lerp, delta-time correctness, move_toward, easing, Euler integration, and steering/arrival, engine-agnostic"
depth: 0
parent: null
leads_to: [godot-3d-navigation]   # click-to-move APPLIES this math
```

Standalone depth-0, **engine-agnostic** (not a Godot domain). `leads_to` godot-3d-navigation
(that track's click-to-move applies the arrive-ramp/lerp taught here). Only external prereq is
general programming (gamedev `0002-gdscript-fundamentals` as a concrete anchor if desired).
Through-line: **desired state → error → correction → integrate over dt.**

## Topics + prereq spine (6, from `.scratch/tracks/movement-math.md`)

| # | slug | why (short) | prereqs |
|---|------|-------------|---------|
| 1 | `lerp-and-interpolation` | `a+t*(b-a)`, unlerp/remap; marching-t vs iterative smoothing | [] |
| 2 | `delta-time-and-frame-rate-independence` | why iterative lerp is fps-dependent; `lerp(a,b,1-pow(s,dt))` fix; fixed vs variable timestep | [1] |
| 3 | `move-toward-and-constant-speed` | fixed-step, never overshoots, arrives exactly; lerp-vs-move_toward decision | [1],[2] |
| 4 | `easing-and-tweening` | `lerp(a,b,ease(t))`; ease families; overshoot eases; needs marching-t | [1],[2] |
| 5 | `euler-integration-and-overshoot` | explicit vs semi-implicit Euler; overshoot/energy-gain; step-clamp/substep | [2],[3] |
| 6 | `steering-arrival-and-smooth-damp` | Reynolds seek/arrive-ramp, stopping-distance kinematics, critically-damped spring (capstone) | [3],[4],[5] |

Prereq edges: spine `1→2→3→5→6`; `4` branches off `2`; `6` is the convergence node
(`3,4,5→6`). All within-map.

## Runnable-artifact validation gate (ADR-0010) — different tier from the Godot tracks

**Pure-Python property oracles** (stdlib only), NOT Godot. Each lesson ships a `.py` at
`reference/code/movement-math/{slug}/` that runs a fixed loop, prints a structured result
(`{"status":"pass|fail","metrics":{…}}`, exit 0/1), and **asserts the taught property** —
validated by `tools/check-lesson-code.py` (`.py` → `py_compile`) in `mise run verify`. Headline
oracle `dt_damping.py` (L02): naive `lerp(a,b,r)` diverges across 30/60/120fps while the
pow-form converges. ASCII trajectory sparklines for visuals (no plotting dep). Optional minimal
Godot `.gd` mirrors (compile-check opt-in, shipped as reference not gated). This tier needs NO
Godot and runs in core verify — the cleanest validation of the four tracks.

## Acceptance criteria

- [ ] `movement-math.MAP.md` at `library/movement-math/maps/` with all 6 topics + prereq edges; ULIDs via `migrate_map_ids.py --apply`; passes `check-maps-forest.py`
- [ ] Pure-Python oracle artifact convention confirmed (structured JSON + exit code, `check-lesson-code.py` py_compile in verify); `leads_to godot-3d-navigation` edge set
- [ ] Standalone depth-0, engine-agnostic; external prereq (general programming / gamedev 0002) noted
- [ ] Provenance recorded (Reynolds red3d.com, gafferongames, Driscoll — design source `.scratch/tracks/movement-math.md`)
- [ ] The 5 open questions resolved or deferred (pure-Python-primary vs Godot-primary, plotting dep vs ASCII/SVG, rotation as 7th lesson vs separate track, accumulator depth in L06, splines/paths boundary)
- [ ] NO lessons generated — 6 topic tickets created after sign-off

## Notes

- Restructured + EXPANDED from #300 (closed superseded; was 1 topic, now a 6-topic track).
- Scope: `.scratch/tracks/movement-math.md`. The user's explicitly-requested fundamentals track.
