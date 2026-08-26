---
id: "187"
title: "Lesson 0009: Configurable Toon Banding"
status: done
blocked_by: ["186"]
priority: high
tags: [mktoon]
---

# Lesson 0009: Configurable Toon Banding

## Win statement

"You can build a configurable banding shader with smoothness, scale, and threshold controls — and explain why `mix(banded, continuous, smoothness)` gives you soft N-band shading that neither smoothstep nor floor alone can achieve."

## Prereqs

- Lesson 0004 (toon-banding): modulo trick, step(), smoothstep approach, NdotL, max() accumulation

## Acceptance criteria

- [x] Lesson HTML at `examples/godot-gamedev/lessons/0009-configurable-banding.html`
- [x] Reference shader at `examples/godot-gamedev/reference/code/configurable-banding/configurable_banding.gdshader`
- [x] README.md in the reference/code directory
- [x] Shader compiles via Godot headless
- [x] SR questions in learning record
- [x] Glossary entries: configurable-banding, light-bands-scale, diffuse-smoothness, centering-trick
- [x] Exercise tests the win statement (near-transfer with misconception probe)
- [x] check-lesson.py passes
