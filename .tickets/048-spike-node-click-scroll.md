---
id: "048"
title: "Spike: SVG node click → scroll to topic card + highlight"
status: open
priority: high
blocked_by: []
type: spike
---

# Spike: SVG node click → scroll to topic card

## What to test

When a user clicks a node in the map SVG, the page smoothly scrolls to the matching topic card and briefly highlights it. This is the primary navigation interaction for the map page.

## Current bug

SVG nodes link to `#generate-{slug}` but topic cards have `id="topic-{slug}"`. The links don't scroll anywhere.

## Fix + enhancement

1. Fix href in generate_map_page.py: always point to `#topic-{slug}`
2. Add `scroll-margin-top` on topic cards (prevent sticky header occlusion if we add one later)
3. Add a brief highlight animation when the target card is scrolled into view (CSS `:target` or JS flash)
4. If the topic has a lesson: node links to the lesson page directly. If not: scrolls to card where "Generate" button lives.

## Success criteria

- [ ] SVG node click scrolls to matching topic card
- [ ] Brief highlight on the target card (0.5s background flash)
- [ ] Smooth scroll behavior (CSS `scroll-behavior: smooth`)
- [ ] Works for all 7 nodes in the test map
