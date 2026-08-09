---
id: "024"
title: "Spike: challenge/exercise component"
status: done
priority: high
blocked_by: ["021"]
type: spike
---

# Spike: challenge/exercise component

## Hypothesis

Challenges ("try it yourself" with progressive hints) build application skills that quizzes don't. Quizzes test recall; challenges test whether the learner can USE what they learned. GDQuest uses a three-tier model: quiz → practice → project.

## What to build

A simple exercise pattern using `<details>` for optional practice. NOT required in every lesson — only added when the learner's mission involves *doing* (not just understanding).

1. HTML pattern: task description + progressive hints in `<details>` + solution in `<details>`
2. Light CSS for exercise blocks (distinct from quiz — maybe a left border)
3. Teach skill note: "Add a challenge when the mission involves application, not just comprehension"

No separate `challenge` skill needed — it's a paragraph in the teach skill.

## Acceptance criteria

- [x] HTML pattern demonstrated in lesson 1 (one exercise)
- [x] Progressive hints via `<details>`
- [x] Teach skill documents when to include exercises (mission-dependent)
- [x] ~~`challenge` skill created~~ Not needed — covered in teach skill
- [x] ~~Visual distinction~~ Minimal — left border is enough

## Depends on

Ticket 021 (collapsible details) — hints use `<details>` pattern.
