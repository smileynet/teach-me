---
id: "350"
title: "Make review and lifecycle history rebuildable and versioned"
status: in_progress
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

- [ ] Every event has an event ID, UTC timestamp, full card ID, action/rating, scheduler version, and sufficient result state to replay it.
- [ ] Suspend, reset, retire, and other lifecycle operations are represented in the same event model.
- [ ] Rebuilding the projection from a fixture event stream produces the expected due dates, intervals, ease factors, and lifecycle state.
- [ ] Interrupted or malformed writes recover without accepting a partially applied review.
- [ ] Existing prefix-ID review logs have an explicit migration or unsupported-version diagnostic.
- [ ] Fixture tests cover replay, reset, lifecycle transitions, and duplicate/missing-event behavior.
