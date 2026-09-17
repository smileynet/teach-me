---
id: "376"
title: "Teach: generative-media-pipelines / media-types-and-image-to-3d"
status: open
blocked_by: ["367", "371"]
tags: ["content"]
---

# Teach: generative-media-pipelines / media-types-and-image-to-3d

Generate the lesson for topic 6 (MAP id `01M2R98N1JBZ8E3378G56N2Y8S`, lesson file
`06-media-types-and-image-to-3d.html`, scope: substantial, prereqs:
the-universal-serving-pipeline).

## What to build

Teach what these platforms actually generate, with image→3D as the common denominator plus its own
licensing/cleanup gotchas. Cover the two-level 2D pipeline (Options × Variations, canary
moderation), video-async, image→3D model families (TRELLIS.2 / Hunyuan3D / TripoSG / TripoSR), the
**Hunyuan3D non-commercial-license gate**, and the universal retopo/UV/PBR/LOD "cleanup tax."

**Decision locked in #367:** teach image→3D as a *generation + platform* concern and
**cross-reference `gltf-format` and `godot-asset-pipeline`** (prose cross-link) for the
mesh/PBR/UV/LOD/collision cleanup mechanics — do NOT re-teach them, and do NOT add a MAP prereq
edge to those domains (they're engine/format tracks, not prerequisites for gen-media hosting).

Run `generate-topic`: research → lesson → post-process → verify.

## Source-verification gate (per #367)

- Claims → repo file path or `[L#]` source. Model families + Hunyuan3D license terms cited to
  their model cards/licenses as `[L#]`.
- Cross-links to `gltf-format` / `godot-asset-pipeline` are prose references, not duplicated content.
- `mise run verify` clean.

## Acceptance criteria

- [ ] `library/generative-media-pipelines/lessons/generative-media-pipelines/06-media-types-and-image-to-3d.html` generated
- [ ] Two-level 2D pipeline + video-async + image→3D families covered; Hunyuan3D non-commercial license gate flagged
- [ ] Cleanup tax cross-references gltf-format / godot-asset-pipeline (prose link, no duplication, no MAP prereq edge)
- [ ] Reference doc + quiz + SR cards + glossary JSON produced
- [ ] Every load-bearing claim cites a repo file path or `[L#]` source
- [ ] `mise run verify` passes; `check-topic-completeness.py` clean for this topic
