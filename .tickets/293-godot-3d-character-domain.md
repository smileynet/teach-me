---
id: "293"
title: "Set up godot-3d-character-pipeline domain (MAP + reference project + validation gate)"
status: open
blocked_by: []
priority: medium
validation_criteria:
  - "godot-3d-character-pipeline.MAP.md exists with 6 topics + prereq edges"
  - "Reference Godot project + headless-import validation identified before any lesson generates (ADR-0010)"
  - "Kenney CC0 provenance recorded; prereq wiring to godot-fundamentals/godot-gamedev set"
tags: ["content"]
---

# Set up godot-3d-character-pipeline domain (MAP + reference project + validation gate)

Stand up a NEW standalone teaching domain that teaches the full Godot 3D-character
pipeline — importing rigged 3D assets, exporting them cleanly from Blender, driving them
with an AnimationTree state machine, swapping skins at runtime, and moving them with
click-to-move navigation. This ticket creates the domain scaffold; the six topic tickets
(#294–#299) + the movement-math prereq (#300) generate the lessons.

**Do this FIRST** — the topic tickets are `blocked_by` this one. Nothing generates until
the domain shape + the runnable-artifact validation toolchain are signed off (ADR-0010).

## Source

- `~/code/pnw-mystical-helper/design/` — a Godot 4.7 3D-character pipeline guide, verified
  live 2026-09-05:
  - `pipeline_guide.md` — the 5-stage narrative (import → Blender export → animation →
    materials/skin → navigation) + the assembled Character scene.
  - `guide_sources.md` — annotated, live-verified first-party Godot doc list (the L4
    citations for every lesson).
  - `examples/animation_test.md` + `animation_test_skin.gd` — the AnimationTree half,
    worked end-to-end (ready-made final-state artifact).
  - `examples/click_to_move.md` + `click_to_move_example.gd` — the navigation half, worked
    (arrive-ramp math, the wall contract, ready-made artifact).
- **Assets:** Kenney Animated Characters Bundle — **CC0** (no attribution required; safe to
  derive/commit). 4 models · 17 clips · 53 shared-UV skins · 39 accessories.
- **Pipeline decision already made** by the source: assemble-in-Godot, Blender = source
  authoring only (pnw-mystical ADR-0001). Teach that stance; don't re-litigate it.

## Fit (reviewed 2026-09-05 — see `.scratch/review/godot-coverage.md`)

3 of 5 pipeline pillars are ENTIRELY untaught in teach-me today (AnimationTree/state
machines, runtime skin swap, NavigationAgent3D click-to-move). The other 2 (glTF import,
Blender→Godot export) exist only as a TEXTURE-only slice in `blender-texture-prep` — this
domain adds meshes + armatures + animations on top. No duplication.

## Domain shape (proposed)

```yaml
domain: godot-3d-character-pipeline
description: "Take a rigged 3D character from Blender source into a moving, animated, skinnable actor in Godot"
depth: 0
parent: null
leads_to: []   # future: IK, ragdoll, retargeting
```

Standalone depth-0 (NOT a sub-map of godot-gamedev): it's an asset+gameplay-pipeline axis,
distinct from the NPR/shading axis of godot-gamedev's existing sub-maps. Precedent:
`ink-godot` is standalone despite depending on Godot (#193).

### Topics + prereq spine

| Topic (ticket) | slug | prereqs |
|----------------|------|---------|
| #294 | `importing-3d-characters` | godot-fundamentals (or 0001-nodes-and-scenes) |
| #295 | `blender-gltf-character-export` | importing-3d-characters |
| #296 | `animation-tree-state-machines` | blender-gltf-character-export |
| #297 | `runtime-skin-and-accessories` | animation-tree-state-machines |
| #300 | `movement-math-lerp-acceleration` (prereq) | 0002-gdscript-fundamentals |
| #298 | `navigation-click-to-move` | 0015-physics-and-collision, movement-math-lerp-acceleration |
| #299 | `assembling-the-character` | animation-tree-state-machines, runtime-skin-and-accessories, navigation-click-to-move |

## Runnable-artifact validation gate (ADR-0010 — the hard question, answer BEFORE lessons)

Each lesson produces a Godot scene/script artifact. Validation tier (same as the shader
track): `godot --headless --import --quit` against a test-scene reference project +
per-file `.gd` compile-check. The design ships `animation_test_skin.gd` and
`click_to_move_example.gd` as ready-made final-state artifacts. **This ticket must confirm
the reference project + validation command are in place before #294–#300 generate.**

## What to do

1. Decide reference-project location (a `.references/`-adjacent Godot test-scene, or reuse
   an existing one) and confirm `godot --headless --import` validates a rigged-glTF +
   AnimationTree scene. Record the exact command.
2. Write `godot-3d-character-pipeline.MAP.md` (domain frontmatter + `## Orientation` +
   6 `### {topic}` blocks with `id`/`title`/`why`/`scope`/`prereqs`; NO `lesson_file` yet).
3. Wire prereqs: prereq `godot-fundamentals` (#195) once built; until then the concrete
   `godot-gamedev` lessons 0001/0002/0015. Add cross-domain tags for the global map.
4. Record Kenney CC0 provenance + the design-doc source in the MAP orientation / a
   `.memory/` note.

## Acceptance criteria

- [ ] `godot-3d-character-pipeline.MAP.md` created with all 6 topics + prereq edges (passes `tools/check-maps-forest.py`)
- [ ] Reference Godot project identified + `godot --headless --import --quit` validation command recorded (ADR-0010 gate answered)
- [ ] Kenney CC0 provenance + design-doc source recorded
- [ ] Prereq wiring to godot-fundamentals (#195) / godot-gamedev 0001·0002·0015 set
- [ ] Standalone depth-0 confirmed; no duplication with blender-texture-prep / godot-gamedev (differentiated per `.scratch/review/godot-coverage.md`)
- [ ] NO lessons generated — topic tickets #294–#300 do that after this is signed off

## Notes

- Setup/scaffold only; lessons come from the topic tickets.
- The toolchain-validation gate is the real risk (can't ship a lesson whose artifact we
  can't headless-import). Answer it here.
- Review artifacts: `.scratch/review/conventions.md`, `.scratch/review/godot-coverage.md`.
