---
id: "164"
title: "Steering: code block pedagogy and narrative framing convention"
status: done
blocked_by: []
priority: high
---

# Steering: code block pedagogy and narrative framing convention

## Context

Lessons were dropping code blocks without narrative context — readers didn't know what changed, why, or how blocks related to each other. The toon-banding lesson review (session 2026-08-19) established the pattern: lead-in → bridge → connect-back.

Also: lessons need domain subfolders (`lessons/{domain}/NN-slug.html`) instead of flat global numbering.

## What to build

Apply steering and documentation updates that shape all future content generation:

1. `visual-teaching.md` — new "Code Block Pedagogy" section
2. `AGENTS.md` — constraint rows + domain subfolder explanation
3. `examples/README.md` — updated workspace tree
4. `CONTRIBUTING.md` — two convention bullets

## Acceptance criteria

- [x] `visual-teaching.md` has Code Block Pedagogy section with lead-in/bridge/connect-back pattern
- [x] `AGENTS.md` constraints table includes no-code-without-framing and no-flat-lessons rules
- [x] `AGENTS.md` workspace section explains domain subfolder layout
- [x] `examples/README.md` tree shows `{domain-slug}/NN-slug.html`
- [x] `CONTRIBUTING.md` mentions both conventions

## Resolution (2026-08-19)

Applied all steering/docs changes for narrative framing and domain subfolder conventions
