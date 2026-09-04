---
id: "166"
title: "Script changes for domain subfolder support"
status: done
blocked_by: ["163"]
tags: [platform]
---

# Script changes for domain subfolder support

## What to build

Update the tooling so scripts operate on per-domain lesson subfolders
(`library/{domain}/lessons/{domain-slug}/NN-slug.html`) rather than assuming a flat
`lessons/` root — check-lesson, map generation, quiz generation, read-time, SVG checks, etc.

## Acceptance criteria

- [x] Lesson-authoring/validation scripts resolve lessons under domain subfolders
- [x] Map/quiz generation handle the subfolder layout

## Resolution (2026-09-04)

Shipped and in active use. The tooling operates on the subfolder layout end-to-end, proven
this session by the blender-texture-prep track: `check-lesson.py --workspace library/godot-gamedev
--lesson lessons/blender-texture-prep/06-wiring-the-shader.html` resolves and validates;
`estimate-read-time.py`, the map generator, and `verify-links` all handle the 21 files under
`library/godot-gamedev/lessons/blender-texture-prep/`. `mise run verify` passes over the
subfoldered lessons. Retro-closed under #285 (was an un-closed stub for shipped work).
