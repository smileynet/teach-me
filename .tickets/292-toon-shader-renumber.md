---
id: "292"
title: "Renumber godot-toon-shaders lessons 0003-0014 to per-domain 01-NN (consistency)"
status: open
blocked_by: []
priority: low
tags: [platform, content-quality]
---

# Renumber godot-toon-shaders lessons 0003-0014 to per-domain 01-NN (consistency)

## Problem

Surfaced during #285 (2026-09-04). The per-domain numbering convention (each MAP track starts
at 01, `NN-slug.html`) is applied to newer tracks (blender-texture-prep = 01–06) but the
godot-toon-shaders + godot-mktoon tracks still use the old GLOBAL numbering
(`0003-spatial-shader-anatomy.html` … `0014-vfx-dissolve-vertex.html`). #163 had an AC to
renumber `0003→01` / `0004→02` but it was never done (its deferral to #166 didn't cover it).

So the repo is internally inconsistent: two numbering schemes coexist. Not urgent (both resolve
and serve fine), but it violates the documented convention.

## What to build

Renumber the godot-toon-shaders (and godot-mktoon) lesson files to per-domain `NN-slug.html`
starting at 01, and update every reference: the MAP.md `lesson_file:` fields, the committed
map-page HTML `lessonPath`, cross-lesson nav links (prev/next), quiz/reference back-links, and
any `reference/code/{slug}/` paths that embed the number.

## Acceptance criteria

- [ ] godot-toon-shaders + godot-mktoon lessons renumbered to per-domain `NN-slug.html` (01…)
- [ ] MAP.md + committed map-page HTML + nav/quiz/reference cross-references all updated
- [ ] `mise run verify` EXIT 0 (verify-links resolves every renamed path)
- [ ] Check #163's deferred renumber AC once this lands (or note it superseded by this ticket)

## Context

- Files: `library/godot-gamedev/lessons/0003-…0014-*.html` (12 lessons across two sub-tracks)
- Convention source: AGENTS.md ("per-domain subfolders numbered from 01"; "no flat lessons/ root"
  — note these toon lessons are in the flat `lessons/` root, a second inconsistency to consider)
- Risk: high cross-reference fan-out — do it as a scripted rename + reference-rewrite, verify-links as the gate
