---
id: "093"
title: "Spike: Alpine.js + d3-dag map page prototype"
type: spike
status: open
priority: high
blocked_by: []
---

# Spike: Alpine.js + d3-dag map page prototype

## Question to answer

Does Alpine.js + d3-dag produce a better map page experience than our current Graphviz + vanilla JS approach? Is the developer experience (generating HTML from Python) acceptable?

## Method

Build a standalone prototype at `tools/spike-alpine-d3dag.html` that:
1. Loads Alpine.js (15KB) and d3-dag (30KB) from CDN
2. Uses Alpine `x-data` for topic state (status, generation progress)
3. Uses d3-dag to compute DAG layout positions
4. Renders topic cards as Alpine-reactive HTML divs at computed positions
5. Simulates live generation (mock SSE → Alpine state update → card re-renders)
6. Uses existing `assets/style.css` for theming
7. Hardcodes the blender-godot-shaders topic data for evaluation

## Evaluate

- [ ] Does Alpine's directive syntax make the generated HTML readable/maintainable?
- [ ] Does d3-dag handle branching better than dagre? (parallel branches at correct rank)
- [ ] Is the reactive state model natural for generation status updates?
- [ ] Does it feel snappy (sub-100ms layout for 7-9 nodes)?
- [ ] Can Python's `generate_map_page.py` realistically output Alpine-flavored HTML?
- [ ] Does theming (dark/light toggle) work without fighting Alpine?
- [ ] Total page weight with CDN deps

## Acceptance Criteria

- [ ] Single HTML file, opens in browser, no server needed (except CDN fetch)
- [ ] 7 topic cards in correct DAG layout with edges
- [ ] Click "Generate" → simulated progress state visible on card (spinner/text)
- [ ] Card status updates reactively (not-started → generating → complete)
- [ ] Dark/light theme toggle works
- [ ] No overlapping cards
- [ ] Cards wide enough for content

## NOT in scope

- Real SSE connection to `/api/generate`
- Replacing `generate_map_page.py` (that's ticket 091)
- Quiz or subtopic functionality
- Mobile responsiveness (evaluate desktop first)
