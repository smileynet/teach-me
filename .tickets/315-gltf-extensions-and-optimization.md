---
id: "315"
title: "Topic: extensions-and-optimization (KHR_/EXT_ mechanism; Draco/meshopt; KTX2; validators — capstone)"
status: open
blocked_by: ["313"]
priority: medium
validation_criteria:
  - "Lesson teaches extensionsUsed vs extensionsRequired, Draco + EXT_meshopt_compression, KHR_texture_basisu (KTX2), KHR_materials_variants, the Khronos glTF Validator + gltf-transform"
  - "Runnable artifact: oracle asserting extensionsRequired subset of used + detecting compression extensions; optional Khronos-Validator Tier-2 cross-check noted"
tags: ["content"]
---

# Topic: extensions-and-optimization (KHR_/EXT_ mechanism; Draco/meshopt; KTX2; validators — capstone)

The ships-to-production capstone — how to extend the format and shrink files without breaking
baseline viewers.

> **Prereqs:** #313 (materials — extensions build on the material model). Capstone of the track.

## Source

`.scratch/research/gltf-standard.md` (extensions) + `.scratch/research/gltf-validators.md`; Khronos
extension registry; gltf-transform docs.

## What to teach

- **The extension mechanism:** `KHR_` (Khronos) / `EXT_` (multi-vendor) / vendor prefixes;
  **`extensionsUsed` vs `extensionsRequired`** — a viewer can ignore an *used* extension but MUST
  understand a *required* one (the graceful-degradation contract).
- **Geometry compression:** Draco (`KHR_draco_mesh_compression`, smaller/slower-decode) vs
  **meshopt** (`EXT_meshopt_compression`, faster-decode) — decision callout.
- **Texture compression:** `KHR_texture_basisu` (KTX2/Basis Universal) — GPU-ready, transcodes to
  the target's native format.
- **Variants:** `KHR_materials_variants` (swap materials without duplicating meshes).
- **Validation:** the **Khronos glTF Validator** (reference conformance) + `gltf-transform` CLI
  (inspect/optimize) — how to check a file is spec-conformant before shipping.

## Runnable artifact (ADR-0010)

Oracle asserting `extensionsRequired ⊆ extensionsUsed` + detecting compression extensions in
`extensionsUsed` (already in `tools/gltf-format-oracle.py`). **Optional Tier-2:** a Khronos glTF
Validator Node wrapper (npm library, skip-if-no-node) as the real-conformance cross-check — noted,
not required for core verify. Downloadable at `reference/code/gltf-format/extensions-and-optimization/`.

## Acceptance criteria

- [ ] Lesson teaches the KHR_/EXT_ mechanism + extensionsUsed-vs-Required contract, Draco vs meshopt (decision callout), KTX2, variants, and the Khronos Validator/gltf-transform
- [ ] Runnable artifact: oracle asserting extensionsRequired subset of used + compression-extension detection
- [ ] Optional Khronos-Validator Tier-2 cross-check documented (npm library + Node wrapper, skip-if-no-node); gltf-transform noted as optimization-only
- [ ] Snapshot the ratified-KHR list + cite the registry at author time (extensions evolve)
- [ ] Cites the Khronos extension registry
- [ ] `mise run verify` passes; MAP.md gets lesson_file on completion

## Notes

- Capstone — assumes the base file (topics 1-5) lands first (extensions-before-base-file is a fail pattern).
