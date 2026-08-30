---
id: "275"
title: "Spike: index + global-map as two views over one domain-graph island"
status: open
blocked_by: []
tags: ["platform"]
---

# Spike: index + global-map as two views over one domain-graph island

## Premise (2026-08-30)

The aggregate index (`library/index.html`, `IndexView.js`) and the global map
(`library/global-map.html`, `GlobalMapView.js`) are two RENDERINGS of the same domain graph,
not two datasets. The global map's `#page-data` is a superset: it already carries per-domain
`{title, total, complete, inProgress, mapHref}` PLUS `depth`, `parent`, `edges`, `islands`.
The index is that same graph filtered to depth-0 nodes, laid out as a flat card grid, with
mission + the #271 start/resume cue on top. Both generators re-derive the domain list from the
same MAP.md scan; both define a `.domain-card` + progress ring. That duplication is the smell.

This spike DE-RISKS the unification (#276) before committing to the architecture. Learn, don't
ship production code — throwaway prototype is fine.

## Questions to answer

1. **Data superset holds?** Confirm the global-map island can serve BOTH views with no data loss
   — i.e. the index needs nothing the map island lacks (verify mission handling: the map has no
   mission block today; where does it live in a unified page?).
2. **One generator feasible?** Can `generate_global_map.py`'s data-build subsume
   `generate_index_page.py`'s (depth-0 filter + mission parse), emitting ONE island? Note the
   count-baking + overlay behavior (#271 lesson: regeneration re-bakes from local overlay — the
   unified generator must not clobber committed demo counts).
3. **Toggle UX + state.** Prototype a list⇄map view switch off one signal; does landing default
   to list (low-load, per #271 research) with map one click away? Persist choice (localStorage)?
   Does this collide with the single-axis-preferences steering rule? (Likely EXEMPT — it cites
   "map page vs lesson page" as a legitimate distinct-view switch; confirm.)
4. **Shared card component.** Can `IndexView`'s card and `GlobalMapView`'s positioned card share
   one component (props: domain + optional layout/edge context)? What diverges (grid vs absolute
   positioning, edges, islands panel)?
5. **Deploy/ADR-0015.** One page instead of two — confirm document-relative paths + #272 `_site`
   assembly stay correct (should simplify: one index, the map view is a client toggle).
6. **Scale.** At 15+ domains, does the map view hairball? Does the list view stay usable? Any
   layout ceiling that argues for keeping list as the default landing.

## What to build (throwaway)

- A prototype (branch or `.scratch/`) that renders BOTH views from the global-map island with a
  toggle, served locally. Enough to feel the UX and confirm the data/generator/deploy answers.
- A short findings doc (`.scratch/` or promote to the ADR draft) answering Q1-Q6 with evidence.

## Acceptance criteria

- [ ] Q1-Q6 answered with concrete evidence (code refs, prototype behavior, served screenshots)
- [ ] Prototype demonstrates list⇄map toggle over ONE data island (throwaway, not production)
- [ ] Findings doc written; feeds the #276 implementation plan and the #277 ADR options/decision
- [ ] Recommendation: proceed with unification as scoped, adjust scope, or keep separate (with why)

## Validation

Serve the prototype (`--lan` for human view), toggle list↔map, confirm both render from one
island with no data loss. Findings doc reviewed before #276 starts.
