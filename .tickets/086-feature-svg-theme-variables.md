---
id: "086"
title: "Feature: SVG diagrams use CSS custom properties for theme-aligned colors"
status: open
blocked_by: []
priority: medium
---

# Feature: SVG diagrams use CSS custom properties for theme-aligned colors

## Problem

Inline SVG diagrams use hardcoded hex colors (`#2563eb`, `#dbeafe`, etc.) from the color vocabulary. These don't respond to theme changes (dark mode). When the page switches to dark mode, diagram backgrounds and text remain fixed — creating contrast issues and visual disconnection from the themed page.

## Strategy

Define SVG-specific CSS custom properties that:
1. Align with the existing color vocabulary (blue=primary, green=success, etc.)
2. Provide light/dark variants via the theme system
3. Offer a broader palette than the 5 semantic colors (additional tints, shades)
4. Are declared in `style.css` so all SVGs inherit them automatically

### Proposed variables (in style.css)

```css
:root {
  /* SVG diagram palette — light mode */
  --svg-primary: #2563eb;
  --svg-primary-fill: #dbeafe;
  --svg-primary-text: #1e40af;
  --svg-success: #16a34a;
  --svg-success-fill: #dcfce7;
  --svg-success-text: #166534;
  --svg-warning: #d97706;
  --svg-warning-fill: #fef3c7;
  --svg-warning-text: #92400e;
  --svg-error: #dc2626;
  --svg-error-fill: #fef2f2;
  --svg-neutral: #6b7280;
  --svg-neutral-fill: #f3f4f6;
  --svg-neutral-text: #374151;
  --svg-line: #94a3b8;
  --svg-text: #374151;
}

[data-theme="dark"] {
  --svg-primary: #60a5fa;
  --svg-primary-fill: #1e3a5f;
  --svg-primary-text: #bfdbfe;
  /* ... dark equivalents for each */
}
```

### Migration path

1. Add variables to style.css (non-breaking — existing hex still works)
2. Update scaffolds and visual-teaching.md to document new variables
3. Update draw-diagram.py to emit `var(--svg-*)` instead of hex
4. Migrate existing lesson SVGs (find/replace in committed pages)
5. Update svg-patterns.md reference

## What to build

1. Add `--svg-*` custom properties to `assets/style.css` (light + dark variants)
2. Update `assets/svg-patterns.md` to use the new variables
3. Update `tools/draw-diagram.py` output to reference CSS variables
4. Update `.kiro/steering/visual-teaching.md` color vocabulary table
5. Migrate all inline SVGs in example lessons to use the variables

## Acceptance criteria

- [ ] `style.css` defines `--svg-*` variables for light and dark themes
- [ ] `draw-diagram.py` outputs SVGs using `var(--svg-*)` references
- [ ] At least one example lesson's SVG uses the new variables (proof of concept)
- [ ] Diagrams render correctly in both light and dark mode
- [ ] `svg-patterns.md` updated with new variable names
- [ ] `mise run verify` passes
