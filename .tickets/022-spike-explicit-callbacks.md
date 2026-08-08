---
id: "022"
title: "Spike: explicit callbacks to prior lessons"
status: open
priority: high
blocked_by: []
type: spike
---

# Spike: explicit callbacks to prior lessons

## Hypothesis

When a concept from a prior lesson reappears, explicitly naming it ("Remember from Lesson 1: snapshots are frozen file views") prevents confusion and reinforces retention. GDQuest does this aggressively with code comparisons and verbal callbacks.

## What to build

Since we only have one lesson currently, this spike focuses on the teach skill guidance + a synthetic example showing how lesson 2 would reference lesson 1 concepts.

1. Update teach skill: when referencing prior concepts, name the lesson and restate briefly
2. Write a short mock opening for a hypothetical "Lesson 2" that demonstrates the callback pattern
3. Include the expandable reminder variant for concepts 3+ lessons old

## Baseline

Current teach skill says "read learning records to calculate ZPD" but doesn't prescribe HOW to reference prior learning in lesson prose.

## Compare against

- Does the callback feel natural or forced?
- Is the restatement brief enough to not patronize?
- Does the expandable reminder work for "maybe you forgot" situations?

## Acceptance criteria

- [ ] Teach skill documents callback pattern with examples
- [ ] Mock lesson-2 opening demonstrates the technique
- [ ] Comparison presented: lesson with callbacks vs without
