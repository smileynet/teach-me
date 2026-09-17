---
id: "350"
title: "Make review and lifecycle history rebuildable and versioned"
status: done
priority: high
type: feature
blocked_by: ["349"]
tags: ["arch-review", "sr", "data-model"]
validation_criteria:
  - "A local SR projection can be reconstructed from its event log"
---

# Make review and lifecycle history rebuildable and versioned

## Intent

Make the learner's review and lifecycle history an auditable, versioned local event stream with a rebuildable schedule projection.

## Context

`review_card` writes the mutable card before appending a lossy event. Events use ID prefixes, omit scheduler/version and result state, and lifecycle transitions are unrecorded. That prevents reliable recovery, migration, and analytics.

## What to build

Design a versioned event schema and local projection. Record review and lifecycle actions before or atomically with projection updates, and supply deterministic rebuild/migration behavior.

## Acceptance criteria

- [x] Every event has an event ID, UTC timestamp, full card ID, action/rating, scheduler version, and sufficient result state to replay it.
- [x] Suspend, reset, retire, and other lifecycle operations are represented in the same event model.
- [x] Rebuilding the projection from a fixture event stream produces the expected due dates, intervals, ease factors, and lifecycle state.
- [x] Interrupted or malformed writes recover without accepting a partially applied review.
- [x] Existing prefix-ID review logs have an explicit migration or unsupported-version diagnostic.
- [x] Fixture tests cover replay, reset, lifecycle transitions, and duplicate/missing-event behavior.

## Resolution

Local learner progress now uses `.user/learning-records/sr-events.sqlite3`: immutable,
versioned events and their disposable `card_projection` are committed in one SQLite
transaction. Review and lifecycle commands emit the same event model; canonical card
definitions remain shared JSONL. Old local state imports as snapshot events when safe,
and prefix-ID history without a state snapshot reports a clear unsupported diagnostic.

Evidence: `python -m pytest tools/test_questions_local_state.py -q` → 8 passed;
`mise run verify` → 55 tests, 20 interactive checks, and 5 Ink transcript fixtures passed.
