---
id: "326"
title: "godot-asset-pipeline topic 4: import-dock-and-name-suffixes"
status: open
blocked_by: ["305", "325"]
validation_criteria:
  - "Lesson 03: from a working visual prop → 'it is just a mesh — needs collision / strip a helper' → three interfaces + 4.7 suffix vocabulary by role (-col/-convcol/-colonly/-occ/-navmesh/-noimp/-rigid/-loop). Decision callout: triangle-vs-convex-vs-primitive + OMI-glTF-physics alternative. Lands at a game object that still renders"
  - "Runnable artifact (multi-object suffixed source) + asset:validate-gd L4 assertion (StaticBody3D+CollisionShape3D for -col, -noimp node absent, Occluder3D present)"
  - "Reference doc + SR cards + glossary JSON; passes mise run verify"
tags: ["content"]
---

# godot-asset-pipeline topic 4: import-dock-and-name-suffixes

## Context

Track spiral topic 4 (#305). win → complication → resolution → win. Design:
`.scratch/proposals/305-godot-asset-pipeline-setup.md`.

## What to build

- **Start from the win**: "You have a prop that imports and renders correctly, safely."
- **Harder case**: "But it's *just a mesh* — it needs collision, or a modeling-only helper needs
  stripping."
- **Resolve**: the three customization interfaces (Import dock / Advanced Import Settings / name
  suffixes) + the 4.7 suffix vocabulary taught *by asset role*: `-col`/`-convcol`/`-colonly`,
  `-occ`/`-occonly`, `-navmesh`, `-noimp`, `-rigid`, `-loop`. **Decision callout** at the fork:
  triangle-vs-convex-vs-primitive collision; and OMI glTF-physics as an *Alternative* callout (Q4 —
  suffixes are the taught default).
- **Land back**: the prop is now a *game object* (has collision / occlusion) that still renders.
- **Asset: a small multi-object Kenney scene (CC0)** — e.g. Furniture `table`+`chair` or a Nature
  cluster; author suffixed copies (`-col`, `-noimp`, `-occ`). Reuses the topic-1 kit. Manifest:
  `.scratch/tracks/asset-pipeline-ASSETS-manifest.md`.

## Acceptance criteria

- [ ] Lesson `04-import-dock-and-name-suffixes.html` in the spiral shape; collision + OMI Decision callouts with criteria
- [ ] Runnable artifact (multi-object source with suffixes) + `asset:validate-gd` L4 assertion (StaticBody3D+CollisionShape3D for `-col`, `-noimp` node absent, Occluder3D present)
- [ ] Reference doc + SR cards + glossary JSON
- [ ] Passes `mise run verify`
