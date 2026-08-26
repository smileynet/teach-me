---
id: "023"
title: "Spike: reading level constraint (Grade 8-10)"
status: done
priority: high
blocked_by: []
type: spike
tags: [platform]
---

# Spike: reading level constraint

## Hypothesis

Targeting Grade 8-10 reading level (15-20 words/sentence, no clause stacking, no idioms) makes lessons accessible to non-native speakers and reduces cognitive load for everyone. GDQuest explicitly targets this and it's a stated design choice for their audience.

## What to build

1. Audit lesson 1's current reading level (count sentence lengths, identify complex constructions)
2. Rewrite 3-5 sentences that exceed the constraint to show the before/after
3. Add the constraint to the teach skill
4. Optionally: a simple `tools/reading-level.py` script that flags sentences > 25 words

## Baseline

Lesson 1 was written by an agent without a reading level constraint. Some sentences are likely fine; others may be dense.

## Compare against

- Do simplified sentences lose precision?
- Does the lesson feel "dumbed down" or just clearer?
- Is the constraint practical for technical topics?

## Acceptance criteria

- [x] Lesson 1 audited with sentence length data
- [x] 3-5 sentences rewritten to demonstrate the constraint
- [x] Teach skill documents the rule
- [x] Before/after comparison presented
