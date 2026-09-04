---
domain: blender-texture-prep
description: "Convert PBR textures to toon-friendly assets in Blender — simplify albedo, author control maps, and export to Godot for the mktoon shader"
generated: 2026-08-26
depth: 1
parent: godot-gamedev
leads_to:
  - godot-mktoon
  - stylized-rendering
---

# Blender Texture Prep for Toon Shading

## Orientation

Toon shaders handle lighting procedurally — banding, specular, rim are all computed in real time. But photorealistic PBR textures fight the look: continuous gradients create noisy band edges, high-frequency detail overwhelms flat-color regions, and unused PBR channels (roughness, metallic) add confusion without contributing to the style.

This track teaches the **texture prep layer** between "I downloaded PBR assets" and "my scene looks stylized." You won't rebake lighting (that kills dynamic shadows) — you'll simplify the albedo, discard irrelevant PBR channels, and author the toon-specific control maps that production shaders expect but nobody provides.

The reference implementation is `mk_toon_lite.gdshader` — which declares uniforms for noise_map, threshold_map, hatching_dark_map, and sketch_map, all currently unpopulated in the test-scene. (The 1D lighting ramp is a separate mechanism in `toon_ramp.gdshader`, covered by its own topic — mk_toon_lite colors its bands via gooch, not a ramp.)

## Topics

### texture-audit
- **id:** 01M174TQPB723EMSEZPECA55MC
- **title:** What Makes a Texture Toon-Unfriendly?
- **why:** Before changing anything, you need to identify what in a PBR texture set fights toon shading — continuous gradients that create noisy band edges, micro-detail normals that chatter, and roughness maps the shader ignores entirely
- **scope:** lightweight
- **prereqs:** [toon-banding]
- **lesson_file:** blender-texture-prep/01-texture-audit.html

### albedo-posterize
- **id:** 01M174TQPB8QFQZ6A8D4WQ3HAB
- **title:** Albedo Posterization — Floor-Divide Quantization in Blender Nodes
- **why:** The same floor(x*N)/N math that quantizes lighting in the shader can quantize texture colors in Blender — reducing a photorealistic albedo to N color bands that harmonize with N-band toon shading
- **scope:** substantial
- **prereqs:** [texture-audit]
- **lesson_file:** blender-texture-prep/02-albedo-posterize.html

### palette-snap
- **id:** 01M174TQPBFQG4MTH62HANBFMD
- **title:** Palette Snapping — Color Ramp & 1D Lookup Tables
- **why:** Posterization reduces color count but doesn't guarantee aesthetic harmony — palette snapping maps every pixel to the nearest color in an artist-chosen palette, giving unified art direction across all assets
- **scope:** substantial
- **prereqs:** [albedo-posterize]
- **lesson_file:** blender-texture-prep/03-palette-snap.html

### toon-control-maps
- **id:** 01M174TQPBTDFW2AAZZXKCCWKN
- **title:** Authoring Toon Control Maps — Noise & Threshold
- **why:** mk_toon_lite samples two authored control maps that ship empty: a noise map that biases NdotL before banding to break up straight band edges, and a threshold map (seeded from the ARM texture's AO channel) that shifts the shadow boundary per-pixel
- **scope:** substantial
- **prereqs:** [texture-audit]
- **lesson_file:** blender-texture-prep/04-toon-control-maps.html

### ramp-band-textures
- **id:** 01M174TQPBD4AXH3MSNAF1CNPS
- **title:** Ramp Band Textures — 1D Lighting Ramps for toon_ramp.gdshader
- **why:** A ramp texture REPLACES floor-divide banding with a 1D lighting-curve lookup — the texture IS the light response, giving per-step color and width control. This is an alternative banding mechanism (toon_ramp.gdshader), a sibling of toon-banding, not a mk_toon_lite control slot
- **scope:** substantial
- **prereqs:** [toon-banding]
- **lesson_file:** blender-texture-prep/ramp-band-textures.html

### bake-and-export
- **id:** 01M174TQPB4KRM72DXG8GAZ3KJ
- **title:** Emit Bake & glTF Export — Blender to Godot Round-Trip
- **why:** Blender's Cycles Emit pass captures simplified color without lighting influence — the one bake type that produces textures safe for dynamic toon shading. The glTF export validates the full pipeline end-to-end.
- **scope:** substantial
- **prereqs:** [palette-snap, toon-control-maps]
- **lesson_file:** blender-texture-prep/05-bake-and-export.html

### wiring-the-shader
- **id:** 01M174TQPB5WJ7TT2EJ2YPXTZ4
- **title:** Wiring It All Up — Populate mk_toon_lite in Godot
- **why:** The pipeline isn't proven until every texture slot is populated and the scene renders correctly — this lesson takes the exported assets and connects them to the full mk_toon_lite shader with before/after proof
- **scope:** substantial
- **prereqs:** [bake-and-export, configurable-banding]
- **lesson_file:** blender-texture-prep/06-wiring-the-shader.html

## Expansion Opportunities

Subtopics that could become full topics if the track grows:

- **hand-painted-shadows** — Genshin-style directional shadow textures for faces; 2-channel (R/G) approach where each channel controls shadow shape at different light angles (surfaced in: toon-texture-pipelines research, Genshin analysis)
- **ilm-channel-packing** — Guilty Gear ILM maps: R=specular mask, G=shadow offset, B=specular size, A=inner lines. The AAA approach to per-pixel artistic control (surfaced in: GDC 2015 talk analysis)
- **matcap-textures** — Bake a sphere with desired lighting into a 2D texture, sample with view-space normals for metallic/hair luster effects without PBR (surfaced in: MK.Toon/MToon research)
- **tileable-overlay-textures** — Creating seamless hatching, sketch, and drawn overlay textures for mk_toon_lite's artistic modes (surfaced in: test-scene review — hatching_dark_map/sketch_map slots empty)
- **normal-editing-for-shadow-shape** — Transfer normals from simplified proxy mesh for clean geometric shadow boundaries; manual face-normal editing for characters (surfaced in: Guilty Gear GDC talk)
- **palette-swaps-at-runtime** — Keep palette lookup in the Godot shader (not baked) for runtime color theming; DCP addon's approach with Godot 4 spatial shader export (surfaced in: Dynamic Color Palette addon research)
