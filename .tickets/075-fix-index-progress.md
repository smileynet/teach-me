---
id: "075"
title: "Fix: index page progress rings — read live data from /api/map"
status: open
priority: high
blocked_by: []
type: feature
---

# Fix: index page progress rings

## Problem

Index page shows hardcoded "0/7", "0/8", "0 complete". Should read from `/api/map/{domain}` for each domain card to show actual completion state.

## What to build

On page load, fetch `/api/map/{domain}` for each domain card and update:
- Progress ring: fill proportional to complete/total
- Status text: "N complete · M in progress"
- Ring number: "N/total"

## Acceptance criteria

- [ ] Progress rings show actual complete count (not hardcoded 0)
- [ ] Status text updates to reflect MAP.md state
- [ ] Works without server (graceful fallback to static values)

## Validation

- **E2E (Playwright):** Load index → verify data-analytics shows "2 complete" (matching MAP.md) → verify ring shows 2/7
