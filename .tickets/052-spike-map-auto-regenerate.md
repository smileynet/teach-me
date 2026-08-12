---
id: "052"
title: "Spike: auto-regenerate map page when lessons/questions are added"
status: open
priority: low
blocked_by: []
type: spike
---

# Spike: auto-regenerate map on status change

## What to test

After a lesson is generated or questions are written, can the map page automatically update its node colors and action buttons to reflect the new state?

## Approaches to test

### A. Post-hook in teach skill
After writing a lesson, the teach skill runs `mise run map:generate -- MAP.md` to rebuild the page.

### B. mise file watching
`mise run map:watch` watches `lessons/*.html` and `learning-records/questions/*.jsonl` — regenerates on changes.

### C. Status in MAP.md itself
The teach skill updates `status: in-progress` in MAP.md, then regenerates. This is the ticket-046 approach — map page regeneration is just a side effect.

## Questions to answer

1. Which trigger is simplest and most reliable?
2. Should the map page be git-committed after regeneration, or treated as ephemeral (regenerated on demand)?
3. How to detect "this topic now has a lesson" — by file existence, or by MAP.md status field?
4. Does the learner care about immediate visual feedback, or is "run `mise run map:generate`" sufficient?

## Success criteria

- [x] After creating a lesson file, the map page shows that topic's node in blue (in-progress) — done via dynamic /api/lessons detection on page load (no regeneration needed)
- [ ] After completing a quiz, the node turns green (complete)
- [x] The regeneration is triggered by a clear, documented mechanism — page load triggers detection; no regeneration needed for status
- [ ] No manual step beyond what the teach skill already does

## Partial resolution (2026-08-11)

Dynamic lesson detection on page load (via `/api/lessons` endpoint) makes the first and third criteria moot — the map page doesn't need regeneration to show status changes. Nodes turn blue when a matching lesson file is found. This means auto-regeneration is only needed for the SVG graph layout itself (adding/removing nodes), not for status updates.

Remaining: green state (quiz complete) detection. Likely needs `/api/questions` endpoint or similar.

## Validation (remaining work)

- **Integration:** `/api/questions/{slug}` endpoint checks if SR questions exist for a topic. Map page JS calls it to determine complete vs in-progress.
- **E2E (Playwright):** Create a lesson file + questions file for a topic → reload map page → verify node turns green (not just blue). Remove questions file → verify node stays blue (lesson exists but not complete).
