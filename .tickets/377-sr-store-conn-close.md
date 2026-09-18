---
id: "377"
title: "Close SR event-store sqlite connections deterministically"
status: in_progress
blocked_by: []
priority: low
type: fix
tags: ["sr", "tools", "resource-hygiene", "risk-review"]
validation_criteria:
  - "No SR entry point strands an open sqlite connection on success, error, or abandoned iteration"
---

# Close SR event-store sqlite connections deterministically

## Intent

Event-store connections close on a deterministic path instead of relying on GC/process exit.

## Context (found 2026-09-18 risk review of the 2026-09-16/17 window)

`tools/questions.py` uses `with _connect() as connection:` throughout — but sqlite3's
`Connection` context manager only commits/rolls back; it does NOT close. Connections close at
GC or process exit. Mostly harmless for short-lived CLI runs, but two spots are worse:

- `iter_events()` (`tools/questions.py:406-410`) yields INSIDE the `with` block — a consumer
  that abandons the generator mid-iteration keeps the connection (and its read snapshot) open
  until GC.
- Long-lived callers (a future serve-process integration) would accumulate connections.

The pattern predates the window but was substantially extended by `e750b1b` (event-store
rewrite) and `c3e11bb` (retry loop reuses one connection across attempts — that one is fine).
Low priority: current consumers are CLIs that exit promptly.

## What to build

Wrap connection lifetime explicitly — e.g. `contextlib.closing(_connect())` composed with the
transaction `with`, or a small helper — so every entry point (`record_card_event`,
`rebuild_projection`, `read_cards`, `iter_events`) closes on all paths. For `iter_events`,
use `contextlib.closing` + `try/finally` around the generator body (or `yield from` inside a
closing context) so abandonment closes too.

## Acceptance criteria

- [ ] All `_connect()` call sites close the connection on success, exception, and generator abandonment
- [ ] `iter_events` half-consumed then garbage-collected leaves no open connection (testable via `sqlite3.Connection` instrumentation or a stress loop checking `PRAGMA`-side locks release)
- [ ] Existing suites stay green (`tools/test_questions_local_state.py`, `tools/test_sr_event_serialization.py`)

## References

- Commits `e750b1b`, `c3e11bb`; `tools/questions.py:168-171, 319-331, 406-410, 419-431`
