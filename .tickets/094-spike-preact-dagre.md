---
id: "094"
title: "Spike: Preact + HTM + Signals + dagre map page prototype"
type: spike
status: open
priority: high
blocked_by: []
---

# Spike: Preact + HTM + Signals + dagre map page prototype

## Question to answer

Does Preact (with HTM tagged templates + Signals for state) produce a better component model for our map page than Alpine's directive approach? Is the no-build ESM-from-CDN workflow viable for Python-generated HTML?

## Method

Build a standalone prototype at `tools/spike-preact-dagre.html` that:
1. Loads Preact (4KB), HTM (1KB), Signals (1.6KB), dagre (30KB) from CDN via ESM imports
2. Defines a `TopicCard` component with props (title, why, status, prereqs)
3. Uses Signals for reactive state (generation status per card)
4. Uses dagre for DAG layout (already proven in spike-092)
5. Renders edges as SVG overlay
6. Simulates live generation (setTimeout → signal update → component re-renders)
7. Uses existing `assets/style.css` for theming
8. Hardcodes the blender-godot-shaders topic data

## Evaluate

- [ ] Does the component model (TopicCard, EdgeLayer, MapView) feel cleaner than Alpine directives?
- [ ] Is HTM (tagged template literals) readable without JSX/build?
- [ ] Do Signals provide a better mental model for SSE-driven state than Alpine's reactivity?
- [ ] Is the Python generation story viable? (outputting ESM imports + HTM templates)
- [ ] Does it feel snappy (sub-100ms render for 7-9 nodes)?
- [ ] How does error handling work (component boundaries)?
- [ ] Total page weight with CDN deps

## Evaluate vs Alpine spike (093)

Direct comparison:
- **DX for Python generation** — which template format is easier to emit from a Python script?
- **Readability of output HTML** — which is easier for a human to inspect/debug?
- **Reactivity model** — which handles SSE state changes more naturally?
- **Composability** — which is easier to extend with new card types (quiz, review, locked)?
- **Bundle size** — which loads faster on LAN?

## Acceptance Criteria

- [ ] Single HTML file, opens in browser, no server needed (except CDN fetch)
- [ ] 7 topic cards in correct DAG layout with edges
- [ ] Click "Generate" → simulated progress state visible on card
- [ ] Card status updates reactively via Signals
- [ ] Dark/light theme toggle works
- [ ] No overlapping cards
- [ ] Cards wide enough for content
- [ ] Components are separable (TopicCard could be reused in lesson pages)

## NOT in scope

- Real SSE connection
- Replacing `generate_map_page.py`
- Full component library
- Mobile responsiveness (desktop evaluation first)
