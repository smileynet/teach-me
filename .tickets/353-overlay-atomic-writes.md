---
id: "353"
title: "Make local progress overlay writes atomic and concurrency-safe"
status: in_progress
priority: high
type: bug
blocked_by: ["341"]
tags: ["arch-review", "persistence", "security"]
validation_criteria:
  - "Concurrent writes preserve every independently updated progress record"
---

# Make local progress overlay writes atomic and concurrency-safe

## Intent

Make local learner-progress persistence atomic so concurrent browser requests cannot erase one another.

## Context

The security deep dive reproduced read-modify-write loss: 100 distinct updates from 20 threads retained as few as two records. This affects the status overlay and establishes a persistence contract needed by local SR state.

## What to build

Use a same-directory atomic-write protocol plus appropriate process/thread coordination. Define recovery behavior for malformed or interrupted local files and reuse the contract for all mutable local overlays.

## Acceptance criteria

- [ ] A concurrent-update test preserves all 100 independently addressed records across repeated runs.
- [ ] Readers never observe a truncated or partially serialized overlay.
- [ ] Writes use a same-filesystem temporary file and atomic replacement with documented Windows behavior.
- [ ] Malformed or interrupted local state produces a recoverable diagnostic without silently discarding valid records.
- [ ] Status and SR local persistence share the documented atomic-write contract or explicitly justify different requirements.
- [ ] Regression tests exercise process/thread contention and recovery paths.
