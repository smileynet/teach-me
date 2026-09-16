---
id: "338"
title: "Refresh topic-map progress from the local overlay at load time"
status: open
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

- [ ] Back-navigation or reload updates topic status without regeneration
- [ ] Prerequisite met/unmet indicators use refreshed progress
- [ ] API failure retains embedded status without an uncaught error
- [ ] No learner progress enters committed HTML, MAP.md, or demo fixtures
- [ ] An automated browser test covers the freshness scenario
- [ ] `mise run verify` exits 0

## Out of scope

Cross-device sync, browser-local learner storage, and the derivation unification rejected by ADR 0017.

## Resolution

TBD
