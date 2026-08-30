---
id: "276"
title: "Unify index + global-map into one two-view page (list/map toggle over shared data)"
status: open
blocked_by: ["275"]
tags: ["platform"]
---

# Unify index + global-map into one two-view page (list/map toggle over shared data)

## Goal (pending #275 findings)

Make the aggregate index and the global map ONE page with two views over ONE domain-graph
data island — list view (default: depth-0 domain cards + mission + #271 start/resume cue) and
map view (full forest: all depths + edges + islands). Retire the duplicate data derivation and
duplicate `.domain-card` definitions. Exact shape confirmed by the #275 spike.

## What to build (baseline plan — refine from spike)

1. **One data island.** Extend/rename the generator so a single `#page-data` carries the full
   graph (domains with depth/parent, edges, islands, per-domain progress, mission). The list
   view filters to `depth===0` client-side; the map view uses the whole thing. Retire
   `generate_index_page.py`'s separate domain re-derivation (fold into the map generator or a
   shared `build_domain_graph()` helper).
2. **View toggle.** A control that swaps list⇄map rendering off one signal; default to LIST
   (low-load landing per #271 research); persist the choice in localStorage so returning users
   land where they left. Map is one click away, never the forced first screen.
3. **Shared card component.** Extract one `DomainCard` used by both layouts (grid vs absolute
   positioning + edges provided by the view wrapper).
4. **Mission + cue above the view** (learner-state, not graph structure) — present in both modes.
5. **Preserve committed demo counts.** Per #271: do NOT regenerate against a local empty overlay
   and clobber baked counts; apply the same care (or gate regeneration behind an overlay check).
6. **Deploy (ADR-0015 / #272).** One landing page; confirm `_site` assembly + document-relative
   paths still resolve. Update the #272 workflow if the page filename/layout changes.
7. **Redirect/compat.** Decide the fate of `global-map.html` as a URL (redirect to the unified
   page's map view, or keep as a deep-link that opens map view). Update inbound links (breadcrumbs,
   forest links).

## Acceptance criteria

- [ ] ONE `#page-data` island feeds both views; no duplicate domain re-derivation
- [ ] List view is the default landing (mission + #271 cue intact); map view via a persisted toggle
- [ ] Shared `DomainCard` component used by both layouts
- [ ] Committed demo progress counts preserved (no overlay-clobber regression)
- [ ] `_site` deploy + document-relative paths verified on the `/{repo}/` subpath (#272)
- [ ] `global-map.html` inbound links + any redirect handled; no broken nav (verify-links guard)
- [ ] `mise run verify` EXIT 0 (incl. the #271 index_cue + #273 breadcrumb guards)
- [ ] Browser: toggle list↔map, both render from one island; cue states intact (fold into #274)

## Validation

Served `--lan` for human review + browser click-through of the toggle and both views. `verify`
green. Coverage folded into `test-navigation.py` (#274).
