---
id: "327"
title: "godot-asset-pipeline topic 4: lod-and-import-optimization"
status: open
blocked_by: ["305", "326"]
validation_criteria:
  - "Lesson 04: from a working game object → 'fill a scene → framerate tanks' → auto mesh-LOD (meshoptimizer), threshold/bias, HLOD visibility ranges, occlusion, collision-shape perf. Decision callout: LOD-or-not by asset role. Cites gltf-format t6 Draco/meshopt. Lands at same object performant at scale"
  - "Runnable artifact (dense mesh, LOD-enabled) + asset:validate-gd L4 assertion (ImporterMesh LOD count>1; collision shape type matches role)"
  - "Reference doc + SR cards + glossary JSON; passes mise run verify"
tags: ["content"]
---

# godot-asset-pipeline topic 4: lod-and-import-optimization

## Context

Track spiral topic 4 (#305). win → complication → resolution → win. Design:
`.scratch/proposals/305-godot-asset-pipeline-setup.md`.

## What to build

- **Start from the win**: "You have a working game object with collision."
- **Harder case**: "You fill a scene with it and the framerate tanks."
- **Resolve**: automatic mesh-LOD (meshoptimizer) on import + threshold/bias; HLOD visibility ranges;
  occlusion culling via the `-occ` occluders from topic 3; collision-shape perf (primitive vs convex
  vs trimesh). **Decision callout**: LOD-or-not / which collision shape, by asset role. Cites
  gltf-format t6 for Draco/meshopt.
- **Land back**: the same object, now performant at scale.
- Optional Q5 spike (separate): Blender-free Tier-1 LOD oracle if wanted.

## Acceptance criteria

- [ ] Lesson `04-lod-and-import-optimization.html` in the spiral shape; LOD/collision Decision callout with criteria
- [ ] Runnable artifact (dense mesh, LOD-enabled) + `asset:validate-gd` L4 assertion (`ImporterMesh` LOD count > 1; collision shape type matches role)
- [ ] Reference doc + SR cards + glossary JSON
- [ ] Passes `mise run verify`
