---
id: "084"
title: "Fix: add inline SVG diagram to workout lesson 0001"
status: open
blocked_by: []
priority: medium
---

# Fix: add inline SVG diagram to workout lesson 0001

## Problem

Workout lesson 0001 (Progressive Overload) is the only lesson without an inline SVG diagram. The scaffold requires at least one accessible diagram per lesson. This lesson would benefit from a simple visual showing the overload concept (weight/reps trending up over time).

## What to build

Add an inline SVG showing progressive overload visually. Options:
- A simple line graph trending upward (sessions on X axis, weight on Y)
- A stepped staircase showing weight increases session-to-session
- A comparison: flat line (accommodation) vs upward trend (overload)

Must include: `role="img"`, `<title>`, `aria-labelledby`, `viewBox` (no fixed width/height).

## Acceptance criteria

- [ ] Lesson 0001 has at least one inline SVG with accessibility attributes
- [ ] Diagram illustrates progressive overload concept
- [ ] Uses the project color vocabulary (blue for primary, green for success)
- [ ] `mise run verify` passes
