---
id: "270"
title: "Map prereq indicator renders glued: add gap between glyph/state/name spans"
status: open
blocked_by: []
priority: medium
tags: ["platform"]
---

# Prereq indicator span spacing

## Why (found in UX audit, 2026-08-29 — .scratch/ux/shots/toon-map-styled-*.png)

The recommended-prereq indicator (#255) renders glued: **"✓metSpatial Shader Anatomy"** —
the `.prereq-mark` (✓/○), `.prereq-state` ("met"/"not yet"), and `.prereq-name` spans have
no separating space. Markup is correct; the CSS lacks a gap.

## What to build

- In `tools/generate_map_page.py` `css_extra` (`.prereq-item` block, which sets
  `display:flex; gap:0.3rem` on the ITEM but the three child spans still collide because
  `align-items: baseline` + no per-span margin renders them adjacent), ensure visible
  separation between mark, state, and name. Simplest: the `.prereq-item` flex `gap`
  already exists — verify it applies (the glyph+state+name are 3 flex children, so gap
  SHOULD separate them; the bug suggests they're wrapped or the gap is being collapsed).
  Add explicit `margin-right`/separators if flex gap isn't taking, or restructure so
  "✓ met" and the name are clearly spaced.

## Acceptance criteria

- [ ] Prereq indicator renders as "✓ met  Spatial Shader Anatomy" (clear separation)
- [ ] Both met (✓) and not-yet (○) states legible with glyph + word + name spaced
- [ ] `mise run verify` EXIT 0; Playwright re-shot confirms spacing

## Validation

Regenerate a domain map with a mix of met/unmet prereqs; Playwright screenshot confirms the
three parts are visually separated.
