---
id: "189"
title: "Lesson 0011: Wrapped Lighting and Noise Bias"
status: done
blocked_by: ["188"]
priority: high
---

# Lesson 0011: Wrapped Lighting and Noise Bias

## Win statement

"You can soften the shadow terminator with wrapped lighting and add organic edge variation with noise bias — and explain why full wrap eliminates banding entirely."

## Prereqs

- Lesson 0010 (gooch-shading): Gooch endpoints, lit_factor driving color ramp

## Acceptance criteria

- [x] Lesson HTML at `examples/godot-gamedev/lessons/0011-wrapped-lighting-noise.html`
- [x] Reference shader at `examples/godot-gamedev/reference/code/wrapped-lighting-noise/wrapped_noise_banding.gdshader`
- [x] README.md in the reference/code directory
- [x] Shader compiles via Godot headless
- [x] Glossary entries: wrapped-lighting, noise-bias, toggle-pattern
- [x] Exercise tests the win statement (misconception: full wrap = no banding)
- [x] check-lesson.py passes
