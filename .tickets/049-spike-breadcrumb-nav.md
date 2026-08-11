---
id: "049"
title: "Spike: breadcrumb navigation — '← Back to Map' on lesson pages"
status: done
priority: high
blocked_by: []
type: spike
---

# Spike: breadcrumb nav on lesson pages

## What to test

Can we add a consistent "← Back to Map" link at the top of every lesson page that navigates back to the map hub? This is the return affordance for the hub-and-spoke navigation model.

## Design

A minimal nav bar inserted at the top of lesson HTML:

```html
<nav class="lesson-nav">
  <a href="../map.html" class="back-to-map">← Course Map</a>
  <span class="lesson-position">Lesson 1 of 8 · Storage & Table Formats</span>
</nav>
```

## What to build in the spike

1. A reusable HTML/CSS snippet for lesson navigation
2. A script or template addition that injects it into generated lessons
3. Test: does the link resolve correctly from `lessons/0001-*.html` to `lessons/map.html`?
4. Visually: does it fit the dark theme without clashing?

## Questions to answer

- Should the nav be injected by the teach skill at generation time, or post-processed?
- Does it need prev/next lesson links too, or just back-to-map?
- How to determine "Lesson N of M" without a MAP.md parser integrated into lesson generation?

## Success criteria

- [ ] "← Course Map" link at top of a lesson page navigates to map.html
- [ ] Visually consistent with the dark theme
- [ ] Doesn't add clutter to a single-topic lesson (hide if no map exists?)
- [ ] Works with relative paths from `lessons/` directory
