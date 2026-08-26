---
id: "027"
title: "Spike: scaffold withdrawal (reduce hand-holding over time)"
status: done
priority: high
blocked_by: ["022"]
type: spike
tags: [platform]
---

# Spike: scaffold withdrawal

## Hypothesis

As lessons progress, explicitly withdrawing hand-holding ("From here on, I won't re-explain X") signals growth and reduces redundancy. GDQuest does this by replacing full explanations with expandable reminders, and explicitly acknowledging the transition.

## What to build

1. Document the pattern in the teach skill:
   - Concept demonstrated 1-2 times → full explanation
   - Concept demonstrated 3+ times → expandable reminder + name only
   - Transition is EXPLICIT: "You've seen this pattern before — I'll just reference it from now on"
2. Show a mock example: how lesson 5 would reference a concept from lesson 1 differently than lesson 2 does
3. Tie to learning records: the teach skill checks how many times a concept has appeared

## Baseline

Current teach skill treats every lesson independently. No mechanism to reduce explanation depth as familiarity grows.

## Compare against

- Does the withdrawal feel earned or abrupt?
- Does the expandable reminder catch learners who genuinely forgot?
- Is the explicit transition reassuring or jarring?

## Acceptance criteria

- [x] Teach skill documents the three stages (full → reminder → reference)
- [x] Mock example shows the progression across hypothetical lessons
- [x] Learning record integration described (how to count prior appearances)
- [x] Comparison presented

## Depends on

Ticket 022 (explicit callbacks) — withdrawal builds on the callback pattern.
