---
id: "186"
title: "MKToon track setup: MAP, test-scene fixture, design decisions"
status: done
blocked_by: ["185"]
priority: high
tags: [mktoon]
---

# MKToon track setup: MAP, test-scene fixture, design decisions

## Context

Lessons 0003–0008 teach toon shading via post-process filtering (banding → outlines → Kuwahara). The MKToon track teaches the alternative: per-material authored NPR, building the look from scratch layer by layer. Source material: `D:\code\ebb-analyzer\shaders\godot\mk_toon_lite.gdshader`.

Subagent research (2026-08-23) at `.scratch/subagent-raw/ebb-*.md` confirmed the shader decomposes into 6 teachable layers with clear incremental progression.

## Design decisions (resolved 2026-08-23)

### 1. Build-up vs study → **Build from zero**
Learners write each layer themselves. The ebb-analyzer shader is reference ("here's how a shipped game does it"), not starting point.

### 2. MAP placement → **Sibling map, fork from toon-banding**
New `godot-mktoon.MAP.md` as a depth-1 child of `godot-gamedev`, sibling to `godot-toon-shaders`. Both branch from the `toon-banding` topic. This creates a visible fork on the parent map: "post-process path" vs "per-material path."

### 3. Test-scene → **New scene in existing project**
Add `mktoon_test.tscn` to `test-scene/scenes/`. Reuses existing Poly Haven PBR assets and headless validation pipeline.

### 4. Framing → **"Alternative approach: authored vs filtered"**
Explicitly positioned as a fork after `toon-banding`. Learner doesn't need to complete outlines/Kuwahara first.

### 5. Lesson numbering → **Continue at 0009**
Same `godot-gamedev` domain folder, sequential numbering. Filesystem stays simple.

### 6. Global map integration
The sibling-fork relationship is documented in #155 (global map) and #055 (cross-domain links) as the concrete use case for rendering parent maps with child-fork points.

## What to build

1. **`godot-mktoon.MAP.md`** — new map file with 6 topics, prereq link to `toon-banding`
2. **`mktoon_test.tscn`** — test scene with one Poly Haven mesh + placeholder ShaderMaterial
3. **Update `godot-toon-shaders.MAP.md`** — add `leads_to: [godot-mktoon]`
4. **Copy `mk_toon_lite.gdshader`** to `test-scene/shaders/reference/` as read-only reference
5. **Brief design note** in `.memory/` capturing the fork decision for future sessions

## Acceptance criteria

- [x] `examples/godot-gamedev/maps/godot-mktoon.MAP.md` exists with 6 topics and correct frontmatter
- [x] `godot-toon-shaders.MAP.md` updated with `leads_to` including `godot-mktoon`
- [x] `test-scene/scenes/mktoon_test.tscn` exists with at least one PBR mesh
- [x] Reference shader copied to test-scene (not modified — read-only comparison target)
- [x] `godot --headless --editor --import --quit --path test-scene` passes
- [x] Design decisions recorded in `.memory/adr/` or `.memory/`

## Downstream tickets (one per lesson)

| Ticket | Lesson | Core technique |
|--------|--------|---------------|
| #187 | 0009: Configurable toon banding | floor() quantization + smoothness + scale |
| #188 | 0010: Gooch warm/cool shadows | Color split replaces black shadows |
| #189 | 0011: Wrapped lighting + noise | Half-lambert + noise threshold bias |
| #190 | 0012: Specular + rim | Threshold-smoothstep pattern × 2 |
| #191 | 0013: Outlines + overlays | Inverted-hull companion shader + textures |
| #192 | 0014: VFX (dissolve, vertex) | Map-based dissolve + vertex displacement |

Each blocked by its predecessor. Created separately once this setup ticket is done.
