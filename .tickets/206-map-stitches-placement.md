---
id: "206"
title: "Decide stitches placement in ink-godot MAP"
status: done
blocked_by: []
priority: high
type: decision
---

# Decide stitches placement in ink-godot MAP

## Decision (2026-08-25)

**Add stitches to lesson 02.** MAP title updated: "Choices & Weave" → "Choices, Stitches & Weave".

Rationale:
- Stitches are lightweight (just "knots within knots", `= name` syntax)
- Official docs introduce stitches BEFORE variables (Part 1§6)
- Esoteric Ebb uses them extensively (avg 8.6 per file) as conversation sub-topics
- Pairs naturally with gathers/weave (both are structural flow tools)
- Keeps MAP at 8 lessons (no new lesson needed)

## Problem

Stitches (sub-sections within knots, `= name`) are introduced in Part 1 Section 5 of WritingWithInk.md — BEFORE variables, functions, and tunnels. Our current MAP has:

- Lesson 01: Flow & Knots ← knots here
- Lesson 02: Choices & Weave ← gathers here
- Lesson 03: Variables & Conditionals
- Lesson 04: Functions & Tunnels ← stitches NOT mentioned

Stitches are a structural concept (like knots) not a logic concept (like variables). They naturally belong after knots and before variables. Options:

1. **Add stitches to lesson 01** (alongside knots) — may overload the first lesson
2. **Add stitches to lesson 02** (part of "structure beyond knots") — pairs well with gathers
3. **Create a lesson 02.5** or rename lesson 04 — adds a lesson
4. **Defer to lesson 04** and rename it "Stitches, Functions & Tunnels" — groups structural features

## Evidence

- Esoteric Ebb uses stitches EXTENSIVELY (avg 8.6 per file) as conversation sub-topics
- Official docs introduce stitches after basic choices but before variables
- Stitches are simpler than gathers/weave — they're just "knots within knots"

## Recommendation

Add stitches to **lesson 02** (Choices & Weave → "Choices, Stitches & Weave"). Stitches are lightweight enough to teach alongside choices, and the Ebb examples show them used primarily as choice-target sub-sections within a knot. This matches the official docs order and keeps the MAP at 8 lessons.
