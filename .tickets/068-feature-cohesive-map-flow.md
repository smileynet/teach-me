---
id: "068"
title: "Feature: cohesive map flow — suggestion banner, status sync on generation"
status: done
priority: high
blocked_by: []
type: feature
tags: [platform]
---

# Feature: cohesive map flow

## What to build

Three changes that close the loop between generation, navigation, and status:

### 1. "Start here" / "Continue with" suggestion banner on map page
- If no topics started: banner above graph with "Start here: [topic]" button
- If topics in progress: "Suggested next: [topic]" in the nav area
- Reads from `/api/map/{domain}` (uses `get_next_suggestion()`)

### 2. Update MAP.md status after successful generation
- After generation completes (done event, exit_code 0): POST to `/api/map/{domain}/{slug}/status`
- Endpoint calls `update_status(path, slug, 'in-progress')` from the parser
- MAP.md becomes consistent with dynamic detection (single source of truth)

### 3. `/api/map/{domain}/{slug}/status` endpoint
- POST with `{"status": "in-progress" | "complete"}` body
- Calls `update_status()` from map_parser.py
- Returns 200 on success, 404 if domain/slug not found, 400 if invalid status

## Acceptance criteria

- [x] Map page shows suggestion banner with correct topic name
- [x] Clicking suggestion opens the detail panel or starts generation
- [x] After generation completes, MAP.md file shows updated status
- [x] Returning to map page after generation: node is blue AND MAP.md is consistent

## Resolution (2026-08-12)

- POST `/api/map/{domain}/{slug}/status` endpoint added
- Suggestion banner reads from `/api/map/{domain}` (get_next_suggestion)
- finish() POSTs status update before auto-navigating
- Validated: curl + Playwright, zero errors, mise run verify passes

## Validation

- **Integration:** POST to `/api/map/data-analytics/compute-engines/status` with `{"status": "in-progress"}` → verify MAP.md file changed → GET `/api/map/data-analytics` → verify topic status updated
- **E2E (Playwright):** Load map page → verify suggestion banner shows a topic name → click a gray node → generate (mock) → verify redirect → navigate back to map → verify node is blue and MAP.md was updated
