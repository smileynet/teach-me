---
id: "188"
title: "Lesson 0010: Gooch Warm/Cool Shadows"
status: done
blocked_by: ["187"]
priority: high
---

# Lesson 0010: Gooch Warm/Cool Shadows

## Win statement

"You can implement Gooch shading and explain why tinting shadows cool (instead of just darkening them) creates perceived depth — and why the dark_color must have non-zero channels to work."

## Prereqs

- Lesson 0009 (configurable-banding): floor-divide, smoothness, scale, lit_factor output

## Acceptance criteria

- [ ] Lesson HTML at `examples/godot-gamedev/lessons/0010-gooch-shading.html`
- [ ] Reference shader at `examples/godot-gamedev/reference/code/gooch-shading/gooch_banding.gdshader`
- [ ] README.md in the reference/code directory
- [ ] Shader compiles via Godot headless
- [ ] Glossary entries: gooch-shading, gooch-ramp-intensity, warm-cool-shadows
- [ ] Exercise tests the win statement (misconception: black dark_color = no effect)
- [ ] check-lesson.py passes
