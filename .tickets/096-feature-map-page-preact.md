---
id: "096"
title: "Convert generate_map_page.py to Preact DAG output"
type: feature
status: done
priority: high
blocked_by: ["095"]
tags: [platform]
---

# Convert generate_map_page.py to Preact DAG output

## What to build

Replace the current Graphviz SVG + vanilla JS card list output with the Preact + dagre inline DAG card layout proven in spike 094.

## Architecture

Python generates:
1. HTML shell with import map + `<div id="app">`
2. Data island: `<script type="application/json" id="map-data">` containing topics, edges, orientation, leads_to
3. Module script that imports MapView component and mounts it with the data

The MapView component handles:
- dagre layout (two-pass: render hidden → measure → layout → show)
- TopicCard rendering at computed positions
- EdgeLayer SVG overlay
- Live generation via SSE (signals update → cards re-render)

## Two-pass layout (from dagre research)

dagre has no native rank-same constraint and needs actual node heights:
1. Render all TopicCards with `visibility: hidden`
2. Measure each card's `offsetHeight`
3. Call `dagre.layout()` with measured heights
4. Position cards at computed (x, y)
5. Draw edges
6. Set `visibility: visible`

## Acceptance Criteria

- [x] `python tools/generate_map_page.py MAP.md --workspace X --output Y` produces a Preact page
- [x] Page loads without CDN (vendored deps)
- [x] 7 topic cards render in correct DAG layout with edges
- [x] No overlapping cards (two-pass measurement)
- [x] Cards wide enough for content (no clipping)
- [x] Click "Generate this topic" triggers live SSE via `/api/generate`
- [x] Status updates reactively (not-started → generating → complete)
- [x] Theme toggle works (dark/light)
- [x] "Where This Leads" section renders as buttons with descriptions
- [x] All `test_map_page.py` tests pass (update assertions for new output)
- [x] Existing example map pages regenerate successfully

## Supersedes

- Ticket 091 (graph inline cards) — this IS that ticket, with Preact as the implementation
- The current Graphviz + `offerGenerate()` + vanilla JS modal code is deleted

## Research references

- `.scratch/research/dagre-layout-customization.md` — two-pass, rank workarounds
- `.scratch/research/preact-dag-performance.md` — negligible overhead at 30 nodes
- Spike 094 (`tools/spike-preact-dagre.html`) — working prototype
