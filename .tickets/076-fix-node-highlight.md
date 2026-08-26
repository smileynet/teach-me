---
id: "076"
title: "Fix: highlight selected node on map graph when detail panel shows"
status: done
priority: high
blocked_by: []
type: feature
tags: [platform]
---

# Fix: selected node highlight

## Problem

When clicking a gray node and the detail panel appears, there's no visual indicator on the graph showing WHICH node is selected. The panel appears below without context.

## What to build

Add a CSS-based highlight (glow, thicker border, or scale) to the selected graph node. The `selectTopic()` function already adds `.selected` class to the node — just needs CSS to style it.

## Acceptance criteria

- [x] Clicking a graph node visually highlights it (distinct from hover)
- [x] Highlight clears when a different node is clicked
- [x] Works for all three states (green, blue, gray nodes)

## Validation

- **E2E (Playwright):** Click a gray node → screenshot → verify node has visible highlight (different from its neighbors)
