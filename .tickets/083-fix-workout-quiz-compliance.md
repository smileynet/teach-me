---
id: "083"
title: "Fix: workout quiz pages — add questions to meet 5+ minimum and 3+ types"
status: open
blocked_by: []
priority: medium
---

# Fix: workout quiz pages — add questions to meet 5+ minimum and 3+ types

## Problem

All 3 workout-fundamentals quiz pages have only 4 questions and 2 question types (explain + apply). The scaffold requires 5-9 questions and at least 3 different types.

## Affected files

- `examples/workout-fundamentals/lessons/quiz/0001-progressive-overload-quiz.html`
- `examples/workout-fundamentals/lessons/quiz/0002-recovery-and-adaptation-quiz.html`
- `examples/workout-fundamentals/lessons/quiz/0003-programming-basics-quiz.html`

## What to build

For each quiz page:
1. Add 1-3 more questions to reach minimum 5
2. Add at least one `predict` or `quick-check` type question (currently only explain + apply)
3. Add new questions to the SR JSONL file as well

## Acceptance criteria

- [ ] Each quiz page has 5+ questions
- [ ] Each quiz page uses 3+ distinct question types
- [ ] New questions also added to `learning-records/questions/workout-fundamentals.jsonl`
- [ ] `mise run verify` passes
