---
id: "046"
title: "Feature: topic status tracking + 'what's next?' suggestions"
status: open
priority: low
blocked_by: ["043"]
type: feature
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

- [ ] Status updates persist in MAP.md
- [ ] "What's next?" never suggests topics with incomplete prereqs
- [ ] Suggests the topic that unblocks the most downstream content
- [ ] Handles "all done" (triggers leads_to presentation)
- [ ] Handles "everything available" (offers choice, doesn't force)

## Validation

- **Unit:** `update_status` + `load_map` round-trip: update a topic, reload, verify status persisted and other fields intact. `get_next_suggestion` with various status combos returns correct picks.
- **Integration:** `/api/map/{domain}` endpoint returns current topic statuses from MAP.md. POST to `/api/map/{domain}/{slug}/status` updates MAP.md. Verify with GET after POST.
- **E2E (Playwright):** Generate a topic → map page reloads → node is blue → click node → detail panel shows "Open lesson" (not generate). Set all topics to complete → verify "Where This Leads" section is highlighted/promoted.
