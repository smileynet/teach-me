---
id: "082"
title: "Fix: add lesson-actions.js to all example lessons"
status: done
blocked_by: []
priority: high
---

# Fix: add lesson-actions.js to all example lessons

## Problem

All 5 example lesson pages are missing `lesson-actions.js` — the script that provides the bottom nav bar (← Back to map, Take the Quiz, Mark Complete). Without it, lessons have no interactive navigation.

## Affected files

- `examples/oidc-rust/lessons/0001-oidc-auth-flows.html`
- `examples/oidc-rust/lessons/0002-token-anatomy.html`
- `examples/workout-fundamentals/lessons/0001-progressive-overload.html`
- `examples/workout-fundamentals/lessons/0002-recovery-and-adaptation.html`
- `examples/workout-fundamentals/lessons/0003-programming-basics.html`

## What to build

Add before `</body>` in each lesson (after glossary.js, before theme-toggle.js):

```html
<script src="../assets/lesson-actions.js"
  data-map-page="{domain}-map.html"
  data-domain="{domain-slug}"
  data-topic-slug="{topic-slug}"></script>
```

## Acceptance criteria

- [x] All 5 lessons include lesson-actions.js with correct data attributes
- [x] `mise run verify` passes
- [x] Bottom nav bar renders in browser (← map, quiz, mark complete)

## Resolution (2026-08-12)

TBD
