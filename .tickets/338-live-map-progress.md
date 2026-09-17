---
id: "338"
title: "Refresh topic-map progress from the local overlay at load time"
status: done
priority: high
blocked_by: ["332"]
type: fix
tags: ["arch-review", "platform"]
validation_criteria:
  - "Playwright completes a lesson, returns to its map without regeneration, and observes updated status"
  - "Static map pages retain embedded fallback status when the overlay API is unavailable"
  - "mise run verify exits 0"
---

# Refresh topic-map progress from the local overlay at load time

## Problem

The 2026-09-16 architecture review found that lesson pages write progress live and aggregate
indexes fetch `/api/overlay`, but topic maps seed `store.js` only from generation-time page
data. This contradicts #258 and leaves map badges and prerequisite indicators stale.

## Context

Read #258, #279, `tools/generate_map_page.py`, `assets/components/MapView.js`, and
`assets/components/store.js`. Keep embedded data as the static/no-JS fallback. #332 must first
make status routing correct for every domain served from the library root.

## What to build

Join current local progress onto embedded topic data before initializing signals. Returning
from a completed lesson must show the new status without regenerating HTML.

## Acceptance criteria

- [x] Back-navigation or reload updates topic status without regeneration
- [x] Prerequisite met/unmet indicators use refreshed progress
- [x] API failure retains embedded status without an uncaught error
- [x] No learner progress enters committed HTML, MAP.md, or demo fixtures
- [x] An automated browser test covers the freshness scenario
- [x] `mise run verify` exits 0

## Out of scope

Cross-device sync, browser-local learner storage, and the derivation unification rejected by ADR 0017.

## Resolution

Map pages now carry the canonical MAP `domain` and, before `MapView` initializes its
signals, fetch `/api/map/{domain}` and replace only matching topic statuses. A failed or
unavailable request leaves the embedded demo/no-JS data intact.

Generation no longer reads `.user/status-overlay.json` or infers learner progress from
the presence of shared lesson artifacts. Its sole static status source is the committed
`demo-status.json` fixture, so per-user progress cannot enter generated map HTML, MAP.md,
or demo data.

`tools/test-library-status-api.py` now builds a throwaway library fixture, completes a
lesson through the real UI, verifies its map badge and a dependent prerequisite after a
reload, then aborts the status request and verifies the static fallback without a page
error. `tools/test_map_page.py` adds a conflicting demo/private-overlay regression.

Evidence: `python tools/test-library-status-api.py` → 11 map domains plus browser
persistence and fallback pass; `mise run verify` → 45 tests, 20 interactive checks, and
5 Ink transcripts pass (70.41s).
