---
id: "109"
title: "Embed mission context in index page header"
type: feature
status: done
priority: high
blocked_by: []
---

# Embed mission context in index page header

## What to build

The index page (All Lessons dashboard) should show the user's learning mission as a context block above the domain cards. Users should see WHY they're learning before WHAT topics exist — one glance, not a separate navigation step.

## Current state

- MISSION.md is served as raw markdown (unthemed, no navigation, dead end)
- Index page shows domain cards with no framing about the learner's goals
- The user has to know MISSION.md exists and navigate to it manually

## Desired state

- Index page header shows a condensed mission statement (from MISSION.md)
- If MISSION.md has a "Success Criteria" section, show the top 2-3 as a checklist
- No separate MISSION.md page needed — the index IS where you see your goals
- `generate_index_page.py` reads MISSION.md and includes it in the data island

## Acceptance Criteria

- [x] Index page shows mission context above domain cards
- [x] Reads from workspace/MISSION.md automatically
- [x] If MISSION.md is the generic template (no real content), shows a prompt to set goals
- [x] Styled consistently (not raw markdown)
- [x] Works with multiple domains (mission frames all of them)

## Context

- Current index generator: `tools/generate_index_page.py`
- IndexView component: `assets/components/IndexView.js`
- Mission file: `workspace/MISSION.md`

## Resolution (2026-08-13)

TBD
