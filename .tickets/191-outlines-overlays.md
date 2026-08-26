---
id: "191"
title: "Lesson 0013: Outlines and Artistic Overlays"
status: done
blocked_by: ["190"]
priority: high
tags: [mktoon]
---

# Lesson 0013: Outlines and Artistic Overlays

## Win statement

"You can add an inverted-hull outline via next_pass and shadow-weighted texture overlays — and explain why pipeline order (overlays before specular) matters for multiplicative vs additive effects."

## Prereqs

- Lesson 0012 (specular-rim): complete single-shader toon pipeline
- Lesson 0006 (toon-outlines): inverted hull concept (recalled, not re-taught)

## Acceptance criteria

- [x] Lesson HTML at `examples/godot-gamedev/lessons/0013-outlines-overlays.html`
- [x] Outline shader at `examples/godot-gamedev/reference/code/outlines-overlays/toon_outline_hull.gdshader`
- [x] Main shader at `examples/godot-gamedev/reference/code/outlines-overlays/overlays_banding.gdshader`
- [x] README.md in the reference/code directory
- [x] Both shaders compile via Godot headless
- [x] Glossary entries: artistic-overlay, shadow-weighted, outline-clip-offset, pipeline-order
- [x] Exercise tests the win statement (pipeline ordering misconception)
- [x] check-lesson.py passes
