---
id: "218"
title: "Lesson: Albedo Posterization in Blender Nodes (0016)"
type: feature
status: open
priority: high
blocked_by: ["217"]
parent: "216"
tags: [mktoon, blender]
---

# Lesson: Albedo Posterization in Blender Nodes (0016)

## What to build

A substantial lesson teaching floor-divide quantization in Blender's shader node editor — the same math that discretizes lighting in the toon shader, applied to texture colors.

### Lesson arc

1. Connect to prior knowledge: `floor(NdotL * N) / N` in the shader quantizes lighting → same math on albedo quantizes color
2. Build the posterize node chain step by step: Image Texture → Scale(N) → Floor → Scale(1/N)
3. Show the visual result on Barrel_01 albedo at N=4, N=8, N=16 — too few = loss of form, too many = still noisy
4. Introduce the +0.5/N offset trick to center bands (avoids dark-biased quantization)
5. Compare Method A (Vector Math Floor) vs Method B (Separate RGB + Greater Than) — when each is appropriate
6. Build a reusable node group ("Posterize RGB") with exposed N parameter
7. Connect to next lesson: posterization reduces count but doesn't control WHICH colors survive → palette snapping

### Key concept

> Posterization and toon banding are the same operation applied at different stages: one quantizes lighting in the shader, the other quantizes texture color in the prep stage. Matching their band counts produces visual harmony.

### Code deliverables

- Blender node group: "Posterize RGB" (input: Color, N; output: Posterized Color)
- Screenshot comparison: N=4, N=8, N=16 on Barrel_01 diff texture

### Exercise

"Your toon shader uses 4 bands. You posterize the albedo to 4 levels. The result looks flat and lifeless. Why? What N value would preserve enough texture detail while still harmonizing with 4-band shading?"

## Acceptance criteria

- [ ] Lesson file: `examples/godot-gamedev/lessons/blender-texture-prep/02-albedo-posterize.html`
- [ ] Node chain built step-by-step with code blocks showing Blender node connections
- [ ] Visual comparison at 3 band counts (N=4/8/16 on Barrel_01 — Blender Emit bake, or inline-SVG schematic fallback)
- [ ] Node group created and documented (reusable) — as a bpy Python node-setup script (text, diffable), NOT a raw .blend
- [ ] Explains truncate-vs-round: `floor(x*N)/N` (mirrors the shader) then the canonical `floor(x*(N-1)+0.5)/(N-1)` as an improvement (preserves white)
- [ ] Connects floor-divide math to `posterize_albedo.gdshader:13` (the shader equivalent), NOT configurable_banding (that's a `/(N-1)` lighting-band form)
- [ ] Color-space gotcha documented: input texture Color Space (sRGB "Color" vs "Non-Color") changes band distribution; must be pinned for reproducibility
- [ ] SR questions generated (3-5 cards)
- [ ] Reference artifact: bpy node-setup script at `reference/code/albedo-posterize/`
- [ ] Tier-1 numpy posterize oracle wired into `mise run verify` (validates the taught math without Blender)

## Corrected findings (2026-08-27, subagent research + shader audit)

Evidence: `.scratch/subagent-review/lesson218-grounding.md`, `.scratch/subagent-research/{posterize-math,posterize-node-prior-art,blender-headless}.md`.

### Math — the spec's "+0.5/N offset trick mirrors the shader" is FALSE
- `posterize_albedo.gdshader:13` = `floor(tex_color * n) / n` — plain truncating `/N`, no offset. This IS the shader equivalent; mirror `color_levels` (default 4, range 2–16).
- No albedo shader uses a +0.5 offset; the only +0.5 in the codebase is a Half-Lambert *lighting* remap. → **Teach `floor(x*N)/N` as "what the shader does," then present `floor(x*(N-1)+0.5)/(N-1)` (round-to-nearest, exactly N levels, preserves black AND white) as the deliberate improvement — framed honestly, not as a mirror.**
- Do NOT use the `/(N-1)` divisor from configurable_banding — that's a lighting-band choice, wrong for albedo.

### Method B is thresholding, not posterization
- Separate RGB + Greater-Than = at most 2 levels/channel (8 colors, cube corners); does not scale to N bands. → Teach **Method A (Vector Math Multiply(N)→Floor→Multiply(1/N))** as the general posterize tool; present Method B as a special-case 2-tone hard cut WITH decision criteria (per visual-teaching steering), not an equal alternative.

### Color space is a required gotcha
- sRGB "Color" textures decode to linear before math nodes → bands cluster in shadows; "Non-Color" spreads them perceptually. Must pin the input Color Space explicitly or results aren't reproducible.

### Validation — Blender 5.2.0 LTS IS available
`C:\Program Files\Blender Foundation\Blender 5.2\blender.exe` (mise shim is broken; use the full path). All three tiers feasible:
- **Tier 1 (CI gate, no Blender):** numpy oracle for `floor(x*N)/N` + `floor(x*(N-1)+0.5)/(N-1)` — assert level counts + N=4 endpoints `{0,.333,.667,1.0}`. Wire into `mise run verify`.
- **Tier 2:** `blender -b --python check_nodes.py` asserts the node group's sockets + Scale→Floor→Scale wiring (the bpy script is also the downloadable artifact).
- **Tier 3:** headless Emit-bake N=4/8/16 on Barrel_01, human-reviewed, committed as PNGs (NOT a CI gate). Do NOT build a regex node-linter.

## Research context

**From blender-bake-nodes research:**

Method A — Math Floor (most common):
```
Image Texture → Vector Math: Scale(N) → Vector Math: Floor → Vector Math: Scale(1/N) → Base Color
```
- Colors range 0–N after multiply, floor cuts decimals, divide remaps to 0–1
- Source: BSE #304301

Method B — Separate RGB + Greater Than:
- For hard-edge posterization with manual per-channel threshold control
- Separate RGB → each channel through Math "Greater Than" → Combine RGB
- Source: BSE #101750

**From toon-texture-pipelines research:**
- Strategy D (Posterization): `color = floor(albedo * levels + 0.5) / levels`
- "Apply BEFORE lighting for color palette reduction; apply AFTER lighting for cel-shading bands"
- Quick stylization, good for prototyping; combine with stepped lighting for full cel look

**Key Blender constraint:**
- Shader nodes work in EEVEE viewport preview but baking requires Cycles
- For baking posterized result: use Emit pass (captures color without lighting influence)
- Set bake Samples to 1-16 (flat shading needs minimal samples)
