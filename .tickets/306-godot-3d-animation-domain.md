---
id: "306"
title: "Set up godot-3d-animation domain (character animation track: MAP + reference project + validation gate)"
status: open
blocked_by: []
priority: medium
validation_criteria:
  - "godot-3d-animation.MAP.md exists with 6 topics + prereq edges (passes check-maps-forest)"
  - "Committed anim test-project + opt-in headless import/drive validation (ADR-0010, ink-gd-run.py pattern)"
  - "CC0 rigged character asset with root-motion clip sourced + provenance recorded; standalone depth-0"
tags: ["content"]
---

# Set up godot-3d-animation domain (character animation track: MAP + reference project + validation gate)

Stand up the standalone **`godot-3d-animation`** teaching domain — driving a 3D character's
motion and look in Godot 4.x: AnimationPlayer/libraries → AnimationTree blending → state
machines → root motion → runtime skins/accessories. One of four focused tracks split from the
retired `godot-3d-character-pipeline` (#293, closed). **This track is the "assembly/authoring"
home** — it absorbs the old single-track capstone (#299).

**Setup/scaffold + proposal only — NO lessons.** Full scope + sources + artifacts + open Qs:
**`.scratch/tracks/3d-animation.md`**.

## Domain shape

```yaml
domain: godot-3d-animation
description: "Animate 3D characters in Godot — AnimationPlayer/libraries, AnimationTree blending, state machines, root motion, and runtime skins/accessories"
depth: 0
parent: null
leads_to: []
```

Standalone depth-0. **This is the canonical AnimationTree home** — coordinate with
godot-gamedev's unbuilt `animation-and-audio` topic (keep that AnimationPlayer/2D-focused).
Soft prereq: `godot-asset-pipeline` (you need imported rigged clips) — a `leads_to`/global-map
edge, not a spine prereq.

## Topics + prereq spine (6, from `.scratch/tracks/3d-animation.md`)

| # | slug | why (short) | prereqs |
|---|------|-------------|---------|
| 1 | `animationplayer-and-libraries` | AnimationPlayer + AnimationLibrary container model; `library/anim` keys; callback modes | [] |
| 2 | `animationtree-blend-trees` | AnimationTree↔Player relationship; Blend2/3/OneShot/filters; `parameters/…`; RESET/T-pose rule | [1] |
| 3 | `blend-spaces-locomotion` | BlendSpace1D vs 2D, Delaunay triangles, sync modes (locomotion as ONE application) | [2] |
| 4 | `state-machines-and-oneshot-actions` | StateMachine `travel()` (switch modes, low-fps trap), OneShot FIRE/ABORT action layers | [3] |
| 5 | `root-motion-driven-movement` | `root_motion_track`, get_root_motion_* vs _accumulator, feed move_and_slide, zero-vector pitfall | [4] |
| 6 | `character-authoring-skins-and-accessories` | runtime `set_surface_override_material` (duplicate gotcha), BoneAttachment3D, retargeting/BoneMap | [2] (soft [1],[5]) |

Prereq edges: linear spine `1→2→3→4→5`; `6` branches off `2`. All within-map.

## Runnable-artifact validation gate (ADR-0010)

Committed **anim test-project** (sibling to `ink-test-project/`). Opt-in `anim:validate-gd`
mise task modeled on `ink:validate-gd` — instantiate each lesson scene, `await` ready, drive
input/requests, assert node state (blend_position quadrant, current state name, `OneShot/active`
true→false, root-motion delta non-zero when track set + zero when unset, surface override
changed, BoneAttachment global transform tracks the hand bone). `godot --headless --editor
--import --quit` twice + harness `quit(0|1)`; `resolve_godot()`→SKIP→return 0; not in core
verify/CI. **Also needs a CC0 rigged GLB** (idle/walk/run/strafe/jump/attack + a root-motion
clip + humanoid rig + hand bone) — source + license + REFERENCES.md clone line. Answer BEFORE lessons.

## Acceptance criteria

- [ ] `godot-3d-animation.MAP.md` at `library/godot-3d-animation/maps/` with all 6 topics + prereq edges; ULIDs via `migrate_map_ids.py --apply`; passes `check-maps-forest.py`
- [ ] Committed anim test-project + opt-in `anim:validate-gd` harness identified/recorded (ADR-0010 gate answered)
- [ ] CC0 rigged character asset (root-motion clip + humanoid rig + hand bone) sourced; license + REFERENCES.md clone line recorded
- [ ] Canonical-AnimationTree-home coordination with godot-gamedev animation-and-audio noted (no duplication)
- [ ] Standalone depth-0; asset-pipeline soft-prereq wired via leads_to/global map
- [ ] The 5 open questions in the scope doc resolved or deferred (test-project reuse, asset licensing, Godot version pin, retarget-as-7th-lesson, GDScript-only)
- [ ] NO lessons generated — 6 topic tickets created after sign-off

## Notes

- Restructured from #296/#297/#299 (closed superseded). Scope: `.scratch/tracks/3d-animation.md`.
