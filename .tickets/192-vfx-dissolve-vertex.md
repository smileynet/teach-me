---
id: "192"
title: "Lesson 0014: VFX Dissolve and Vertex Animation"
status: done
blocked_by: ["191"]
priority: high
---

# Lesson 0014: VFX Dissolve and Vertex Animation

## Win statement

"You can add map-based dissolve with a glowing border and vertex displacement with time-stutter — and explain why discard must live in fragment() (not light()) for both correctness and performance."

## Prereqs

- Lesson 0013 (outlines-overlays): complete toon pipeline with overlays

## Acceptance criteria

- [x] Lesson HTML at `examples/godot-gamedev/lessons/0014-vfx-dissolve-vertex.html`
- [x] Reference shader at `examples/godot-gamedev/reference/code/vfx-dissolve-vertex/vfx_toon.gdshader`
- [x] README.md in the reference/code directory
- [x] Shader compiles via Godot headless
- [x] Glossary entries: dissolve-effect, discard-keyword, time-stutter, vertex-displacement
- [x] Exercise tests the win statement (discard in light() misconception)
- [x] check-lesson.py passes
- [x] Final lesson in the MKToon track — marks completion of the 6-lesson arc
