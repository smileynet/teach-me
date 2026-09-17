---
id: "365"
title: "Serialize same-card SR event writes"
status: open
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

- [ ] Concurrent same-card reviews either serialize into a valid ordered event stream or return a documented retryable conflict; no raw SQLite error reaches a caller.
- [ ] Concurrent reviews of different cards preserve both events and projections.
- [ ] Regression tests cover same-card and different-card process/thread contention.
- [ ] The event/projection transaction remains local-only and replayable.
