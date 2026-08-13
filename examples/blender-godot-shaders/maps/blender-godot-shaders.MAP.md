---
domain: blender-godot-shaders
description: "Build stylized forest environments using Blender shaders and Godot's shader language, inspired by the Esoteric Ebb art style"
generated: 2026-08-12
depth: 0
parent: null
leads_to:
  - procedural-worldbuilding
  - godot-vfx-particles
  - hand-painted-texturing
---

# Blender → Godot Shader Pipeline (Esoteric Ebb Style)

## Orientation

You'll learn to create stylized 3D forest environments by combining Blender's shader nodes for authoring with Godot's shader language for real-time rendering. The Esoteric Ebb style — camera-projected hand-painting over 3D geometry with limited palettes — is the target aesthetic. By the end, you can produce a repeatable pipeline from Blender blockout to playable Godot scene.

## Topics

### esoteric-ebb-breakdown
- **title:** Esoteric Ebb Art Style Breakdown
- **why:** You need a clear visual target before building shaders — understanding the projection-painting technique and palette philosophy grounds every decision
- **scope:** lightweight
- **prereqs:** []
- **status:** not-started

### blender-npr-shaders
- **title:** Blender NPR Shader Fundamentals
- **why:** ShaderToRGB → ColorRamp is the foundation of every stylized material you'll build
- **scope:** substantial
- **prereqs:** []
- **status:** not-started

### stylized-foliage-materials
- **title:** Stylized Foliage & Environment Materials
- **why:** Forests are foliage-heavy — radial normals, procedural color variation, and alpha masking are the core techniques
- **scope:** substantial
- **prereqs:** [blender-npr-shaders]
- **status:** not-started

### baking-for-export
- **title:** Baking Stylized Materials for Game Export
- **why:** Blender's shader nodes don't export — you need to bake the look into textures that survive the pipeline
- **scope:** substantial
- **prereqs:** [blender-npr-shaders]
- **status:** not-started

### godot-shader-language
- **title:** Godot Shader Language (GDShader)
- **why:** Everything real-time — wind, toon lighting, fog — lives in Godot's shaders, and you haven't written them before
- **scope:** substantial
- **prereqs:** []
- **status:** not-started

### blender-to-godot-pipeline
- **title:** Blender → Godot Export Pipeline
- **why:** Understanding what transfers via glTF (and what doesn't) determines where each piece of work belongs
- **scope:** lightweight
- **prereqs:** [baking-for-export, godot-shader-language]
- **status:** not-started

### godot-environment-shaders
- **title:** Godot Environment Shaders (Wind, Fog, Toon, Outlines)
- **why:** The final forest scene needs dynamic wind on foliage, atmospheric fog, and consistent stylized lighting — all shader-driven in Godot
- **scope:** deep
- **prereqs:** [godot-shader-language, blender-to-godot-pipeline]
- **status:** not-started
