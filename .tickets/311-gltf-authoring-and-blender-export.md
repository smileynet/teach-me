---
id: "311"
title: "Topic: authoring-and-blender-export (Blender->glTF; Principled BSDF mapping; what's dropped)"
status: done
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

A **stdlib-generated** `cube_metalrough.glb` (via `make_cube_glb.py` — `struct`+`json`+`base64`+`zlib`,
embedded base-color PNG, NO Blender) is the **committed always-validatable** artifact, checked by
`tools/gltf-format-oracle.py` (extended to assert material-channel presence — see below).
A **`export_cube.py` bpy script** is the reproducible Blender source (NOT a committed `.blend` —
the repo has a zero-`.blend` precedent; the Blender track ships diffable bpy `.py` scripts). Wire it
as an opt-in Tier-2 `--check` in `tools/verify-blender.py` (success-sentinel + `--python-exit-code 1`;
SKIPs where Blender absent). Downloadable at `reference/code/gltf-format/authoring-and-blender-export/`.

## Acceptance criteria

- [x] Lesson teaches the pattern-matcher model, Principled→glTF mapping (clean/re-baked/ignored), +Y-up + apply-transform, mesh/animation export modes, and what doesn't survive
- [x] Decision/gotcha callouts for the export-dialog choices that matter (Actions vs NLA; apply transform)
- [x] Runnable artifact: stdlib `cube_metalrough.glb` (+ `make_cube_glb.py`) validated by the domain oracle asserting material channels present; **reproducible bpy source script** (`export_cube.py`, opt-in Tier-2 in `verify-blender.py`, SKIP without Blender) — NOT a committed `.blend`
- [x] Oracle extended to assert `pbrMetallicRoughness` + `baseColorTexture` presence for the lesson asset; cube added to `DEFAULT_ASSETS`
- [x] Cites the Blender glTF exporter manual (local `.references/blender-manual/manual/addons/scene_gltf2.rst`) + glTF-Blender-IO
- [x] `mise run verify` gates pass; MAP.md got lesson_file on completion

## Resolution (2026-09-06)

Authored lesson 02 + its artifacts, all validated:

- **Lesson:** `library/gltf-format/lessons/02-authoring-and-blender-export.html` — key-concept ("translator, not renderer") → the **3-column (CLEAN/RE-BAKED/DROPPED) × 5-row (material/geometry/textures/animation/lights) decision-matrix SVG** → clean material path + `KHR_materials_*` escape-hatch `.note` → geometry/transform gotcha (`+Y Up`, apply scale/modifiers, triangulation) → animation Mode decision + IK-needs-Sampling gotcha → **exercise** (Voronoi-DROPPED + IK-needs-sampling misconception probe) → Code Files (4 downloads) → What's Next. 5 glossary terms, all annotated.
- **Artifacts** at `reference/code/authoring-and-blender-export/`: `cube_metalrough.glb` (stdlib-built, `pbrMetallicRoughness` + `baseColorTexture` + embedded PNG), `make_cube_glb.py` (stdlib generator — `struct`+`json`+`zlib`, no Blender/Pillow), `export_cube.py` (bpy source, `--bake`/`--check`, `EXPORT_CUBE_OK` sentinel), `export_notes.md` (game-ready settings card from the local Blender manual RST), `README.md`.
- **Oracle extended:** `check_asset(require_material=)` asserts `material[0].pbrMetallicRoughness` + `baseColorTexture`; `cube_metalrough.glb` in `DEFAULT_ASSETS` + `REQUIRE_MATERIAL`; `--require-material` CLI flag added. Tamper-tested: cube passes (exit 0), material-less triangle with `--require-material` fails (exit 1).
- **Tier-2 wiring:** `export_cube.py --check` added to `tools/verify-blender.py` ARTIFACTS (opt-in, SKIPs where Blender absent).

**Verification:** `check-lesson.py --workspace library/gltf-format --lesson lessons/02-...` → "11 pass, 0 fail, 0 warn, 3 skip"; lesson 01 re-checked "13 pass, 0 fail" (forward-link added); `gltf-format-oracle.py` → exit 0 (cube material-gated); `check-lesson-code.py` → make_cube_glb.py + export_cube.py compile; `check-svg-vars.py` → clean; `check-maps-forest.py` → all 6 domains clean; `verify-blender.py` → SKIP (no Blender), exit 0. MAP got `lesson_file: 02-authoring-and-blender-export.html`; map page + indexes regenerated.

Doc-review corrections (`.scratch/review/*.md`) folded: `.blend`→bpy-script, oracle material-assertion, export-extension list. #312/#313/#314 remain on the frontier (they prereq #310, not this).

## Notes

- Empirically verify export settings against the target Blender version before publishing.
- **Doc-review (2026-09-05, `.scratch/review/blender-manual-verify.md` vs local latest RST):** the
  4.5-fetched research is substantially accurate — channel mapping / +Y-up / animation Mode / Sampling
  all confirmed verbatim. ADDITIVE corrections to fold in when authoring: the export-extension list
  must include **`EXT_meshopt_compression`, `KHR_animation_pointer`, `KHR_materials_dispersion`** (the
  4.5 fetch predated them); there's now a **Meshopt compression panel** beside Draco. `.blend`→bpy-script
  and the oracle material-assertion decisions above come from `.scratch/review/glb-artifact-gen.md`.
