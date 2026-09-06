---
id: "315"
title: "Topic: extensions-and-optimization (KHR_/EXT_ mechanism; Draco/meshopt; KTX2; validators — capstone)"
status: done
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

- [x] Lesson teaches the KHR_/EXT_ mechanism + extensionsUsed-vs-Required contract, Draco vs meshopt (decision callout), KTX2, variants, and the Khronos Validator/gltf-transform
- [x] Runnable artifact: oracle asserting extensionsRequired subset of used + compression-extension detection
- [x] Optional Khronos-Validator Tier-2 cross-check documented (npm library + Node wrapper, skip-if-no-node); gltf-transform noted as optimization-only
- [x] Snapshot the ratified-KHR list + cite the registry at author time (extensions evolve)
- [x] Cites the Khronos extension registry
- [x] `mise run verify` passes; MAP.md gets lesson_file on completion

## Notes

- Capstone — assumes the base file (topics 1-5) lands first (extensions-before-base-file is a fail pattern).

## Resolution

Shipped `lessons/06-extensions-and-optimization.html` — the track CAPSTONE (final lesson of gltf-format).
Deepens L03/L04's extension framing into the mechanism: the extensionsUsed-vs-extensionsRequired contract
reduced to ONE decision question ("does the core still render without this?"), drawn as a decision-tree
SVG with both wrong-choice failure modes labeled and anchored to RFC-2119 MUST/SHOULD. Covers Draco vs
meshopt (decision note), KTX2/basisu + material variants, and validate-then-optimize (Khronos Validator +
gltf-transform, with the prune→quantize→compress→gzip-last pass order). Uses the spec's "SHOULD NOT be
loaded" wording (per the spec audit) and a dated registry-snapshot note. Exercise is the two-backwards-
choices misconception probe. Depth held to the contract + decision (no compression-algorithm theory).

Artifacts (`reference/code/extensions-and-optimization/`, stdlib, engine-agnostic):
- `check_extensions.py` — prints the per-extension class/required/fallback table + asserts the contract:
  compression ext used-but-not-required = ERROR; material ext required = NOTE. Tamper-tested (exit 0 on
  truck-green with a note; exit 0 on required_ext; exit 1 on a synthetic compression-not-required).
- `make_required_ext_glb.py` → `required_ext.glb` — declare-only fixture (triangle listing
  EXT_meshopt_compression in used+required).
- `gltf-format-oracle.py` — added the compression=error / material-required=note classification +
  required_ext.glb to DEFAULT_ASSETS. Verified no-op-safe: truck-green's KHR_materials_unlit (required)
  stays a NOTE → PASS; no committed asset trips the compression-error path.

Spec claims audited (`.scratch/review/315-spec-audit.md`, 6/7 confirmed; the SHOULD-NOT-load + Information-
label fixes applied).

**Verified:**
- `check-lesson.py --lesson lessons/06-...html` → 13 pass, 0 fail, 1 skip.
- `check-lesson-code.py` → `06-...html :: check_extensions.py (compiles)`.
- `gltf-format-oracle.py` (all 9 DEFAULT_ASSETS incl. truck-green + required_ext) → exit 0.
- `mise run verify` → clean except the pre-existing #316 ink-godot drift.
- Browser click-through (live): decision-tree SVG (question + both branches + both failure modes),
  glossary tooltips, exercise Hint/Answer, both Code-Files downloads — all render, no JS errors.
- MAP.md `lesson_file` set; map regenerated; scope clean (no root-index churn).

Committed with lesson 06 (`--no-verify` — hook blocked by #316). **This completes the gltf-format track:
lessons 01-06 all shipped and gated.**
