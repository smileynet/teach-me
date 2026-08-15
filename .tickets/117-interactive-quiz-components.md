---
id: "117"
title: "Feature: Interactive quiz components — drag-and-drop, fill-in-blanks, matching"
status: done
blocked_by: ["127"]
---

# Feature: Interactive quiz components — drag-and-drop, fill-in-blanks, matching

> **Note:** This ticket absorbs the scope of ticket 078 (quiz question type system: MC, open-answer, interactive SVG). All interactive question types are consolidated here.

## What to build

Visually engaging, interactive question types beyond text prompts. These break monotony and increase engagement through varied interaction patterns:

- **Drag and drop** — reorder steps, match items to categories, place labels on diagrams
- **Fill in the blanks** — code or concept completion with inline text inputs
- **Matching** — connect terms to definitions, inputs to outputs
- **Label the diagram** — drag labels onto positions in an SVG
- **Sequence ordering** — arrange steps in correct order

These are simple, lightweight components (Preact) — not a full LMS quiz engine. The goal is visual variety and tactile interaction, not complex grading.

## Acceptance criteria

- [ ] At least 3 interactive question types implemented as Preact components
- [ ] Components work without a server (static HTML, client-side only)
- [ ] Questions can be authored in the JSONL format (or a simple extension of it)
- [ ] Correct/incorrect feedback is immediate and visual
- [ ] Accessible (keyboard navigable, screen reader announcements)
- [ ] Mobile-friendly (touch targets, responsive layout)
- [ ] Integrated into the quiz page generation pipeline
