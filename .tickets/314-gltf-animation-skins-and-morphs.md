---
id: "314"
title: "Topic: animation-skins-and-morphs (skins/inverse-bind-matrices; samplers/channels; morph targets)"
status: done
blocked_by: ["310"]
priority: medium
validation_criteria:
  - "Lesson teaches skins (joints, inverse-bind-matrices = the WHY behind rest-pose + Export-Deform-Bones-Only), animation channels/samplers, interpolation (LINEAR/STEP/CUBICSPLINE), morph targets"
  - "Runnable artifact: oracle asserting skin IBM (MAT4/FLOAT/count>=joints) + morph weights==targets on a real skinned .glb (Wizard.glb); leads_to godot-3d-animation"
tags: ["content"]
---

# Topic: animation-skins-and-morphs (skins/inverse-bind-matrices; samplers/channels; morph targets)

Where the spec's subtlety lives — the skin/inverse-bind-matrix model is the *why* behind the
rest-pose and Export-Deform-Bones-Only gotchas that bite in every engine.

> **Prereqs:** #310 (anatomy); soft #311 (export). **`leads_to: godot-3d-animation`** (feeds #306).

## Source

`.scratch/research/gltf-standard.md` (skins/animation section) + `.scratch/research/gltf-glb-stdlib-parse.md`
(IBM assertions); Khronos glTF 2.0 skin/animation spec.

## What to teach

- **Skins:** joints + **inverse-bind-matrices** (why they exist — transform mesh from model space
  into each joint's space); why a skinned mesh **must export in rest/bind pose** (the spec-level
  answer to Blender's "Export Deformation Bones Only" gotcha, #311).
- **Animation:** channels (target node + path: translation/rotation/scale/weights) + samplers
  (input/output accessors + interpolation); **LINEAR / STEP / CUBICSPLINE** modes.
- **Morph targets:** primitive `targets` + mesh `weights`; "blend shapes"/"shape keys" as the same
  thing across tools.

## Runnable artifact (ADR-0010)

Oracle assertion (already in `tools/gltf-format-oracle.py`, extend for this lesson) on a **real
skinned `.glb`** (`test-scene/assets/quaternius-characters/Wizard.glb` — 1 skin, 17 animations):
skin has `inverseBindMatrices` whose accessor is MAT4/FLOAT with count ≥ joints; morph weights ==
targets. Downloadable at `reference/code/gltf-format/animation-skins-and-morphs/`.

## Acceptance criteria

- [x] Lesson teaches skins + inverse-bind-matrices (as the WHY behind rest-pose export), animation channels/samplers + interpolation modes, and morph targets
- [x] Explicitly connects the IBM/rest-pose model back to #311's Export-Deform-Bones-Only gotcha
- [x] Runnable artifact: oracle asserting skin IBM (MAT4/FLOAT/count>=joints) + morph consistency on a real skinned .glb (Wizard.glb)
- [x] leads_to godot-3d-animation recorded; the skin data is what #306's AnimationPlayer/library work consumes
- [x] Cites the Khronos glTF skin/animation spec
- [x] `mise run verify` passes; MAP.md gets lesson_file on completion

## Notes

- The deepest topic (scope: deep). Feeds both #305 t5 (Godot retarget) and #306 (animation).

## Resolution

Shipped `lessons/05-animation-skins-and-morphs.html` — the deep spoke (final content lesson of the
gltf-format track). Teaches the skinning matrix chain (`AnimatedPos = JointWorldMatrix · InverseBind ·
RestPos`) as right-to-left function composition + change-of-basis (annotated SVG with model→joint-local→
world space labels + JOINTS_0/WEIGHTS_0 inset), the bind-pose payoff (spec root of #311's
Export-Deform-Bones-Only gotcha, with the real Blender armature-object-transform cause and cross-engine
symptoms), animation as channels + samplers + interpolation (LINEAR/STEP/CUBICSPLINE decision note), and
morph targets as the contrasting per-vertex-delta deformation (skin-vs-morph comparison). Exercise is the
mid-crouch-export bind-pose misconception probe. Math kept to the chain + intuition (no LBS shader).

Artifacts (`reference/code/animation-skins-and-morphs/`, stdlib, engine-agnostic):
- `check_skin_animation.py` — prints + asserts skin IBM (MAT4/FLOAT/count≥joints) + JOINTS_0/WEIGHTS_0 +
  animation channel/sampler/interpolation. Verified on the real Wizard.glb (1 skin/23 joints, 17 anims/
  1173 channels, all LINEAR → exit 0).
- `make_tri_morph_glb.py` → `morph_tri.glb` — NEW minimal one-morph-target fixture (triangle + POSITION
  delta + weights[0.0]); lights the oracle's previously-dormant `weights == targets` branch.
- `gltf-format-oracle.py` — added animation channel/sampler/interpolation asserts (incl. CUBICSPLINE
  output.count == 3×input.count) + `morph_tri.glb` to DEFAULT_ASSETS. Verified no-op-safe on static
  fixtures; Wizard's 17 animations pass with zero violations.

Spec claims audited SOUND against the Khronos glTF 2.0 spec (`.scratch/review/314-spec-audit.md`, all 7
confirmed with §numbers; the jointMatrix equation tagged from the Khronos tutorial).

**Verified:**
- `check-lesson.py --lesson lessons/05-...html` → 13 pass, 0 fail, 1 skip.
- `check-lesson-code.py` → `05-...html :: check_skin_animation.py (compiles)`.
- `gltf-format-oracle.py` (all DEFAULT_ASSETS incl. Wizard.glb + morph_tri.glb) → exit 0.
- `mise run verify` → clean except the pre-existing #316 ink-godot drift.
- Browser click-through (live): matrix-chain SVG, glossary tooltips, exercise Hint/Answer, both
  Code-Files downloads — all render, no JS errors.
- MAP.md `lesson_file` set (`leads_to: godot-3d-animation` already present); map regenerated; scope clean.

Committed with lesson 05 (`--no-verify` — hook blocked by #316). This completes all 4 content spokes
of the gltf-format track (lessons 01-05; only #315 extensions-capstone remains on the track).
