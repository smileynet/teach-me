---
id: "295"
title: "Topic: blender-gltf-character-export (rigged meshes + armatures + per-clip actions)"
status: open
blocked_by: ["294"]
priority: medium
validation_criteria:
  - "Lesson teaches Blender glTF export of rigged meshes/armatures + Animation Mode=Actions, Export Deformation Bones Only, Y-up/T-pose"
  - "References (not repeats) blender-texture-prep bake-and-export color-space slice"
tags: ["content"]
---

# Topic: blender-gltf-character-export (rigged meshes + armatures + per-clip actions)

Export a rigged character and its animation clips cleanly from Blender to glTF — the
mesh/armature/animation counterpart to the texture-only export taught in
`blender-texture-prep`.

> **Prereqs:** #294 (you know how Godot imports the pieces; now produce them).

## Source

`pipeline_guide.md` §2 + `guide_sources.md` §2; `examples/animation_test.md` (export+merge
mechanics). Note: two Blender manual pages 403 to fetchers — glTF-Blender-IO repo is the
fallback source of truth (record this).

## What to teach

- **Prep that prevents 90% of surprises:** Y-up / −Z-forward axis, triangulate, apply
  transforms, reset to T-pose (Model export considerations).
- **Base model export:** Selected Objects, Use Rest Position Armature, mesh + skeleton only.
- **Clip export:** **Animation Mode = "Actions"** (each action → its own clip) or NLA
  tracks; enable sampling + **Export Deformation Bones Only**.
- **The shared-skeleton prerequisite:** every clip must share the base model's exact
  skeleton (keep "Rename Bones" OFF) or tracks bind to the wrong bones — verify bone lists
  at import. Retargeting (`bone_map` + SkeletonProfileHumanoid) only when skeletons differ.
- **Material/texture gotchas:** Blender backface-culling default → Godot Cull Mode =
  Disabled; emissive needs Blender ≥3.2.
- **Reference, do not repeat:** `blender-texture-prep/bake-and-export` already covers glTF
  color-space slots — frame this as "you learned texture round-trip; now the full scene
  round-trip adds meshes + armatures + animations."

## Runnable artifact (ADR-0010)

An exported base-model `.glb` + at least one clip `.glb` (or the equivalent via the
`.blend`/`.fbx` sources), importing 1:1 in Godot. Headless-import validated. Downloadable
finals under `reference/code/blender-gltf-character-export/` (note: `.glb` are LFS-tracked
binaries — confirm the repo's LFS/asset policy).

## Acceptance criteria

- [ ] Lesson teaches export prep, base-vs-clip export settings, Actions/NLA, Export Deformation Bones Only, the shared-skeleton prerequisite, and material gotchas
- [ ] Explicitly references (does not duplicate) blender-texture-prep bake-and-export
- [ ] Runnable artifact: exported base + clip glTF importing 1:1, headless-import validated; downloadable finals under reference/code/
- [ ] Blender manual 403 + glTF-Blender-IO fallback noted
- [ ] `mise run verify` + check-topic-completeness pass; MAP.md gets lesson_file on completion

## Research-backed content notes (from #293 dispatch — see `.scratch/research/char-blender-export.md`)

- **The #1 failure is missing/collapsed animations** → author each clip as its own **named
  NLA track** (push down actions) before export. This is the single most-reported break.
- **Export settings checklist:** Limit-to-Selected + Use Rest Position Armature + Export
  Deformation Bones Only (+ **Sampling** when baking constraint/IK motion). `[L6:reported]`
- **Cross-skeleton sharing is a Godot-4-specific problem** (Bone Rest is baked into pose
  values). Solve via the importer **Retarget** section: BoneMap + SkeletonProfileHumanoid +
  Rest Fixer (esp. **"Overwrite Axis"**), or the Realtime Retarget module to preserve rests.
  `[L4:verified — official Retargeting docs]`
- **Explicit-export seam (DOGWALK, first-party):** teach export as a *deliberate* step and the
  glTF as the **inspection seam** — reject silent `.blend` auto-import. This is the *why*
  behind ADR-0001, not just the how.
- **5 items to empirically verify against the target Blender+Godot version BEFORE publishing**
  (flagged L6, not yet L4): Actions-vs-NLA reliability on current Blender 4.x; exact
  AnimationLibrary import toggles; Apply-Transform recommendation; + 2 more in the scratch doc.
  Do a real export/import spike as part of authoring — don't ship community-reported settings
  unverified.

## Notes

- The shared-skeleton check is the one hard prerequisite for #296's library merge to work.
