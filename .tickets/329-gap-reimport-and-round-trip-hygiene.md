---
id: "329"
title: "godot-asset-pipeline topic 6: reimport-and-round-trip-hygiene"
status: open
blocked_by: ["305", "325"]
validation_criteria:
  - "Lesson 06: from 'can get assets in' → 'source keeps changing / need it back out' → iterate loop, reimport-multiple, changing importer, reverse GLTFDocument export (runtime API), UID stability, .blend-vs-committed-glTF team tradeoff. Decision callout at that fork. Soft-prereq topic 5. References gltf-format round-trip fidelity. Lands at a mature round-trip"
  - "Runnable artifact (import → export-back → reimport) + asset:validate-gd L6 assertion (surface/vertex count preserved within tolerance)"
  - "Reference doc + SR cards + glossary JSON; passes mise run verify"
tags: ["content"]
---

# godot-asset-pipeline topic 6: reimport-and-round-trip-hygiene

## Context

Track spiral topic 6, the track closer (#305). win → complication → resolution → win. Prereq topic 2
(soft topic 5). Design: `.scratch/proposals/305-godot-asset-pipeline-setup.md`.

## What to build

- **Start from the win**: "You can get assets *in* — static and rigged, correctly."
- **Harder case**: "The source keeps changing, files move, and sometimes you need it back *out*."
- **Resolve**: the iterate loop (edit source → auto-reimport, fast with `.blend` direct);
  reimport-multiple with per-parameter checkboxes; changing an importer; the reverse direction —
  exporting a Godot scene to glTF via `GLTFDocument` (runtime API: `append_from_scene` →
  `write_to_filesystem`) and its limits; UID stability. **Decision callout** at the fork:
  `.blend`-direct vs committed-glTF team tradeoff (everyone needs Blender for `.blend`). Wraps the
  track by returning to the "fix upstream" principle.
- **Land back**: a mature round-trip the learner can live in.
- Prose link: references gltf-format round-trip fidelity.

## Acceptance criteria

- [ ] Lesson `06-reimport-and-round-trip-hygiene.html` in the spiral shape; `.blend`-vs-glTF Decision callout with criteria
- [ ] Runnable artifact (import → export-back → reimport) + `asset:validate-gd` L6 assertion (surface/vertex count preserved within tolerance)
- [ ] Reference doc + SR cards + glossary JSON
- [ ] Passes `mise run verify`
