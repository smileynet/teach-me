---
id: "283"
title: "Unify MapView + IteratedMapView into one GraphView (deepening)"
status: done
blocked_by: []
tags: [platform]
---

# Unify MapView + IteratedMapView into one GraphView (deepening)

## Context

`assets/components/MapView.js` (topic map) and `assets/components/IteratedMapView.js` (domain
forest) are two adapters over ONE concept — a dagre node-link graph of progress-bearing nodes.
Both implement the identical 5-stage core (offscreen height measure → dagre TB layout →
center→corner → edge-path extraction → absolute cards + SVG edge layer). A change to graph
rendering must be made twice and has already diverged (only IteratedMapView has fit-to-view;
MapView has the documented `g.edge(e)` spike bug).

Validated by a spike (`.scratch/spike-graph-view/FINDINGS.md`): both real pages delegated to a
prototype `GraphView` and BOTH oracles passed (check-map-edges 10/10 identical to baseline;
verify 16/16 incl. #279 f–h). Zero `if(level===)` branching — all 12 divergences inject cleanly.
The spike caught a real rendering bug (`stroke-dasharray` `"0"` vs `"none"`), proving the oracle
gate is meaningful.

Killing the sibling candidate (a shared server-side `derive_graph`) is recorded in ADR 0017 —
that seam was a pass-through; THIS one is a real 5-stage algorithm. Judged independently.

## What to build

1. Promote `GraphView` to `assets/components/GraphView.js` (harden the spike prototype):
   `GraphView({nodes, edges, nodeKey, renderNode, viewport:'fit'|'scroll', edgeStyles,
   cardWidth, graphOpts, hover, canvasClass, edgeLayerClass})`. Owns measure/dagre/paths;
   node rendering INJECTED (composition). Measure via offscreen Preact render of the real
   node (`visibility:hidden`). Standardize `g.edge(v,w)`.
2. Rewrite `MapView` + `IteratedMapView` as thin adapters (KEEP both — they are the seam's
   two real callers; two adapters = a proven seam). MapView injects TopicCard/id/scroll +
   prereq synthesis upstream; IteratedMapView injects domain `<a>`/slug/fit/hover + legend +
   islands chrome.
3. Remove now-dead code: `EdgeLayer.js` IF fully subsumed (verify no other importer — grep);
   the inline layout fns in both components. Note: `EdgeLayer` is the topic-map edge renderer;
   confirm the domain view never used it.
4. Solid-edge sentinel is `stroke-dasharray="none"` (NOT `"0"`) — the oracle keys on it.

## Acceptance criteria

- [x] `GraphView` in `assets/components/`; zero `if(level===)`/level-branching (grep-clean)
- [x] MapView + IteratedMapView are thin adapters delegating to GraphView
- [x] Dead code removed (EdgeLayer if subsumed; inline layout fns) — no orphan imports
- [x] `mise run check-maps` PASS — topic-map edge identity + geometry + styling unchanged
- [x] `mise run verify` EXIT 0 — domain-map mount + #279 count-resolution unchanged
- [x] `mise run visual-qa` (or manual load) confirms both pages render correctly

## Resolution

Shipped. `GraphView` (`assets/components/GraphView.js`) owns the 5-stage dagre core (offscreen
measure via real-node render at `visibility:hidden` → dagre TB → center→corner → edge-path →
render); all divergences injected (`nodeKey`, `renderNode`, `viewport`, `edgeStyles`, `hover`,
`cardWidth`, `graphOpts`, caller-owned `canvasClass`/`edgeLayerClass`). `MapView` (118→65 lines)
and `IteratedMapView` (138→63) are now thin adapters. `EdgeLayer.js` deleted (subsumed; no
importer — grep-confirmed); `mise.toml check-maps` sources + `ui-contracts.md` updated to name
GraphView. Standardized `g.edge(v,w)` (fixes the documented MapView `g.edge(e)` spike bug);
solid edges emit `stroke-dasharray="none"` (the oracle contract).

Net -52 lines. Locality proof: the solid-sentinel fix during the spike was ONE edit correcting
BOTH pages.

**Verification:**
- `mise run check-maps` — 10/10 topic maps PASS (edge id/type/geometry/styling, detached=0), identical to pre-refactor baseline.
- `mise run verify` — EXIT 0 (41 unit, 16 interactive incl. domain-map mount + #279 f–h, 5/5 ink).
- `mise run visual-qa` — 2/2 checks pass (with PYTHONIOENCODING=utf-8; the bare `mise run visual-qa` hits the pre-existing #265 cp1252 crash in visual-qa.py's result-print, NOT a #283 defect — that tool lacks the UTF-8 stdout guard the generators have).
- Zero `if(level===)` / no orphan `EdgeLayer` import (grep-clean).

Validated by the Spike-1 dry run first (`.scratch/spike-graph-view/FINDINGS.md`) via a reversible
delegation swap against both oracles. Sibling candidate (shared server `derive_graph`) was killed
— see ADR 0017.

**Follow-up noted (not #283):** #265 — `visual-qa.py` (and ~21 tools) missing the UTF-8 stdout
guard; `mise run visual-qa` crashes on Windows cp1252 when printing the `✓` result glyph.

## References

- Spike: `.scratch/spike-graph-view/{GraphView.js,FINDINGS.md}` (prototype + kill-criteria results).
- `tools/check-map-edges.py` (`mise run check-maps`) — topic-map oracle; NOT in core verify, must run explicitly.
- `tools/verify-interactive.py::run_index_checks` — domain-map (index Map tab) coverage.
- ADR 0017 — the killed sibling (shared derive_graph); this refactor is the client-side seam that survived.
- Research: `.scratch/spike-deepening/*.md` (render-prop layout prior art, offscreen measure, spike methodology).
