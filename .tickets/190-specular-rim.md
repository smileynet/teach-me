---
id: "190"
title: "Lesson 0012: Specular and Rim Lighting"
status: open
blocked_by: ["189"]
priority: high
---

# Lesson 0012: Specular and Rim Lighting

## Win statement

"You can add toon highlights using the threshold-smoothstep pattern applied two ways — Blinn-Phong for flat specular stamps, Fresnel for rim glow — and explain why both are additive on top of diffuse shading."

## Prereqs

- Lesson 0011 (wrapped-lighting-noise): complete toon diffuse pipeline

## Acceptance criteria

- [ ] Lesson HTML at `examples/godot-gamedev/lessons/0012-specular-rim.html`
- [ ] Reference shader at `examples/godot-gamedev/reference/code/specular-rim/specular_rim_banding.gdshader`
- [ ] README.md in the reference/code directory
- [ ] Shader compiles via Godot headless
- [ ] Glossary entries: threshold-smoothstep, flat-specular, rim-lighting, fresnel
- [ ] Exercise tests the win statement (misconception: size parameter inversion)
- [ ] check-lesson.py passes
