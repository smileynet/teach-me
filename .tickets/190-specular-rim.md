---
id: "190"
title: "Lesson 0012: Specular and Rim Lighting"
status: done
blocked_by: ["189"]
priority: high
---

# Lesson 0012: Specular and Rim Lighting

## Win statement

"You can add toon highlights using the threshold-smoothstep pattern applied two ways — Blinn-Phong for flat specular stamps, Fresnel for rim glow — and explain why both are additive on top of diffuse shading."

## Prereqs

- Lesson 0011 (wrapped-lighting-noise): complete toon diffuse pipeline

## Acceptance criteria

- [x] Lesson HTML at `examples/godot-gamedev/lessons/0012-specular-rim.html`
- [x] Reference shader at `examples/godot-gamedev/reference/code/specular-rim/specular_rim_banding.gdshader`
- [x] README.md in the reference/code directory
- [x] Shader compiles via Godot headless
- [x] Glossary entries: threshold-smoothstep, flat-specular, rim-lighting, fresnel
- [x] Exercise tests the win statement (misconception: size parameter inversion)
- [x] check-lesson.py passes
