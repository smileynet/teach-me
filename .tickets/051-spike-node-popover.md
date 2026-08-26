---
id: "051"
title: "Spike: SVG node hover popover — topic detail without scrolling"
status: done
priority: low
blocked_by: []
type: spike
tags: [platform]
---

# Spike: SVG node hover popover

## What to test

Can we show a small popover when hovering/clicking an SVG node that displays the topic's "why" text, scope, and action button — without requiring the user to scroll down to the card section?

## Design

On hover (desktop) or tap (mobile):
- Small tooltip/popover positioned near the node
- Shows: title, why, scope, prereqs
- Action button: "Open lesson" or "Generate"
- Dismiss on mouse leave or tap elsewhere

## Questions to answer

1. SVG hover detection: can we use CSS `:hover` on `<g>` elements, or need JS `mouseenter`/`mouseleave`?
2. Positioning: should the popover be inside the SVG (foreignObject) or an HTML overlay positioned absolutely?
3. Mobile: hover doesn't exist — does tap-to-show + tap-elsewhere-to-dismiss work well enough?
4. Does this add value over just scrolling to the card, or is it unnecessary complexity?

## Success criteria

- [ ] Hover on an SVG node shows a popover with topic details
- [ ] Popover positions correctly (doesn't overflow viewport)
- [ ] Popover has a clickable action (generate or open lesson)
- [ ] Works on both desktop and mobile (hover vs tap)
- [ ] Doesn't interfere with the node click-to-scroll behavior (048)

## Validation

- **E2E (Playwright desktop):** Navigate to map page → hover a node → verify popover element appears with correct title/why text → verify popover disappears on mouseout
- **E2E (Playwright mobile):** Resize to iPhone viewport → tap a node → verify popover appears → tap elsewhere → verify popover dismisses
- **Regression:** After popover implementation, click a node → verify detail panel still appears (no interference)

## Resolution (2026-08-13)

TBD
