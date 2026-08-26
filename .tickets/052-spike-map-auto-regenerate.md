---
id: "052"
title: "Spike: auto-regenerate map page when lessons/questions are added"
status: done
priority: low
blocked_by: []
type: spike
tags: [platform]
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
- [x] After completing a quiz, the node turns green (complete) — done via /api/questions detection on page load
- [x] The regeneration is triggered by a clear, documented mechanism — page load triggers detection; no regeneration needed for status
- [x] No manual step beyond what the teach skill already does — page load auto-detects

## Resolution (2026-08-12)

Full status lifecycle works without regeneration:
- Gray (not-started): no lesson file detected
- Blue (in-progress): lesson exists, no questions yet
- Green (complete): lesson + questions both exist

Implementation: `/api/lessons` + `/api/questions` endpoints called on page load.
Nav counter updates dynamically. Validated via Playwright.
