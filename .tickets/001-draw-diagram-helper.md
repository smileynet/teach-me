---
id: "001"
title: "Create draw-diagram.py helper using drawsvg"
status: open
priority: high
blocked_by: []
---

# Create draw-diagram.py helper using drawsvg

## What to build

A Python helper script at `tools/draw-diagram.py` that provides reusable functions for generating teaching diagrams. The agent calls this to produce SVG strings for embedding in lessons.

## Key functions to implement

- `labeled_box(x, y, w, h, label, fill, stroke)` → SVG group
- `arrow(x1, y1, x2, y2, label=None)` → line with arrowhead marker
- `layered_stack(layers: list[dict])` → vertical stack of labeled boxes
- `flow(nodes: list[dict])` → horizontal left-to-right flow with arrows
- `hub_spoke(center: dict, spokes: list[dict])` → central node with radiating connections
- `render(drawing) → str` → returns inline SVG string

## Design decisions

- Use `drawsvg` (v2.x) — active, pure Python, `as_svg()` for string output
- Follow color vocabulary from `.kiro/steering/visual-teaching.md`
- All functions return drawsvg elements (composable) OR full SVG strings
- CLI mode: `python tools/draw-diagram.py --type flow --data '{"nodes": [...]}'` → stdout SVG

## Acceptance criteria

- [ ] `pip install drawsvg` added to a requirements file
- [ ] All 5 core functions produce valid SVG
- [ ] Output embeds correctly in an HTML file
- [ ] Colors match the visual teaching steering vocabulary
- [ ] Script works headless (no display, no Cairo needed)
