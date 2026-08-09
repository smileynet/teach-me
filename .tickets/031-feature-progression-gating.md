---
id: "031"
title: "Feature: gate lesson progression on retention threshold"
status: open
priority: medium
blocked_by: []
type: feature
---

# Feature: gate lesson progression on retention threshold

## What to build

Before advancing to the next lesson, the teach skill checks whether prior material has reached a target retrievability (e.g., 90%). If not, it surfaces due cards first and suggests reviewing before new material.

## Why

SRS retains but doesn't teach. If a learner moves forward while prior concepts are decaying, new material built on those foundations won't stick. Gating ensures the base is solid before adding weight.

## Design sketch

1. teach skill runs `python tools/sr-analytics.py <topic>` before writing a new lesson
2. If avg retrievability < threshold (configurable, default 85%), surface due cards instead of new material
3. Soft gate: inform the learner and recommend review, but don't block if they insist on continuing
4. After review session brings retrievability above threshold, proceed normally

## Open questions

- What threshold? 85%? 90%? Need real usage data to calibrate.
- Hard gate (block progression) vs soft gate (recommend but allow override)?
- Should it gate per-concept or per-topic average?
- How many sessions of data before the gate activates? (Don't gate lesson 2 when lesson 1 was yesterday)

## Acceptance criteria

- [ ] teach skill checks retrievability before producing new lessons
- [ ] Below-threshold surfaces due cards with explanation to learner
- [ ] Learner can override ("I want to continue anyway")
- [ ] Threshold configurable (in NOTES.md or workspace config)
- [ ] Gate doesn't activate until topic has 5+ reviewed cards
