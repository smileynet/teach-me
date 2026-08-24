---
id: "195"
title: "Godot fundamentals domain (shared prereqs for all tracks)"
status: backlog
blocked_by: []
priority: medium
type: feature
---

# Godot fundamentals domain (shared prereqs for all tracks)

## Problem

Multiple lesson tracks require basic Godot knowledge (nodes, scenes, signals, GDScript basics, editor navigation) but each currently either:
- Assumes it (ink+Godot track, future tracks)
- Teaches it inline (godot-gamedev lessons 01-02)
- Skips it (shader tracks start at spatial shaders)

There's no shared, self-contained "Godot basics" domain that any specialized track can prereq.

## What to build

A standalone `godot-fundamentals.MAP.md` domain covering the minimum Godot knowledge needed to begin ANY Godot-based lesson track. Intentionally shallow and broad — not a full game dev curriculum.

### Proposed topics (5–6 lessons)

| Topic | Why it's a prereq |
|-------|-------------------|
| Editor navigation & project structure | Every track assumes you can open scenes, find the inspector, run the project |
| Nodes & the scene tree | Shaders attach to MeshInstance3D; ink UI needs Control nodes; everything is nodes |
| GDScript fundamentals | Signals, variables, functions, _ready/_process — the scripting baseline |
| Signals & communication | godot-ink uses signals; shader materials use set_shader_parameter; UI needs signal wiring |
| Resources & file system | Shaders are resources, ink stories are resources, materials are resources |
| Running & debugging | Play button, output panel, debugger basics — needed for any interactive lesson |

### Relationship to existing content

- `godot-gamedev` lessons 01–02 (nodes-and-scenes, gdscript-fundamentals) cover similar ground but are framed as "building toward a game." The fundamentals domain would be shorter, more focused on "just enough to start a specialized track."
- Could potentially **extract from** 01-02 rather than rewriting — reframe the same content as standalone prereqs.
- All specialized tracks (shaders, ink, future tracks) would prereq this domain rather than specific lessons from godot-gamedev.

### MAP structure

```yaml
domain: godot-fundamentals
description: "Just enough Godot to begin any specialized track — editor, nodes, GDScript, signals, resources"
depth: 0
parent: null
leads_to:
  - godot-gamedev
  - godot-toon-shaders
  - godot-mktoon
  - ink-godot
```

## Design decisions to make

1. **Extract from existing or write fresh?** Lessons 01-02 in godot-gamedev cover nodes and GDScript. Do we restructure those as the fundamentals domain (breaking godot-gamedev's numbering) or write parallel shorter versions?
2. **How shallow?** "Just enough" for ink integration is less than "just enough" for shader writing. Do we target the lowest common denominator or the union?
3. **Include editor tour?** Some tracks (shaders) need inspector + shader editor. Others (ink) need the scene tree + script editor. Cover both?

## Acceptance criteria

- [ ] `godot-fundamentals.MAP.md` exists as a standalone domain
- [ ] 5–6 lessons covering the shared Godot prerequisite knowledge
- [ ] At least two existing tracks (godot-mktoon, ink-godot) prereq this domain
- [ ] No content duplication with godot-gamedev (either extracted or differentiated)
