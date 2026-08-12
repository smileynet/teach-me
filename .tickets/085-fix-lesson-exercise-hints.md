---
id: "085"
title: "Fix: add hint <details> to workout lessons 0002 and 0003 exercises"
status: open
blocked_by: []
priority: low
---

# Fix: add hint details to workout lessons 0002 and 0003 exercises

## Problem

Workout lessons 0002 and 0003 have a "Check Your Understanding" exercise with only a `<details>` for the answer. The scaffold pattern includes a separate hint `<details>` that nudges reasoning before revealing the full answer.

## Affected files

- `examples/workout-fundamentals/lessons/0002-recovery-and-adaptation.html`
- `examples/workout-fundamentals/lessons/0003-programming-basics.html`

## What to build

Add a hint `<details>` before the answer `<details>`:
```html
<details>
<summary>Hint</summary>
<p>{{HINT_THAT_POINTS_TOWARD_REASONING}}</p>
</details>
```

## Acceptance criteria

- [ ] Both lessons have hint + answer in their exercise section
- [ ] Hint guides reasoning without giving away the answer
- [ ] `mise run verify` passes
