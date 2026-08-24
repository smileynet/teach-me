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

- [ ] Lesson HTML at `examples/godot-gamedev/lessons/0011-wrapped-lighting-noise.html`
- [ ] Reference shader at `examples/godot-gamedev/reference/code/wrapped-lighting-noise/wrapped_noise_banding.gdshader`
- [ ] README.md in the reference/code directory
- [ ] Shader compiles via Godot headless
- [ ] Glossary entries: wrapped-lighting, noise-bias, toggle-pattern
- [ ] Exercise tests the win statement (misconception: full wrap = no banding)
- [ ] check-lesson.py passes
