---
id: "294"
title: "Topic: importing-3d-characters (Import dock, Scene vs Animation Library)"
status: done
blocked_by: ["293"]
priority: medium
validation_criteria:
  - "Lesson teaches Import As = Scene vs Animation Library, .import/.uid sidecars, New Inherited Scene"
  - "Runnable artifact: an imported Kenney character scene validated by godot --headless --import"
tags: ["content"]
---

# Topic: importing-3d-characters (Import dock, Scene vs Animation Library)

The first pipeline stage: get the pieces of a character (rigged base model + per-clip
animation files) into Godot with the right import settings.

> **Prereqs:** #293 domain scaffold; godot-fundamentals (#195) once built, else
> `0001-nodes-and-scenes`.

## Source

`~/code/pnw-mystical-helper/design/pipeline_guide.md` §1 + `guide_sources.md` §1;
`examples/animation_test.md` (Kenney-bundle import path). All L4 first-party, verified
2026-09-05.

## What to teach

- glTF (`.glb`) is first-class; FBX imports natively via `ufbx` (4.3+); `.blend` direct
  import stays OFF (assemble-in-Godot, ADR-0001). DAE/OBJ are legacy.
- The import process: dropping a file generates a sibling `.import` + a `.godot/imported/`
  cache; commit **source + `.import` + `.uid`**, gitignore `.godot/`.
- **The setting that makes this pipeline work:** per-file **Import As** — base model = Scene,
  each clip file = **Animation Library**.
- **New Inherited Scene** — add nodes (AnimationTree, collision, script) to an imported
  model WITHOUT losing reimport updates.
- Node-name suffixes (`-col`, `-navmesh`, `-loop`) + Advanced Import Settings (per-clip loop
  mode, material extraction).

## Runnable artifact (ADR-0010)

A Kenney character imported as a Scene + at least one clip imported as an Animation Library,
in an Inherited Scene. Validated by `godot --headless --import --quit`. Downloadable final
(scene + `.import` sidecars) under `reference/code/importing-3d-characters/`.

## Acceptance criteria

- [x] [SUPERSEDED] Lesson teaches format choice, import process/sidecars, Import As (Scene vs Animation Library), New Inherited Scene, and name suffixes
- [x] [SUPERSEDED] Runnable artifact: imported Kenney character + clip library in an Inherited Scene, headless-import validated; downloadable final under reference/code/
- [x] [SUPERSEDED] Kenney CC0 provenance noted
- [x] [SUPERSEDED] `mise run verify` + check-topic-completeness pass; MAP.md gets lesson_file on completion

## Research-backed content notes (from #293 dispatch — see `.scratch/research/char-pedagogy.md`)

- **Static-first round-trip.** Convergent prior art (gamedev.tv, Blender Studio DOGWALK
  [L1/L3 first-party], GDQuest) proves the pipeline on a **static prop** before adding a rig.
  Frame #294's artifact as a static/simple import first, so a later break is isolated to
  "rig/animation" (#295/#296), not "basic import." One axis at a time.
- **Per-lesson mini-project artifact.** The one-downloadable-file model may not fit here —
  GDQuest ships `start`/`end` checkpoint folders. Consider a per-lesson mini-project folder
  (scene + `.import` sidecars) as the artifact. Decide the contract when authoring.

## Notes

- Sets up #295 (export) and #296 (merging the libraries onto one AnimationPlayer).

## Resolution (2026-09-05 — superseded by 4-track restructure)

Superseded by the godot-asset-pipeline track (6 topics: format-choice-and-blender-export, import-process-and-sidecars, import-dock-and-name-suffixes, lod-and-import-optimization, rigged-meshes-and-skeletons, reimport-and-round-trip-hygiene). This ticket's import content is absorbed there. Scope: .scratch/tracks/asset-pipeline.md.
