---
id: "165"
title: "Update teach/generate-topic/jargon skills for narrative + subfolders"
status: done
blocked_by: ["164"]
tags: [content-quality, platform]
---

# Update teach/generate-topic/jargon skills for narrative + subfolders

## What to build

Update the teach, generate-topic, and jargon skills so they (a) author lessons with the
narrative code-block framing (lead-in / bridge / connect-back, per visual-teaching.md) and
(b) write lessons into per-domain subfolders `lessons/{domain-slug}/NN-slug.html` (numbered
per-domain from 01) rather than a flat `lessons/` root.

## Acceptance criteria

- [x] Skills author lessons into `lessons/{domain-slug}/NN-slug.html` subfolders
- [x] Narrative code-block framing is part of the lesson-authoring guidance

## Resolution (2026-09-04)

Shipped and in active use. AGENTS.md documents the `lessons/{domain-slug}/NN-slug.html`
per-domain-subfolder layout as the standard (and the "no flat lessons/ root" constraint);
the narrative code-block framing (lead-in/bridge/connect-back) lives in
`.kiro/steering/visual-teaching.md` and is enforced by `check-lesson.py` (Q1). Both are
demonstrably applied — every recent lesson (e.g. the blender-texture-prep 01–06 track,
0015-physics-and-collision) is authored into a domain subfolder with narrative framing and
passes check-lesson. Retro-closed under #285 (was an un-closed stub for shipped work).
