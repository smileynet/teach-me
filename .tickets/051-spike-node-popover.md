---
id: "051"
title: "Spike: SVG node hover popover — topic detail without scrolling"
status: open
priority: low
blocked_by: ["048"]
type: spike
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
