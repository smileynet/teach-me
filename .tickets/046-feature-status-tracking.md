---
id: "046"
title: "Feature: 'what's next?' suggestions on map page"
status: open
priority: low
blocked_by: []
type: feature
tags: [platform]
---

# Feature: status tracking + what's next

## What to build

After completing a subtopic (demonstrated via quiz-me or explicit "I'm done with X"), update MAP.md status. When asked "what's next?", suggest the best available topic.

## Design

### Status updates

- After first lesson in a topic: `not-started` → `in-progress`
- After quiz-me pass (or explicit "done"): `in-progress` → `complete`
- The teach skill writes the updated status to MAP.md after each change

### "What's next?" logic

1. Find all topics where `status != complete`
2. Filter to those whose `prereqs` are all `complete` (available now)
3. Rank by: most dependents first (unblocks the most of the map)
4. Suggest the top choice, offer the full available list

### Edge case: all available topics are in-progress

Suggest continuing the one with most recent activity, or offer to switch.

## Acceptance criteria

- [x] Status updates persist — via `/api/map/{domain}/{slug}/status`, which since #258 writes the gitignored `.user/` status overlay, NOT MAP.md (AC text amended 2026-09-17, #335; the endpoint itself shipped with 068/069)
- [x] "What's next?" never suggests topics with incomplete prereqs — get_next_suggestion (ticket 043/068)
- [x] Suggests the topic that unblocks the most downstream content — suggestion banner (ticket 068)
- [ ] Handles "all done" (triggers leads_to presentation)
- [ ] Handles "everything available" (offers choice, doesn't force)

## Update (2026-09-17, #335 re-scope)

The #335 triage line "all ACs already checked but status still open — close" was WRONG:
two ACs above remain unchecked. This ticket stays open scoped to exactly those two
items (both are completion-state UX and overlap #047's presentation work):
1. "All done" → trigger the leads_to / where-this-leads presentation.
2. "Everything available" (nothing in progress) → offer a choice rather than forcing one.
The three checked ACs were re-verified against source: the status endpoint writes the
overlay (`tools/serve.py` status route -> `tools/lib/overlay.py`), and the suggestion
banner renders from `get_next_suggestion`.

## Validation

- **Unit:** `update_status` + `load_map` round-trip: update a topic, reload, verify status persisted and other fields intact. `get_next_suggestion` with various status combos returns correct picks.
- **Integration:** `/api/map/{domain}` endpoint returns current topic statuses from MAP.md. POST to `/api/map/{domain}/{slug}/status` updates MAP.md. Verify with GET after POST.
- **E2E (Playwright):** Generate a topic → map page reloads → node is blue → click node → detail panel shows "Open lesson" (not generate). Set all topics to complete → verify "Where This Leads" section is highlighted/promoted.
