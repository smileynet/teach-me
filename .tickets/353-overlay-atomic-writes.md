---
id: "353"
title: "Make local progress overlay writes atomic and concurrency-safe"
status: done
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

- [x] A concurrent-update test preserves all 100 independently addressed records across repeated runs.
- [x] Readers never observe a truncated or partially serialized overlay.
- [x] Writes use a same-filesystem temporary file and atomic replacement with documented Windows behavior.
- [x] Malformed or interrupted local state produces a recoverable diagnostic without silently discarding valid records.
- [x] Status and SR local persistence share the documented atomic-write contract or explicitly justify different requirements.
- [x] Regression tests exercise process/thread contention and recovery paths.

## Resolution

The private status overlay now serializes full read-modify-write operations with a
retained OS-backed lock, then writes an fsynced same-directory temporary file and
atomically replaces the target. Windows sharing violations are retried boundedly for
both writers and readers; malformed documents surface a recovery diagnostic and the
server returns 503 rather than silently resetting progress. ADR-0018 records why this
small JSON overlay uses that contract while SR uses transactional SQLite.

Evidence: `python -m pytest tools/test_overlay_persistence.py -q` → 8 passed;
`mise run verify` → 62 tests plus interactive and transcript checks passed.
