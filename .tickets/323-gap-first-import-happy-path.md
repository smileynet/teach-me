---
id: "323"
title: "godot-asset-pipeline topic 1: first-import-happy-path (the early win)"
status: open
blocked_by: ["305"]
validation_criteria:
  - "Lesson at library/godot-asset-pipeline/lessons/01-first-import-happy-path.html: exports one neutral prop as glTF, imports to Godot, renders correct — zero decisions/forks"
  - "Runnable artifact + opt-in asset:validate-gd L1 assertion (MeshInstance3D present, surface_count>0, non-degenerate AABB)"
  - "Reference doc + SR cards + glossary JSON; passes mise run verify"
tags: ["content"]
---

# godot-asset-pipeline topic 1: first-import-happy-path (the early win)

## Context

First topic of the godot-asset-pipeline track (#305 setup). The track is structured
**happy-path-first, then spiral outward** — this topic is the PURE early win: the whole import
pipeline once, minimally, with **zero decisions and no forks**. Every later topic (2–7) takes this
standing win and widens it. Design: `.scratch/proposals/305-godot-asset-pipeline-setup.md` (§ topic
table). Structure guidance (DRAFT, under review in #322):
`.scratch/proposals/track-topic-structure-guidance-DRAFT.md`.

## What to build

The zero-decision happy path: export one neutral prop (a Kenney `chair` — CC0) → drop it into Godot
→ it renders correct (right-side-out, material intact). The learner's takeaway: **"I put a model in
Godot and it works."** No format matrix, no collision, no "it depends" — those are topics 2–7.

- **Asset: Kenney Furniture Kit `chair` (CC0 1.0).** Source: `Animated Characters Bundle` sibling kit
  Furniture Kit 2.1. Ships glb/fbx — derive a `.blend` (`reference/blender/chair.blend`) so the
  source→glTF path is end-to-end (Blender step shown, not taught here). See asset plan
  `.scratch/tracks/asset-pipeline-asset-plan.md` + license manifest
  `.scratch/tracks/asset-pipeline-ASSETS-manifest.md`.
- Runtime artifact: the prop imported into `asset-test-project/` with a working scene.
- Opt-in `asset:validate-gd` L1 assertion: MeshInstance3D present, `mesh.surface_count > 0`,
  non-degenerate AABB.
- gltf-format prose link (light): the `.glb` is the format from `gltf-anatomy-and-the-standard`.

## Acceptance criteria

- [ ] Lesson `01-first-import-happy-path.html` — the pipeline once, no decisions, lands at a rendered prop
- [ ] Kenney `chair` vendored under `reference/` WITH Furniture Kit `License.txt` copied alongside (row in the ASSETS manifest)
- [ ] Runnable artifact + `asset:validate-gd` L1 assertion (opt-in, SKIP if Godot absent)
- [ ] Reference doc + SR cards + glossary JSON
- [ ] Passes `mise run verify` (jargon annotated, SVG themed, links, accessibility)
