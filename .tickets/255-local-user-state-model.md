---
id: "255"
title: "Minimal per-user overlay: gitignored sparse status map keyed by node ID"
status: open
blocked_by: ["258"]
priority: high
tags: ["platform"]
---

# Minimal per-user overlay: gitignored sparse status map keyed by node ID

## Why (this is the FLOOR, deliberately minimal)

Per owner direction (2026-08-29): the committed content graph is the first-class citizen
(#257); per-user state is a THIN, gitignored overlay whose only job is to keep user
state out of the committed tree, keyed back to the graph's node IDs. **No event-sourcing,
no serve write-API, no sync bridge** — that apparatus is deferred to #259 (backlog) and
nothing here depends on it. A user's overlay is just their local file; losing it is
acceptable (delete = reset progress).

This is the concrete store that #258's overlay-interface calls
(`overlay.get(node_id) -> {status, updated_at} | None`, `overlay.set(node_id, status)`).

## What to build

### 1. Overlay files (gitignored)
- **Progress overlay** — a single sparse JSON map keyed by the ULID node id:
  ```json
  { "schema": 1,
    "overlay": {
      "01J...metadata": { "status": "complete",    "updated_at": "2026-08-29T14:00:00Z" },
      "01J...ingest":   { "status": "in-progress", "updated_at": "2026-08-29T14:20:00Z" } } }
  ```
  Absent key = not-started. `status ∈ {not-started, in-progress, complete}` (read =
  "in-progress" is fine; keep the current lenient semantics). Location: `.user/` (ADR
  0012 private path), gitignored.
- **Quiz/SR state** — per-user, keyed by the SAME node ids (and card id where relevant),
  in a SEPARATE gitignored file under `.user/`. Keep it simple: the existing
  `learning-records/{questions,reviews}` shapes relocated under `.user/`, keyed by node
  id. No log-inversion (that's #259).

### 2. Overlay interface (used by #258's queries/endpoints)
- `overlay.load()` → sparse dict; `overlay.get(node_id)`; `overlay.set(node_id, status)`
  (stamps `updated_at`); `overlay.reset()` (delete file). Pure stdlib, on-disk JSON.
- serve.py status GET/POST (reworked in #258) read/write via this interface.

### 3. `.gitignore`
- Ensure `.user/` is gitignored (coordinate with #183/#184 which also touch `.user/`).

## Prereqs are INFORMATIONAL only (locked decision)
Do NOT gate/lock topics on prereqs. The overlay + graph together power a simple
"recommended prereqs: ✓ met / ○ not yet" indicator per topic (met = the prereq node's
overlay status is complete/in-progress). No availability locking, no blocked topics.

## Depends on
- **#258** (status removed from committed graph; readiness queries take the overlay arg).
  Transitively needs #257 (ULID node ids — the overlay's keys).

## Out of scope (moved to #259, backlog)
- Event-sourced review log, serve write-API beyond simple status GET/POST, browser
  IndexedDB store, export/import bridge, cross-device sync, File System Access API.

## Acceptance criteria

- [ ] A gitignored `.user/` overlay stores `{node_id → {status, updated_at}}` (sparse)
- [ ] Quiz/SR per-user state relocated under `.user/`, keyed by node id (no committed
      per-user state anywhere)
- [ ] Overlay interface (`load/get/set/reset`) is pure stdlib on-disk JSON; #258's
      queries + serve endpoints use it
- [ ] Topic view shows recommended-prereq met/unmet indicator (informational, no gating)
- [ ] Fresh clone (no `.user/`) = all topics not-started, nothing errors; deleting
      `.user/` resets progress cleanly
- [ ] `.user/` is gitignored; `git status` clean after marking topics complete
- [ ] `mise run verify` EXIT 0

## Validation

Mark topics complete → writes only to `.user/`, `git status` clean; delete `.user/` →
progress resets, no errors; a topic with an unmet recommended prereq shows the ○
indicator but is still fully accessible (no gating).
