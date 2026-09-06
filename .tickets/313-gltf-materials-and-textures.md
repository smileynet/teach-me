---
id: "313"
title: "Topic: materials-and-textures (PBR metal-rough; sRGB-vs-linear per slot; ORM; KHR_materials_*)"
status: open
blocked_by: ["310"]
priority: medium
validation_criteria:
  - "Lesson teaches the PBR metallic-roughness model, texture slots (baseColor/metalRough/normal/occlusion/emissive), sRGB-vs-linear per slot (the #1 silent bug), ORM packing, KHR_materials_* extensions"
  - "Runnable artifact: oracle asserting material texture-index validity + color-space-slot expectations on a real .glb"
tags: ["content"]
---

# Topic: materials-and-textures (PBR metal-rough; sRGB-vs-linear per slot; ORM; KHR_materials_*)

The highest-fidelity-loss surface across the round trip — and where the #1 silent bug (color space)
lives.

> **Prereqs:** #310 (anatomy); soft #311 (export mapping).

## Source

`.scratch/research/gltf-standard.md` (PBR section) + `.scratch/research/gltf-godot-import.md`
(material translation); Khronos glTF 2.0 material spec.

## What to teach

- **The PBR metallic-roughness model:** baseColor, metallic, roughness, normal, occlusion,
  emissive — the glTF standard material.
- **Texture slots + the sRGB-vs-linear rule (the #1 silent bug):** baseColor + emissive are
  **sRGB**; metallicRoughness, normal, occlusion are **linear/Non-Color**. Getting this wrong is
  the classic "why is my model too dark/washed out."
- **ORM packing:** occlusion=R, roughness=G, metalness=B in one image (why glTF packs them).
- **`KHR_materials_*` extensions:** emissive_strength, unlit, transmission, clearcoat, sheen, ior —
  what they add and the "baseline viewer ignores unknown extensions" fallback.

## Runnable artifact (ADR-0010)

Extend `tools/gltf-format-oracle.py` (or a lesson `.py`) to assert material texture-index validity
+ the color-space-slot expectations on a real `.glb` (e.g. baseColor slot flagged sRGB). Downloadable
at `reference/code/gltf-format/materials-and-textures/`.

## Acceptance criteria

- [ ] Lesson teaches the PBR metal-rough model, the sRGB-vs-linear-per-slot rule (as the headline gotcha), ORM packing, and the KHR_materials_* mechanism
- [ ] The color-space rule is a Decision/Gotcha callout with concrete "too dark / washed out" symptoms
- [ ] Runnable artifact: oracle asserting material texture-index validity + slot color-space expectations
- [ ] Teaches slots + color space, NOT the BRDF integral (math depth is out of scope — a rendering track)
- [ ] Cites the Khronos glTF material spec
- [ ] `mise run verify` passes; MAP.md gets lesson_file on completion

## Notes

- Prereq for #315 (extensions build on the material model).
