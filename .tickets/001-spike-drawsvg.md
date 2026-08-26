---
id: "001"
title: "Spike: drawsvg for teaching diagrams"
status: done
priority: high
blocked_by: []
type: spike
tags: [platform]
---

# Spike: drawsvg for teaching diagrams

## Question to answer

Can drawsvg produce good-looking inline SVG diagrams for HTML lessons with minimal code? Is the API ergonomic enough that an agent can generate it reliably?

## Experiment

1. `pip install drawsvg` 
2. Write a small script that generates 3 diagram types:
   - Layered stack (Iceberg metadata tree: catalog → metadata → data)
   - Left-to-right flow (3-4 nodes with arrows and labels)
   - Hub-and-spoke (central service with connections)
3. Verify `as_svg()` output embeds correctly in a standalone HTML file
4. Measure: lines of code per diagram, readability of generated SVG, visual quality

## Success criteria

- [x] All 3 diagrams render correctly in browser
- [x] `as_svg()` returns valid inline SVG string (no file I/O needed)
- [x] Diagrams look good enough for teaching materials
- [x] Code is concise enough for an agent to generate reliably (<30 lines per diagram)

## Output

- `tools/spike-drawsvg.py` — the spike script
- `tools/draw-diagram.py` — adopted; spike findings led to the draw-diagram helper (ticket 006)
