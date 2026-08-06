---
id: "002"
title: "Install D2 and create sketch-mode diagram workflow"
status: open
priority: medium
blocked_by: []
---

# Install D2 and create sketch-mode diagram workflow

## What to build

Set up D2 as a diagram-as-code tool for teaching materials. D2's sketch mode produces hand-drawn style diagrams that are pedagogically less intimidating.

## Steps

1. Verify D2 is installed (`brew install d2`) or document install in tools/
2. Create a `diagrams/` directory convention for D2 source files
3. Update `tools/render-diagrams.sh` to handle D2's sketch mode flag
4. Create 2-3 example `.d2` files demonstrating teaching patterns:
   - Architecture layer diagram (containers nested)
   - Data flow diagram (connections with labels)
   - Comparison diagram (side-by-side containers)
5. Verify SVG output embeds in lesson HTML correctly (with `--no-xml-tag` for inline)

## Key D2 features to leverage

- `d2 --sketch` for hand-drawn style
- Containers with `{}` for grouping
- `direction: right` for horizontal flows
- `style.fill`, `style.stroke` for color vocabulary alignment
- `--no-xml-tag` for inline SVG embedding in HTML

## Acceptance criteria

- [ ] D2 renders .d2 files to SVG without errors
- [ ] Sketch mode produces hand-drawn output
- [ ] Generated SVGs embed correctly in lesson HTML
- [ ] Example diagrams follow visual teaching steering colors
- [ ] `tools/render-diagrams.sh` supports `--sketch` flag
