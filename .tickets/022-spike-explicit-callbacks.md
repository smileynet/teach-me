---
id: "022"
title: "Spike: explicit callbacks to prior lessons"
status: done
priority: high
blocked_by: []
type: spike
---

# Spike: explicit callbacks to prior lessons

## Hypothesis

When a concept from a prior lesson reappears, explicitly naming it ("Remember from Lesson 1: snapshots are frozen file views") prevents confusion and reinforces retention. GDQuest does this aggressively with code comparisons and verbal callbacks.

## What to build

Lightweight: when the teach skill references a prior concept, include a one-sentence reminder inline. No formal "callback pattern" — just good writing practice.

1. Update teach skill: "When referencing a concept from a prior lesson, briefly restate it in one clause — don't assume the learner remembers."
2. Example: "The manifest list (the file that tracks which data files belong to this snapshot) also stores..."

That's it. No mock lessons, no expandable reminders (covered by 021 if needed), no formal framework.

## Acceptance criteria

- [x] ~~Teach skill documents callback pattern with examples~~ Simplified
- [x] Teach skill says: restate prior concepts briefly on reuse
- [x] One example in the skill showing good vs bad
- [x] ~~Mock lesson-2 opening~~ Removed — premature
