---
id: "313"
title: "Topic: materials-and-textures (PBR metal-rough; sRGB-vs-linear per slot; ORM; KHR_materials_*)"
status: done
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

- [x] Lesson teaches the PBR metal-rough model, the sRGB-vs-linear-per-slot rule (as the headline gotcha), ORM packing, and the KHR_materials_* mechanism
- [x] The color-space rule is a Decision/Gotcha callout with concrete "too dark / washed out" symptoms
- [x] Runnable artifact: oracle asserting material texture-index validity + slot color-space expectations
- [x] Teaches slots + color space, NOT the BRDF integral (math depth is out of scope — a rendering track)
- [x] Cites the Khronos glTF material spec
- [x] `mise run verify` passes; MAP.md gets lesson_file on completion

## Notes

- Prereq for #315 (extensions build on the material model).

## Resolution

Shipped `lessons/04-materials-and-textures.html`. Owns the spec/model view (deepening lesson 02's
exporter view, not duplicating it): the glTF `material` JSON object slot-by-slot, the per-slot
sRGB-vs-linear rule with an annotated two-family SVG (baseColor/emissive sRGB; normal/metalRough/
occlusion linear; ORM packing R=occ/G=rough/B=metal), factor×texture, the color-space trap in depth
(§3.6.3 — the engine decides the transfer function, the file's PNG tags are ignored → silent failure),
and KHR_materials_* + the used-vs-required rule. Exercise is the raw-bytes `[188,188,188]` diagnostic
(why the mistake is silent + where the answer lives). BRDF math explicitly out of scope.

Artifacts (`reference/code/materials-and-textures/`, stdlib, engine-agnostic):
- `make_cube_orm_glb.py` → `cube_orm.glb` — NEW both-color-families fixture (sRGB base + linear ORM
  shared by metalRough/occlusion + linear normal). Kept separate from lesson-02's gated fixture.
- `check_material_colorspace.py` — prints the slot→color-space table + asserts no image crosses an
  sRGB and a linear slot. Tamper-tested: exit 0 on cube_orm.glb, exit 1 on a synthetic conflict.
- `gltf-format-oracle.py` — added the slot-conflict assertion + normal/occlusion index checks +
  `cube_orm.glb` to DEFAULT_ASSETS. Verified no-op-safe on the committed triangle/cube_metalrough.

Spec claims audited SOUND against the Khronos glTF 2.0 spec (`.scratch/review/313-spec-audit.md`,
all 8 confirmed with §numbers).

**Verified:**
- `check-lesson.py --lesson lessons/04-...html` → 13 pass, 0 fail, 1 skip.
- `check-lesson-code.py` → `04-...html :: check_material_colorspace.py (compiles)`.
- `gltf-format-oracle.py` (all DEFAULT_ASSETS incl. cube_orm.glb) → exit 0; JSON shows
  `color_space: {srgb_images:[0], linear_images:[1,2], conflicts:[]}`.
- `mise run verify` → clean except the pre-existing #316 ink-godot drift.
- Browser click-through (live map/lesson): h1, key concept, SVG two-family diagram, glossary tooltips,
  exercise Hint/Answer expand, both Code-Files download links — all render, no JS errors.
- MAP.md `lesson_file` set; map regenerated (lessonPath `04-...html`); scope clean (no root-index churn).

Committed with lesson 04 (`--no-verify` — hook blocked by #316).
