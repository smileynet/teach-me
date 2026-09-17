---
id: "376"
title: "Teach: generative-media-pipelines / media-types-and-image-to-3d"
status: open
blocked_by: ["367", "371"]
tags: ["content"]
---

# Teach: generative-media-pipelines / media-types-and-image-to-3d

Generate the lesson for topic 6 (MAP id `01M2R98N1JBZ8E3378G56N2Y8S`, lesson file
`06-media-types-and-image-to-3d.html`, scope: substantial, prereqs: the-universal-serving-pipeline).
Produced via the `generate-topic` pipeline.

> **Refined 2026-09-17** from a per-topic research+review subagent (license statuses web-verified
> 2026-09-17). Findings: `.scratch/research/376-refine.md`.

## What to build

Three arcs, all repo-grounded:

1. **Media-type coverage matrix** across the three platforms — image→3D is the *common denominator*
   every platform ships or targets; 2D+editing is REDACTED's depth; video is Bedrock-async **(same
   async contract, not a fourth serving substrate)**; speech = **STT-only, deferred to topic 8**; no
   TTS, no in-platform LoRA training.
2. **The two-level 2D pipeline** (Options × Variations, 1..5 each → ≤25 images) with the **canary
   moderation probe** (one probe moderated before the full batch → a block wastes 1 call not 25),
   cited to `REDACTED/backend/routers/generate.py`.
3. **Image→3D as TWO model families** — native-3D latent generation (Hunyuan3D-DiT, TripoSG,
   TRELLIS/SLAT) vs feed-forward LRM reconstruction (TripoSR ~0.5s, SF3D) — placed correctly, with
   the frontier (TRELLIS.2-4B full-PBR).

**The two taxes:**
- **Licensing gate (headline decision, before quality):** a per-model, dated (2026-09) license table
  — Hunyuan3D (all versions) = **Tencent NON-COMMERCIAL with an EU/UK/South-Korea territorial
  exclusion**; TRELLIS.2 / TripoSG / TripoSR = **MIT**; SF3D = **Stability Community License, $1M
  revenue Enterprise threshold** (a third license class). Each row cites its model card / LICENSE URL.
  **TRELLIS.2 "MIT" carries the nvdiffrast asterisk** every time it's called commercially usable —
  the PBR-bake dependency closure (nvdiffrast/nvdiffrec) has NVIDIA non-commercial-flavored terms;
  license-clear the *whole dependency closure*, not just the headline model.
- **Cleanup tax (existence + who pays it only):** raw AI meshes are triangle-soup with no clean UVs /
  invalid PBR; named stages retopo→LOD→re-UV→PBR-correction→scale/pivot→collision→GLB-export;
  REDACTED's headless-Blender `mesh_export.py` is the "automated" example to cite.

## LOCKED cross-reference framing (enforce; do NOT drift into how-to)

Teach image→3D as a **generation + platform** concern. **Cross-reference `gltf-format` and
`godot-asset-pipeline` for the cleanup MECHANICS via a prose link only** — NOT a MAP prereq edge,
NOT re-taught. This lesson stops at "the cleanup tax exists and here's who pays it." The single most
likely scope creep is drifting into retopo/UV/PBR how-to; the negative-scope AC below guards it.

## G2 warnings (Con callouts, cited)

TRELLIS.2 nvdiffrast dependency-closure caveat; Hunyuan3D territorial exclusion (easy to miss);
raw-mesh quality is a known failure mode (cleanup mandatory; pre-processing choices change quality);
no launched AWS/Bedrock-native image→3D model exists (don't claim one); GLB excludes lights/cameras
(belongs in the gltf-format cross-ref, not re-taught); Gaussian-splat vs mesh mismatch (splats aren't
engine-ready meshes).

## Source-verification gate (per #367)

Design-source facts → repo file paths (`REDACTED/backend/routers/generate.py`, `generate_3d.py`,
`services/mesh_export.py`; `REDACTED .../workflow_api.json`); every **license/model-quality claim** →
model-card/LICENSE URL, dated 2026-09, tagged `[L#:confidence]`. No "commonly known" citations.

## Artifact set (authoritative gate: `tools/check-topic-completeness.py`)

Lesson HTML at **flat** `library/generative-media-pipelines/lessons/06-media-types-and-image-to-3d.html`;
reference; quiz (≥5/≥3); SR JSONL (≥1); **inline `glossary-data` block, not a JSON file**;
code-files dir only if `data-file` blocks exist. Follows `visual-teaching.md` +
`code-validation-teaching.md`.

## Acceptance criteria

- [ ] `library/generative-media-pipelines/lessons/06-media-types-and-image-to-3d.html` generated via `generate-topic` (flat path)
- [ ] Media-type coverage matrix across the three platforms (image→3D common denominator; video = Bedrock-async, same contract; speech = STT-only deferred to topic 8), each cell citing a repo path
- [ ] Two-level Options × Variations pipeline + the canary probe (wastes 1 call not 25) explained, cited
- [ ] Image→3D presented as two families (native-3D vs feed-forward LRM) with TRELLIS.2/Hunyuan3D/TripoSG/TripoSR placed
- [ ] Per-model license table: Hunyuan3D = Tencent NON-COMMERCIAL + EU/UK/South-Korea exclusion; TRELLIS/TripoSR/TripoSG = MIT; SF3D = Stability Community License + $1M threshold; each row cites its card/LICENSE URL; dated 2026-09
- [ ] nvdiffrast dependency-closure warning present wherever TRELLIS.2 is called commercially usable
- [ ] Cleanup tax stated to EXIST (named stages) with `mesh_export.py` as the automated example, and cross-references gltf-format + godot-asset-pipeline via **prose link only**
- [ ] **Negative-scope AC:** lesson does NOT teach retopo/UV/PBR-packing/LOD-authoring/glTF-Godot import mechanics, and adds NO MAP prereq edge to those domains
- [ ] Reference + quiz (≥5/≥3) + SR JSONL + inline glossary produced; every claim cites a repo path or a model-card/LICENSE URL
- [ ] `mise run verify` passes AND `check-topic-completeness.py --workspace library/generative-media-pipelines --topic media-types-and-image-to-3d` (and `--concepts`) clean
