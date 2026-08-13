---
id: "102"
title: "Convert progressive-reveal.js to Preact component"
type: feature
status: done
priority: low
blocked_by: ["095"]
work_order: 6
---

# Convert progressive-reveal.js to Preact component

## What to build

Step-through diagram reveal as a Preact component. Signal tracks current step, DOM elements with `data-step` show/hide reactively.

## Deliverables

- `assets/components/ProgressiveReveal.js` — step counter signal, next/prev buttons, aria-live for a11y
- Works as an island mount in static lesson HTML

## Acceptance Criteria

- [x] Steps advance/retreat on button click
- [x] Only elements up to current step are visible
- [x] aria-live announces new content for screen readers
- [x] Works in existing lesson pages via mount point

## Context & Sources

- **Pattern:** Preact island mount in static HTML — see `.scratch/research/migration-vanilla-to-framework.md`
- **Current code:** `assets/progressive-reveal.js` (61 lines) — `data-step` attrs show/hide elements
- **Components:** New `ProgressiveReveal` component with signal for current step
- **A11y:** Must maintain `aria-live="polite"` on container — see `.kiro/steering/visual-teaching.md`
