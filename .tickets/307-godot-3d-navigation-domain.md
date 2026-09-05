---
id: "307"
title: "Set up godot-3d-navigation domain (nav + point-and-click track: MAP + reference project + validation gate)"
status: open
blocked_by: []
priority: medium
validation_criteria:
  - "godot-3d-navigation.MAP.md exists with 6 topics + prereq edges (passes check-maps-forest)"
  - "Committed nav test-project + opt-in headless run validation (ADR-0010, nav-gd-run.py analogue)"
  - "Standalone depth-0; movement-math soft prereq wired; provenance recorded"
tags: ["content"]
---

# Set up godot-3d-navigation domain (nav + point-and-click track: MAP + reference project + validation gate)

Stand up the standalone **`godot-3d-navigation`** teaching domain — the whole 3D navigation
subsystem in Godot 4.x, with point-and-click movement as the capstone application: navmesh
baking → NavigationAgent3D path-following → click-to-destination → obstacles/avoidance →
layers/links → runtime rebake. One of four focused tracks split from the retired
`godot-3d-character-pipeline` (#293, closed).

**Setup/scaffold + proposal only — NO lessons.** Full scope + sources + artifacts + open Qs:
**`.scratch/tracks/3d-navigation.md`**.

## Domain shape

```yaml
domain: godot-3d-navigation
description: "Navigate 3D worlds in Godot — bake navmeshes, follow paths with NavigationAgent3D, click-to-move, obstacles & avoidance, layers & links, runtime rebake"
depth: 0
parent: null
leads_to: []
```

Standalone depth-0. Core mental model taught throughout: **navigation is independent of
physics** — pathfinding only sees the baked navmesh (the "wall contract"). Soft prereq:
`movement-math` (the lerp/arrive math click-to-move leans on) — a `leads_to` edge from
movement-math into this domain, not a spine prereq. Movement primitive prereq:
godot-gamedev `0015-physics-and-collision` (CharacterBody3D + move_and_slide).

## Topics + prereq spine (6, from `.scratch/tracks/3d-navigation.md`)

| # | slug | why (short) | prereqs |
|---|------|-------------|---------|
| 1 | `navmesh-and-regions` | NavigationMesh/Region bake, cell_size/agent_radius, the physics-independent wall contract | [] |
| 2 | `agent-pathfollowing` | NavigationAgent3D; `get_next_path_position()` per frame; YOU move the body; sync guard | [1] |
| 3 | `click-to-destination` | camera ray-pick + `map_get_closest_point` snap → target_position (the point-and-click payoff) | [2] |
| 4 | `obstacles-and-avoidance` | static carve vs dynamic RVO; `velocity_computed`/safe_velocity; decision criteria | [2] |
| 5 | `layers-and-links` | 32-bit navigation_layers bitmask; NavigationLink3D enter/travel cost, bidirectional | [1] (soft [2]) |
| 6 | `runtime-rebake-and-dynamic-worlds` | threaded bake vs main-thread parse; dynamic worlds (capstone) | [2],[4],[5] |

Prereq edges: `1→2→3`; `2→4`; `1→5`; `(2,4,5)→6`. Minimum path = `1→2→3+4`. All within-map.

## Runnable-artifact validation gate (ADR-0010)

Committed **nav test-project** (sibling to `ink-test-project/`). Opt-in `nav:validate-gd` mise
task (`nav-gd-run.py` analogue of `ink-gd-run.py`) — instantiate each lesson scene, drive
scripted input, assert observable state (agent reaches target; click resolves to a snapped
navmesh point; two agents never overlap within summed radii + `safe_velocity ≤ max_speed`;
path crosses a link, avoids a layer-gated region; pre/post-rebake path differs). Tier-1 stdlib
oracle for L04 (no-overlap / v≤max_speed). `godot --headless` twice + harness `quit(0|1)`;
`resolve_godot()`→SKIP→return 0; not in core verify/CI. Answer BEFORE lessons.

## Acceptance criteria

- [ ] `godot-3d-navigation.MAP.md` at `library/godot-3d-navigation/maps/` with all 6 topics + prereq edges; ULIDs via `migrate_map_ids.py --apply`; passes `check-maps-forest.py`
- [ ] Committed nav test-project + opt-in `nav:validate-gd` harness (+ L04 Tier-1 oracle) identified/recorded (ADR-0010 gate answered)
- [ ] Standalone depth-0; movement-math soft-prereq + gamedev 0015 movement prereq wired
- [ ] Provenance recorded (design source `.scratch/tracks/3d-navigation.md`)
- [ ] The 6 open questions in the scope doc resolved or deferred (exact `map_get_closest_point` signature, test-project reuse, nav-layer vs avoidance-mask conflation, body-type convention, Godot version pin, `map_get_iteration_id` availability)
- [ ] NO lessons generated — 6 topic tickets created after sign-off

## Notes

- Restructured from #298 (closed superseded). Scope: `.scratch/tracks/3d-navigation.md`.
