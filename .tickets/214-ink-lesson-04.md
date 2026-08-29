---
id: "214"
title: "Ink Lesson 08: Production Patterns"
status: in_progress
blocked_by: ["213"]
priority: high
tags: [ink]
---

# Ink Lesson 08: Production Patterns

Multi-story architecture, stateless-per-dialog, SVs as state bus, hub-and-spoke, combat-as-dialog. From Esoteric Ebb (286 stories, 500K words).

## Context
Final Phase-B lesson. Inherit the established pattern from lessons 05–07 (see #213's Context
block): file `examples/ink-godot/lessons/0008-production-patterns.html`, reference code at
`reference/code/production-patterns/`, single-step `continue_story()` accumulate loop (NEVER
maximal — #236), deterministic reference story with top-level `-> start` + golden transcript,
runtime-validated via `mise run ink:validate-gd` (add a lesson-08 harness check + sync-map entry).
Source material: the ebb-analyzer patterns (`.scratch/subagent-raw/review-ebb-*.md` from #193) —
tags-as-commands (#212) is the foundation this builds on. This is the capstone: multi-story
architecture where each dialog is stateless and Story Variables are the cross-story bus.

## Acceptance criteria

- [ ] Lesson `examples/ink-godot/lessons/0008-production-patterns.html` (Win + key-concept + SVG + glossary + exercise)
- [ ] Reference `.ink` story(ies): deterministic, compile 0/0, top-level `-> start`; golden transcript(s) committed
- [ ] README.md in `reference/code/production-patterns/`
- [ ] `mise run ink:validate` + `mise run ink:transcripts` pass
- [ ] `mise run ink:validate-gd` passes — harness check added for lesson 08
- [ ] Glossary terms annotated (Q15) + `check-lesson.py` passes
- [ ] 5 SR questions (ig-08-*); map + index regenerated (explicit `--output`)
