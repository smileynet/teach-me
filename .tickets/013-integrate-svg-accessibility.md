---
id: "013"
title: "Integrate: SVG accessibility and responsive scaling"
status: done
priority: medium
blocked_by: []
type: feature
---

# Integrate: SVG accessibility and responsive scaling

## Source findings

`.scratch/research/inline-svg-compat.md` — researched 2026-08-06

Key findings NOT yet integrated into guidance or tools:

### Accessibility (WCAG compliance)
- Informative SVGs need `role="img"` + `<title>` + `<desc>` (screen readers)
- `aria-labelledby` linking title+desc IDs
- Interactive SVGs (progressive reveal) need `tabindex`, `aria-live` for dynamic content
- Color-independent indicators required (not just red/green — add patterns or icons)

### Responsive scaling
- Always set `viewBox` (case-sensitive!) — remove width/height attrs, size via CSS
- `preserveAspectRatio="xMidYMid meet"` for centered scaling
- `vector-effect="non-scaling-stroke"` for consistent line weights at any size

### Font rendering
- Use system font stack (`system-ui, sans-serif`) — already doing this ✓
- Never rely on specific font metrics for centering (use `text-anchor` + `dominant-baseline`) — already doing this ✓

## What to update

1. **`tools/draw-diagram.py`** — add `<title>` and `role="img"` to SVG output, accept a `--title` param
2. **`assets/svg-patterns.md`** — add accessibility pattern (title + desc + aria-labelledby)
3. **`.kiro/steering/visual-teaching.md`** — add accessibility section (ARIA requirements, color-independent indicators)
4. **Existing lessons** — add `viewBox` CSS sizing pattern (responsive)

## Acceptance criteria

- [x] draw-diagram.py outputs SVGs with `role="img"` and `<title>`
- [x] svg-patterns.md has an accessibility snippet pattern
- [x] Visual steering mentions WCAG requirements
- [x] Lessons use CSS-sized SVGs (no fixed width/height attrs)
