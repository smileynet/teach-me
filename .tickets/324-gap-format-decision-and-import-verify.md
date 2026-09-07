---
id: "324"
title: "godot-asset-pipeline topic 1: format-decision-and-import-verify"
status: open
blocked_by: ["305", "323"]
validation_criteria:
  - "Lesson 01: from the happy-path win → format decision (glTF/FBX-ufbx/.blend/OBJ for Godot) + Blender export prep (backface culling, normals, origin) + verify ingest. Decision callout with when-to-use-which. Builds in prose on gltf-format anatomy/import"
  - "Runnable artifact (prop exported multiple ways) + asset:validate-gd L1 assertion (correct cull_mode round-trip)"
  - "Reference doc + SR cards + glossary JSON; passes mise run verify"
tags: ["content"]
---

# godot-asset-pipeline topic 1: format-decision-and-import-verify

## Context

Track spiral topic 1 (#305). Structure: win → complication → resolution → win. Design:
`.scratch/proposals/305-godot-asset-pipeline-setup.md`. Shrunk ~40% from the pre-split scope — the
glTF anatomy/exporter walkthrough now lives in the `gltf-format` domain; this is the Godot-side
*decision + verify*.

## What to build

- **Start from the win** (topic 0): "You imported one glTF prop and it worked."
- **Harder case**: "But what about FBX, `.blend`, OBJ — and why did one come in inside-out / black /
  mis-scaled?"
- **Resolve**: the format decision *for Godot* (glTF recommended; FBX via ufbx; `.blend` direct
  needs Blender; OBJ/DAE limits) + Blender export prep (enable Backface Culling, face normals,
  origin/pivot) + verifying Godot ingested it. **Decision callout** at this fork with concrete
  when-to-use-which criteria (not "it depends").
- **Land back**: a prop that renders correctly *on purpose*, format chosen deliberately.
- Prose links: builds on gltf-format `gltf-anatomy-and-the-standard` + `consuming-gltf-engine-import`.

## Acceptance criteria

- [ ] Lesson `01-format-decision-and-import-verify.html` in win→complication→resolution→win shape; Decision callout with real criteria
- [ ] Runnable artifact (prop exported multiple ways) + `asset:validate-gd` L1 assertion (correct `cull_mode` round-trip)
- [ ] Reference doc + SR cards + glossary JSON
- [ ] Passes `mise run verify`
