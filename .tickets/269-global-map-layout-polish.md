---
id: "269"
title: "Global map layout: horizontal scroll affordance + fix node clipping + anomalous border"
status: done
blocked_by: []
priority: medium
tags: ["platform"]
---

# Global map layout polish

## Why (found in UX audit, 2026-08-29 — .scratch/ux/shots/global-map*.png)

Three layout issues on `global-map.html`:
1. **Horizontal cutoff, no affordance:** canvas ~2118px vs 1280 viewport; the right-most
   node ("Ink + Godot") is clipped with no visible scroll/pan cue → hidden content.
2. **Node bottom-clip:** the MKToon node's progress ring is cut off by its own card
   (card height in GlobalMapView layout is too short for title-wrap + ring row).
3. **Anomalous highlighted border:** "Blender Texture Prep" renders with a bright
   white/black border unlike its siblings — looks like a stuck selected state; no cause.

## What to build

- `.dag-container` already has `overflow-x: auto`; add a visible scroll affordance (edge
  fade/shadow or a hint) so off-screen nodes are discoverable. Consider fit-to-width or a
  zoom-to-fit for wide forests.
- Fix `GlobalMapView.computeLayout` node height (currently fixed `H = 96`) — measure or
  raise so title-wrap + ring never clip. Mirror MapView's offscreen-measure approach.
- Investigate the "Blender Texture Prep" border anomaly (likely `.is-child` dashed border
  reading as highlighted, or a per-node style) and normalize.

## Acceptance criteria

- [x] No node clipped at right edge without a scroll affordance (fade/shadow/hint present)
- [x] No node's content (ring/title) clipped by its own card at any topic-count
- [x] All domain nodes have consistent border treatment (sub-map = left accent, uniform;
      no lone highlighted node)
- [x] `mise run verify` EXIT 0; Playwright re-shot confirms fixes

## Validation

Regenerate global map, Playwright screenshot at 1280×800: all 9 example nodes either
visible or reachable via a cued scroll; no clipped rings; consistent borders.

## Resolution (2026-08-30)

GlobalMapView: offscreen height measurement replaces fixed H=96 (no clip). generate_global_map css: .dag-scroll edge-fade affordance + .domain-card.is-child left-accent border (replaced dashed all-round). Viewed screenshot: MKToon ring visible, sub-map accent subtle, right node cued by fade.
