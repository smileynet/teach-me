---
id: "365"
title: "Serialize same-card SR event writes"
status: done
blocked_by: []
priority: high
tags: ["arch-review", "sr", "data-model"]
---

# Serialize same-card SR event writes

## Intent

Prevent concurrent reviews of one card from reading the same predecessor and creating
an avoidable SQLite foreign-key failure or stale transition.

## Context

`record_card_event` reads `card_projection.last_event_id` before `BEGIN IMMEDIATE`.
Two browser or CLI writers can therefore derive events from the same predecessor. The
event table preserves correctness by rejecting one write, but the application does not
yet retry or make the serialization boundary explicit. The #353 persistence review
identified this while checking alignment between status JSON and local SR storage.

## What to build

Acquire the SQLite write transaction before reading the card projection, derive the
next event inside it, and make same-card contention deterministic to callers.

## Acceptance criteria

- [x] Concurrent same-card reviews either serialize into a valid ordered event stream or return a documented retryable conflict; no raw SQLite error reaches a caller — `record_card_event` now takes `BEGIN IMMEDIATE` before reading the projection; busy writers wait (explicit busy_timeout), retry with backoff (bounded), and exhaustion raises retryable `EventStoreError`, never raw `sqlite3.OperationalError`
- [x] Concurrent reviews of different cards preserve both events and projections — covered by `test_different_card_thread_contention_preserves_every_event` and the cross-process test's `solo-card` writer
- [x] Regression tests cover same-card and different-card process/thread contention — `tools/test_sr_event_serialization.py`: 8-thread same-card barrier test (single ordered chain, projection agrees, rebuild clean), 6-thread different-card test, spawn-process test mixing same-card and different-card writers, and a prolonged-external-lock test asserting the retryable-conflict contract
- [x] The event/projection transaction remains local-only and replayable — no schema change; events still append-only with predecessor chain; `rebuild_projection` still replays deterministically (now also under an explicit write txn); ADR-0018 carries a contention note

## Resolution (2026-09-17)

Investigation corrected the ticket's premise: the same-predecessor race does NOT
produce an SQLite FK error — a stale predecessor is a valid event id, so both writers
commit and silently FORK the chain; the fork then poisons every future rebuild/read
permanently ("missing or out-of-order predecessor", no repair path). A second bug
compounded it: `_connect`'s `INSERT OR IGNORE` opened a read transaction that blocked
other writers' commits, and serialized-but-stale-derived `result_state` failed replay
revalidation. Fixes in `tools/questions.py`: (1) write txn acquired before the
projection read; (2) reviewed results derived INSIDE the txn from the projected state
(matching `_apply_event`'s replay contract, so serialized writers chain correctly);
(3) connect is DDL-only (no stray write lock); (4) explicit busy_timeout + bounded
retry + retryable `EventStoreError`; (5) `rebuild_projection` runs under an explicit
`BEGIN IMMEDIATE`. WAL deliberately not enabled (tiny CLI-only store; avoids
`-wal`/`-shm` sidecars). Verified: `pytest tools/test_sr_event_serialization.py
tools/test_questions_local_state.py` → 12 passed; new file wired into `mise run verify`.
