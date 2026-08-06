---
id: "004"
title: "Spike: progressive reveal for SVG diagrams"
status: done
priority: medium
blocked_by: []
type: spike
---

# Spike: progressive reveal for SVG diagrams

## Question to answer

Can we build a simple JS component that shows SVG diagram elements step-by-step (Manim-inspired), using only `data-step` attributes and CSS transitions?

## Experiment

1. Create an inline SVG with 4-5 elements tagged `data-step="1"` through `data-step="4"`
2. Write a small JS module that:
   - Hides all elements except step 1 on load
   - Shows Next/Prev buttons (or responds to ← → keys)
   - Fades in new elements with a CSS opacity transition
   - Optionally highlights newly-revealed elements briefly
3. Test with a layered architecture diagram (reveal one layer at a time)

## Success criteria

- [ ] Step-by-step reveal works with keyboard (← →) and buttons
- [ ] CSS transitions provide smooth fade (not jarring show/hide)
- [ ] Works with inline SVG (not just img tags)
- [ ] < 50 lines of JS
- [ ] No external dependencies

## Output

- `assets/progressive-reveal.js`
- `lessons/spike-reveal-test.html` — test page (delete after spike)
