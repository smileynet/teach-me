---
id: "092"
title: "Spike: dagre + HTML cards DAG layout prototype"
type: spike
status: done
priority: high
blocked_by: []
---

# Spike: dagre + HTML cards DAG layout prototype

## Question to answer

Can we render a DAG of rich HTML topic cards (title, description, prereq label, action buttons) with visible edges, using dagre for layout + SVG for arrows, in a single self-contained HTML file that looks and feels better than the current Graphviz SVG + card list?

## Method

Build a standalone prototype HTML file (`tools/spike-dag-cards.html`) that:
1. Hardcodes the blender-godot-shaders topic data inline (no server dependency)
2. Loads dagre from CDN (~30KB)
3. Renders each topic as an absolute-positioned HTML card
4. Draws SVG bezier arrows between cards based on prereq edges
5. Includes status badges, action buttons (non-functional stubs), and prereq labels

## Acceptance Criteria

- [ ] Single HTML file, opens in browser with no server needed
- [ ] 7 topic cards rendered with correct DAG layout (branching, not linear)
- [ ] Arrows/edges visible between cards following prereq relationships
- [ ] Cards show: title, why (one sentence), prereq label, status badge, action button placeholders
- [ ] Responsive: cards reflow or scroll gracefully on narrow viewport
- [ ] Dark mode support (uses CSS variables from style.css vocabulary)
- [ ] File size under 100KB (excluding CDN fetch)
- [ ] Visual comparison: side-by-side with current map page for evaluation

## What we're evaluating

- Does it read better than graph + separate list?
- Is the relationship between topics clearer?
- Does it feel interactive or cluttered?
- Is the dagre layout acceptable or do we need manual positioning?
- Performance with 7-9 nodes (should be trivial but verify)

## NOT in scope

- Live generation (SSE integration)
- Server-side rendering
- Replacing `generate_map_page.py` (that's ticket 091)
- Quiz/subtopic button functionality

## Output

A single file at `tools/spike-dag-cards.html` we can open and compare against the current map page. Decision: adopt, modify, or reject the approach.

## Resolution

Superseded by spike 094 (Preact + dagre). The dagre + HTML cards approach proved correct. Preact was chosen over vanilla JS for reactivity. Production implementation in ticket 096.
