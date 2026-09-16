---
id: "340"
title: "Keep topic signals stable across map rerenders"
status: open
priority: medium
blocked_by: ["338"]
type: fix
tags: ["arch-review", "frontend"]
validation_criteria:
  - "A forced parent rerender preserves topic signal identity and status"
  - "MapView has no state-changing side effect in its render body"
  - "mise run visual-qa exits 0"
---

# Keep topic signals stable across map rerenders

## Problem

`store.js` owns module-global signals while `MapView` calls `initTopicStates()` in its render
body. A rerender can replace signals and discard state or subscriptions.

## Context

Read `assets/components/store.js`, `MapView.js`, `TopicCard.js`, and `UnifiedView.js`. ADR
0005 keeps the current Preact/Signals stack; do not introduce a generalized state framework.

## What to build

Tie topic-state initialization to an explicit lifecycle. The same map preserves signal
identity; intentionally loading another map replaces obsolete entries predictably.

## Acceptance criteria

- [ ] `MapView` does not mutate the store in its render body
- [ ] Same-map rerenders preserve signal identity and values
- [ ] Loading another map removes obsolete entries without retaining cross-map state
- [ ] Focused automated tests cover both cases
- [ ] `mise run visual-qa` and `mise run verify` exit 0

## Resolution

TBD
