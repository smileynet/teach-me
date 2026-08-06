---
id: "003"
title: "Add progressive reveal component to lesson assets"
status: open
priority: medium
blocked_by: ["001"]
---

# Add progressive reveal component to lesson assets

## What to build

A JavaScript component in `assets/` that enables step-by-step diagram reveal in HTML lessons. Inspired by Manim's approach: show one concept, then add the next, building complexity incrementally.

## Design

A lightweight JS module (`assets/progressive-reveal.js`) that:
1. Takes an SVG diagram with elements grouped by `data-step="1"`, `data-step="2"`, etc.
2. Shows only step 1 initially
3. Provides Next/Prev buttons (or keyboard arrows) to reveal subsequent steps
4. Fades in new elements with a CSS transition
5. Optionally highlights the newly-revealed elements briefly

## Why

From Mayer's multimedia learning research: segmenting (presenting in learner-paced segments) improves learning. From Manim prior art: step-by-step reveal is the #1 technique for teaching complex architectures.

## Acceptance criteria

- [ ] Component file at `assets/progressive-reveal.js`
- [ ] Works with inline SVG (elements tagged with `data-step`)
- [ ] Keyboard navigation (← →) and button controls
- [ ] CSS transitions for smooth reveal (not jarring show/hide)
- [ ] Lesson using this component as a demo
- [ ] No external dependencies (vanilla JS + CSS)
