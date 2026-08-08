---
id: "006"
title: "Feature: draw-diagram.py helper script"
status: done
priority: high
blocked_by: ["001"]
type: feature
---

# Feature: draw-diagram.py helper script

## What to build

A Python helper at `tools/draw-diagram.py` with reusable functions for generating teaching diagrams. The agent calls this to produce SVG strings for embedding in lessons.

**Depends on spike 001 results.** If drawsvg proves unsuitable, pivot to svg.py or raw SVG string generation.

## Key functions (proposed, update after spike)

- `labeled_box(x, y, w, h, label, fill, stroke)` → SVG group
- `arrow(x1, y1, x2, y2, label=None)` → line with arrowhead
- `layered_stack(layers: list[dict])` → vertical stack
- `flow(nodes: list[dict])` → horizontal flow with arrows
- `hub_spoke(center, spokes)` → central node with connections
- `render(drawing) → str` → inline SVG string

## Acceptance criteria

- [x] All core functions produce valid SVG
- [x] Output embeds correctly in HTML lessons
- [x] Colors match visual teaching steering vocabulary
- [x] Works headless (no display, no Cairo)
- [x] CLI mode: `python tools/draw-diagram.py --type flow --data '{...}'` → stdout SVG
