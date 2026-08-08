---
id: "024"
title: "Spike: challenge/exercise component"
status: open
priority: high
blocked_by: ["021"]
type: spike
---

# Spike: challenge/exercise component

## Hypothesis

Challenges ("try it yourself" with progressive hints) build application skills that quizzes don't. Quizzes test recall; challenges test whether the learner can USE what they learned. GDQuest uses a three-tier model: quiz → practice → project.

## What to build

1. Design the challenge HTML pattern (using `<details>` from ticket 021)
2. Write a challenge for lesson 1: "Draw the manifest chain for a given query"
3. Write a `challenge` skill that knows when and how to add challenges to lessons
4. CSS for challenge blocks (distinct from quizzes — different visual treatment)

## Baseline

Currently lessons end with a quiz (recall-testing). No "apply this knowledge" exercises exist.

## Compare against

- Does the challenge feel achievable with just the lesson content?
- Are progressive hints the right UX (vs just showing the answer)?
- Does it feel distinct from quizzes or confusing alongside them?

## Acceptance criteria

- [ ] Challenge HTML pattern designed and demonstrated in lesson 1
- [ ] Progressive hints work via `<details>` nesting
- [ ] `challenge` skill created with guidance on when to use
- [ ] Visual distinction between challenge blocks and quiz blocks
- [ ] Before/after comparison presented

## Depends on

Ticket 021 (collapsible details) — hints use `<details>` pattern.
