---
id: "217"
title: "Lesson: What Makes a Texture Toon-Unfriendly? (0015)"
type: feature
status: open
priority: high
blocked_by: []
parent: "216"
tags: [mktoon, blender]
---

# Lesson: What Makes a Texture Toon-Unfriendly? (0015)

## What to build

A lightweight orientation lesson that teaches learners to analyze PBR texture sets and identify what will fight toon shading — before they start fixing anything.

### Lesson arc

1. Show the Barrel_01 PBR textures under mk_toon_lite with default settings → "what looks wrong?"
2. Identify the three enemies: continuous gradients (noisy band edges), high-frequency detail (overwhelms flat regions), micro-detail normals (chattering shadows)
3. Explain which PBR channels matter for toon (albedo + normal) vs which to discard (roughness, metallic)
4. Show the AO channel as a hidden asset (future threshold_map)
5. Reference industry context: Guilty Gear and Genshin don't convert PBR — they author for toon from scratch. Our approach is the indie middle ground.

### Key concept

> PBR textures encode continuous physical properties. Toon shaders discretize lighting into bands. When continuous texture detail meets discrete shading, the texture wins — creating noise where the shader wants flat regions.

### Exercise

Show two textures side by side (one PBR-noisy, one simplified). Ask: "Which texture channels are creating problems under toon banding? What would you keep, discard, or simplify?"

## Acceptance criteria

- [ ] Lesson file: `examples/godot-gamedev/lessons/blender-texture-prep/01-texture-audit.html`
- [ ] Uses Barrel_01 diff + ARM textures as the primary example
- [ ] Diagram: PBR texture channels → which feed toon shader vs which are discarded
- [ ] Before screenshot: Barrel_01 with raw PBR diff under configurable_banding
- [ ] Identifies 3 specific problems (gradients, micro-detail, unnecessary channels)
- [ ] References the `mk_toon_lite.gdshader` uniform list (what slots need filling)
- [ ] SR questions generated (3-5 cards)

## Research context

**From toon-texture-pipelines research:**
- Redshift docs: "Tone mapping is the most important element — it allows direct control over lighting. PBR albedo can often be used directly."
- Guilty Gear: Single texture + ILM map replaces entire PBR set. Hand-painted from scratch, not converted.
- Strategy ranking: A (keep albedo, change lighting) → B (posterize albedo) → C (hand-paint control maps) → D (bake lighting — avoid)

**From existing-test-scene review:**
- ARM textures use channel packing: R=AO, G=Roughness, B=Metallic
- `mk_toon_lite` uses `render_mode specular_disabled` — roughness/metallic literally ignored
- Normal maps from Poly Haven exist (`_nor_gl_`) but aren't connected to any toon shader scene
- The shader declares 7 texture uniforms; all are empty in mktoon_test.tscn

**From MK.Toon requirements research:**
- Toon shaders don't need special base textures — standard albedo works
- Stylization is procedural (in shader math), not in texture content
- Normal maps can soften toon band edges (gotcha to document)
