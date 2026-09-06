---
id: "311"
title: "Topic: authoring-and-blender-export (Blender->glTF; Principled BSDF mapping; what's dropped)"
status: open
blocked_by: ["310"]
priority: medium
validation_criteria:
  - "Lesson teaches the glTF-Blender-IO exporter (pattern-matcher), +Y-up/apply-transform, Principled BSDF->glTF metal-rough (clean vs re-baked vs ignored), animation Actions/NLA, what doesn't survive"
  - "Runnable artifact: an exported .glb validated by the gltf-format oracle (material channels + convention); .blend source opt-in (SKIP if Blender absent)"
tags: ["content"]
---

# Topic: authoring-and-blender-export (Blender->glTF; Principled BSDF mapping; what's dropped)

How a DCC produces conformant glTF — Blender as the canonical example. Where most "my model looks
wrong" bugs are born.

> **Prereqs:** #310 (the anatomy vocabulary).

## Source

`.scratch/research/gltf-blender-export.md`; docs.blender.org glTF exporter + KhronosGroup/glTF-Blender-IO.
(Some Blender-manual version mirrors 403 to bots — the GitHub repo is the fallback source of truth.)

## What to teach

- **The exporter is a pattern-matcher, not a renderer** — it recognizes a specific Principled-BSDF
  + image-texture layout and copies textures verbatim when wired glTF-native (metal=B/rough=G in
  one Non-Color image; AO=R via the glTF Material Output node group; normal = tangent-space).
- **Principled BSDF → glTF metal-rough:** clean (glTF-native channel layout) vs re-baked
  (mis-packed) vs **ignored** (procedural textures, arbitrary node math, non-Principled shaders).
- **Transform:** the single "+Y Up" checkbox; **apply Rotation & Scale (Ctrl+A) before export**
  (unapplied scale → wrong normals/bounds); Flatten Hierarchy escape hatch.
- **Mesh:** Apply Modifiers, UVs/Normals/Tangents toggles, ≤4/8 bone influences; glTF always
  triangulates + splits verts on UV/normal discontinuities.
- **Animation modes:** Actions (default — stash/push-down to NLA), Active, NLA Tracks; only
  Actions/Active export non-sampled; IK/constraints/drivers export as baked keyframes only.
- **What doesn't survive:** procedural textures, material/light/physics animation (only TRS +
  pose bones + shape keys).

## Runnable artifact (ADR-0010)

An exported `.glb` (from a committed `.blend` source, or a pre-exported `.glb` if Blender absent)
validated by `tools/gltf-format-oracle.py` (material channels present, +Y-up convention). The
`.blend` source is opt-in and SKIPs where Blender is absent (Blender-track precedent). Downloadable
at `reference/code/gltf-format/authoring-and-blender-export/`.

## Acceptance criteria

- [ ] Lesson teaches the pattern-matcher model, Principled→glTF mapping (clean/re-baked/ignored), +Y-up + apply-transform, mesh/animation export modes, and what doesn't survive
- [ ] Decision/gotcha callouts for the export-dialog choices that matter (Actions vs NLA; apply transform)
- [ ] Runnable artifact: exported .glb validated by the domain oracle; .blend source opt-in (SKIP without Blender)
- [ ] Cites the Blender glTF exporter manual + glTF-Blender-IO
- [ ] `mise run verify` passes; MAP.md gets lesson_file on completion

## Notes

- Empirically verify export settings against the target Blender version before publishing (5 open
  Qs flagged in the scope doc).
