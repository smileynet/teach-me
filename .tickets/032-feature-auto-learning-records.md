---
id: "032"
title: "Feature: auto-generate learning records from sustained SR mastery"
status: open
priority: medium
blocked_by: []
type: feature
---

# Feature: auto-generate learning records from sustained SR mastery

## What to build

When a concept's SR cards sustain high intervals (>3 months) across multiple reviews, automatically write a learning record documenting demonstrated mastery. This closes the loop between SR performance and the learning-record system that drives zone-of-proximal-development calculations.

## Why

Currently learning records are written manually during Socratic gates. SR data is a more objective signal — if someone has correctly recalled a concept 4+ times over 3+ months, that's demonstrated retention, not just in-session fluency.

## Design sketch

1. `sr-lifecycle.py` (or a new `sr-graduate.py`) scans for cards meeting mastery criteria
2. Criteria: interval ≥ 90 days AND 3+ successful reviews AND no lapses in last 2 reviews
3. Groups related cards by lesson_id/section to form a coherent learning record
4. Writes `learning-records/NNNN-mastery-<concept-slug>.md` with:
   - What was demonstrated (derived from card prompts)
   - Evidence (review dates, intervals achieved)
   - Source lesson reference
5. Marks cards as `mastered: true`

## Open questions

- What interval threshold? 90 days? 180 days?
- Should it auto-write or propose and let the agent/learner confirm?
- How to derive a meaningful concept name from card prompts?
- Should multiple related cards consolidate into one learning record?

## Acceptance criteria

- [ ] Cards meeting mastery criteria detected automatically
- [ ] Learning record generated with evidence (dates, intervals)
- [ ] Cards marked as mastered after record written
- [ ] Links back to source lesson
- [ ] teach skill reads new learning records for ZPD calculation
