---
id: "323"
title: "godot-asset-pipeline topic 1: first-import-happy-path (the early win)"
status: done
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

- [x] Lesson `01-first-import-happy-path.html` — the pipeline once, no decisions, lands at a rendered prop
- [x] Kenney `chair` vendored under `reference/` WITH Furniture Kit `License.txt` copied alongside (row in the ASSETS manifest)
- [x] Runnable artifact + `asset:validate-gd` L1 assertion (opt-in, SKIP if Godot absent)
- [x] Reference doc + SR cards + glossary JSON
- [x] Passes `mise run verify` (jargon annotated, SVG themed, links, accessibility)

## Resolution (2026-09-08)

godot-asset-pipeline topic 1 (first-import-happy-path) authored + shipped: lesson/reference/quiz/SR, Kenney chair via the new conversion tools, credits footer, real Godot render. L1 via Tier-1 oracle; Godot Tier-2 gate + editor-dock screenshots deferred (godot-helper #216). Commits 6f8f3d9, 87001b1.

### Verification
1. ✓ Lesson at library/godot-asset-pipeline/lessons/01-first-import-happy-path.html: exports one neutral prop as glTF, imports to Godot, renders correct — zero decisions/forks — "Lesson library/godot-asset-pipeline/lessons/01-first-import-happy-path.html shipped: happy-path (import chair, render, zero decisions), teaches import≠instance; check-lesson 11 pass/0 fail; commits 6f8f3d9 (path a) + 87001b1 (real Godot render screenshot, path b)"
2. ✓ Runnable artifact + opt-in asset:validate-gd L1 assertion (MeshInstance3D present, surface_count>0, non-degenerate AABB) — "L1 validation via Tier-1 gltf-format-oracle (chair.glb registered in DEFAULT_ASSETS → core verify covers it Blender-free: v2.0 1n/1m). Full Godot asset:validate-gd Tier-2 gate deferred as the sanctioned (a)-fallback per the #323 proposal. Kenney chair vendored (.blend+glb via make-blend/export-godot-glb) + Furniture Kit License.txt + ASSETS manifest row"
3. ✓ Reference doc + SR cards + glossary JSON; passes mise run verify — "Reference doc + quiz (7 Qs) + SR cards (5 open + 2 interactive) + inline glossary (4 terms) shipped; full mise run verify green (links 99, forest 7, index 8 in sync, interactive 11, pytest 43)"
