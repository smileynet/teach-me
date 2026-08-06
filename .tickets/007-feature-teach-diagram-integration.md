---
id: "007"
title: "Feature: integrate diagrams into teach skill"
status: open
priority: medium
blocked_by: ["001", "006"]
type: feature
---

# Feature: integrate diagrams into teach skill

## What to build

Update the teach skill so it naturally produces inline SVG diagrams when authoring lessons. Based on spike results.

## Changes (proposed, update after spikes)

- Add "Diagrams in Lessons" guidance to SKILL.md
- Instruct agent to produce an inline SVG for every architectural concept
- Reference the chosen tooling (drawsvg helper, D2, or raw SVG — determined by spikes)
- Add diagram preferences to NOTES.md template

## Acceptance criteria

- [ ] Teach skill SKILL.md mentions diagram creation
- [ ] Next lesson generated includes at least one inline SVG
- [ ] Diagrams follow visual teaching steering rules
