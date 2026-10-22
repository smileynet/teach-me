# Shader outline / distance-field reference exploration (2026-09-03)

Distilled synthesis of 4 cloned reference repos, for a future decision on expanding the
`godot-toon-shaders` outline track. NOT yet ticketed — awaiting sign-off on the JFA topic.
Raw per-repo findings were in `.scratch/shader-explore/` (deleted at cleanup; rehydrate the
repos via `mise run rehydrate` — REFERENCES.md has the 4 git-clone lines).

## Current state (what already exists)

`godot-toon-shaders` MAP: `advanced-outlines` (lesson 0007) INTRODUCES JFA distance fields +
dual-viewport color-ID; `jfa-distance-fields` is a listed EXPANSION OPPORTUNITY (deep dive:
JFA impl, CompositorEffect, multipass). Outlines already taught: inverted-hull + screen-space
edge detection (0006). The 4 open shader tickets (#216/#222/#253/#227) are all Blender
texture-prep for the mktoon track — UNRELATED to these outline findings (clean separation).

## The 4 repos

- **pink-arcana/godot-distance-field-outlines** — BEST teaching reference. JFA/SDF outlines,
  3 READMEs + diagrams + perf graphs, MIT + live demo. Ships the algorithm TWICE: a
  CanvasItem screen-space version (any renderer / web — the natural intro artifact) AND a
  CompositorEffect compute version (Forward+, the deep artifact). Dynamic-width pass count,
  depth fade. → PRIMARY spine for a jfa-distance-fields topic.
- **Madalaski/godot-jfa-madalaski** — real JFA CompositorEffect + compute, SEPARABLE X/Y JFA,
  depth-as-seed (no color-ID viewport). Forward+ only, no README. → SECONDARY: cite for the
  separable-JFA optimization + depth-seed masking.
- **GarrettGunnell/Acerola-Compute** — NOT a technique: a compute-shader wrapper framework
  (custom `.acompute` lang + autoload + hot-reload). → cite-only TOOL; do NOT depend (custom
  shader-lang autoload = teaching hazard). Its CompositorEffect exposure example is an ideal
  minimal template for the compute-in-CompositorEffect plumbing.
- **Gamelogic-Code/Outlines** — UNITY (technique reference only). NOVEL vs teach-me:
  Difference-of-Gaussians (DoG) soft/sketchy outline; brute-force Max/dilation baseline;
  fused depth+ID+normal edge detection. Redundant: vertex extrusion, plain color-ID+JFA.

## Proposed updates (awaiting decision)

1. **HIGH — promote `jfa-distance-fields` expansion opp → a full topic** in godot-toon-shaders
   (new ticket under the track). Spine = pink-arcana; cite madalaski for separable/depth-seed.
   Two-tier artifact: intro = CanvasItem screen-space (web-safe); deep = CompositorEffect
   compute (Forward+). Validate via godot-validation (headless import + A/B); optional oracle
   asserts pass_count == ceil(log2(width)).
2. **LOW — new topic candidate: Difference-of-Gaussians (DoG) soft outlines** (from Gamelogic).
   A genuinely different aesthetic (soft/sketchy) vs current hard edges. Add as expansion opp
   first; promote if interest.
3. **LOW — update `advanced-outlines` (0007)**: fused depth+ID+normal edges (native Godot
   depth/normal buffers, not the RGB channel-packing hack); Max-dilation baseline to motivate
   JFA's O(log n) win.
4. **Acerola = cite-only** (tool, not topic).

## Gotchas (Godot 4 JFA)

Forward+ only (RenderSceneBuffersRD / normal_roughness); needs 4.3+ + Vulkan compute; RID
lifecycle must free on PREDELETE; 16-byte push-constant/UBO alignment; CompositorEffect can't
be keyframed (share a non-unique settings Resource on a Node). pink-arcana's CanvasItem path
avoids compute entirely (web-capable) but is fragile (many runtime CanvasLayers).