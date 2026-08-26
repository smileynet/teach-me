---
id: "091"
title: "Move topic detail into graph nodes — inline cards replace sidebar list"
type: feature
status: done
priority: high
blocked_by: []
tags: [platform]
---

# Move topic detail into graph nodes — inline cards replace sidebar list

## What to build

Replace the current layout (SVG graph at top + separate topic card list below) with a single integrated view where each graph node IS the card. The title, description, prereq label, and action buttons all live directly on/in the node — no scrolling to a separate section to understand what a topic is or to generate it.

## Current state (what's wrong)

The map page has two disconnected representations:
1. A Graphviz SVG DAG with just the topic title in each node
2. A list of cards below with title, description, prereq label, and action buttons

The user has to mentally map between the graph (which shows relationships) and the cards (which show detail + actions). This doubles cognitive load.

## Desired state

Each node in the graph is a rich card showing:
- **Title** (clickable if lesson exists)
- **Why** — one sentence
- **Prereq label** — "Start here" or "After: X, Y"
- **Action buttons** — Generate / Open lesson, Generate quiz, Explore subtopics

The graph layout still shows edges (prereq arrows) between cards, preserving the DAG structure. The separate "Topics" heading + card list is removed entirely.

## Acceptance Criteria

- [x] Each topic renders as a self-contained card in the graph area
- [x] Cards show: title, why, prereq label, action buttons
- [x] Prereq arrows/edges still visible between cards
- [x] No separate "Topics" list section below the graph
- [x] Clicking "Generate this topic" still triggers live SSE generation
- [x] Status badge (not started / in progress / complete) visible on each card
- [x] Responsive on mobile (cards stack vertically if viewport is narrow)
- [x] All existing tests in `test_map_page.py` still pass (adapt assertions as needed)

## Research needed

- How to render rich HTML cards with edges between them (CSS grid + SVG overlay? HTML-native DAG layout? foreignObject in SVG?)
- Prior art: tools like Miro, Whimsical, Linear project views, Obsidian canvas
- Whether Graphviz foreignObject can embed HTML blocks, or if we need a pure HTML/CSS DAG layout (dagre-d3, elkjs, or CSS-only with absolute positioning)

## Implementation notes

- The current Graphviz SVG is generated server-side in Python — may need to switch to a client-side layout library or a CSS-based approach
- Keep it zero-dependency if possible (no npm build step) — inline JS library or pure CSS grid with manual edge drawing
- The `generate_map_page.py` script produces a single self-contained HTML file; this constraint stays

## Resolution

Superseded by ticket 096 (Convert generate_map_page.py to Preact DAG output). The spike evaluation (092-094) confirmed dagre + HTML cards as the approach, and Preact + HTM + Signals as the reactive layer. Ticket 096 is the production implementation of this ticket's goals.
