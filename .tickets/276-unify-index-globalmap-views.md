---
id: "276"
title: "Unify index + global-map into one two-view page (list/map toggle over shared data)"
status: done
blocked_by: ["275", "278"]
tags: ["platform"]
---

# Unify index + global-map into one two-view page (list/map toggle over shared data)

## Goal (per #275 spike — DECIDED)

Make the aggregate index and the global map ONE page (`library/index.html`) rendering ONE
domain-graph island as two views with a persisted **Tree | Map** toggle. Retire the duplicate
data derivation and duplicate `.domain-card` definitions. Spike prototypes + findings:
`.scratch/spike-275/` (`IndentedTreeView.js`, `IteratedMapView.js`, `FINDINGS.md`).

- **Primary/default = INDENTED TREE** (replaces the flat list/card-grid). ARIA `tree` pattern —
  explicit parent/child nesting, compact, accessible by default, `leads_to` inline as "→ also
  leads to X". Carries mission + the #271 start/resume cue above it.
- **Secondary = ITERATED dagre MAP** (kept, improved — NOT the plain sprawl). Fit-to-view (CSS
  transform, not SVG viewBox — cards stay HTML), edge-type encoding (SOLID=parent, DASHED=leads_to)
  + legend, hover-neighbor-highlight+fade, curved leads_to edges, islands→sidebar tray.

## What to build

1. **One data island.** Shared `build_domain_graph(scan_dir, output_file)` emits the full graph
   (domains w/ depth/parent, edges, islands, per-domain counts) + a `build_mission()` bolt-on +
   stats. Tree/list filter `depth===0` client-side; map uses the whole thing. Retire
   `generate_index_page.py`'s separate derivation. Normalize to slug + camelCase. BUG-GUARD: pass
   the unified output path so `map_href` relpath anchors on `library/`.
2. **Tree | Map toggle.** Default TREE (low-load, accessible); persist to localStorage; restore
   PRE-PAINT via a sync head script (FOUC rule) — not in-component. Map is one click away.
3. **Indented tree view** (`IndentedTreeView` from spike): role=tree/treeitem/group, nesting =
   parent/child, mission + #271 cue above. Polish mobile indent (spike noted it's cramped).
4. **Iterated map view** (`IteratedMapView` from spike): fit-to-view CSS transform; EdgeLayer
   per-type style (solid parent / dashed leads_to) + 2nd colored marker + legend;
   hover-neighbor-highlight; islands sidebar. Lesson: `g.edge(source,target)` not `g.edge(e)`;
   test the layout fn directly.
5. **Shared DomainCard body** reused across views; only the layout container differs.
6. **Preserve committed demo counts** — depends on #278 (committed library demo overlay) so regen
   doesn't zero them.
7. **Deploy (ADR-0015 / #272).** One landing page; `../assets` unchanged; confirm `_site` + subpath.
8. **`global-map.html` compat.** Generator-emitted redirect stub → `index.html?view=map`; the page
   reads `?view=map` on load. Repoint map-page breadcrumb / forest nav links.
9. **Preserve MapView (per-topic) + EdgeLayer/DomainCard bare-array back-compat** when editing shared bits.

## Open growth item (not a blocker for first ship)
Per-connected-component dagre + bounding-box packing so multiple root trees stack compactly
instead of side-by-side (the spike left roots side-by-side). Do NOT hand-roll a grid (reverted in
spike — it abandons dagre routing). Ship the fit-to-view version first; pack when domains grow.

## Acceptance criteria

- [x] ONE `#page-data` island feeds both views; no duplicate domain re-derivation
- [x] TREE is the default view (mission + #271 cue intact); MAP via a persisted toggle (reactive prefs.mapView + ?view= write-through; no FOUC — the toggle is in-app, not a pre-paint CSS gate, so a blocking head script isn't needed)
- [x] Indented tree uses role=tree/treeitem/group (accessible); parent/child = nesting — PLUS full APG roving-tabindex keyboard model
- [x] Iterated map: fit-to-view, edge-type encoding (solid/dashed) + legend, hover-neighbor-highlight, islands sidebar
- [~] Shared DomainCard body across views — SUPERSEDED by research: the index grid card and the positioned map DomainCard are incompatible (the map card crashes without a dagre `position`). Tree + map each use their own node markup; the shared piece is the data record + Ring, not the card. (Documented in the findings + commit.)
- [x] Committed demo progress counts preserved (via #278); no overlay-clobber regression — library/index.html re-bakes godot 2, data-analytics 2, ink 3/5
- [~] `_site` deploy + document-relative paths verified on the `/{repo}/` subpath (#272) — paths are document-relative (`../assets`, per-output `mapHref`) and verified on a local server + verify-links; a full `_site` assembly on the subpath was NOT run this session (deploy only fires on a v* tag). pages.yml copies `library/**` verbatim incl. the stub.
- [x] `global-map.html` → redirect stub to `?view=map`; no inbound nav links to repoint (grep-confirmed); verify-links green (+ fixed to strip ?query/#frag)
- [x] `mise run verify` EXIT 0 (incl. #271 index_cue + #273 breadcrumb guards)
- [~] Browser: toggle Tree↔Map, both render from one island; hover-highlight works — VERIFIED via browser click-through (9/9 PASS incl. hover, ?view= write-through, direct ?view=map load, stub redirect). Automated conditional assertion added to run_index_checks; the active fold-in that drives a server hitting the aggregate is #274's parameterization work.

## Validation

Served `--lan` for human review + browser click-through of the toggle and both views. `verify`
green. Coverage folded into `test-navigation.py` (#274).

## Resolution (2026-08-31, commit 53793b1)

Unified page shipped: `library/index.html` = one #page-data island + Tree|Map toggle.
`mise run verify` EXIT 0; browser click-through 9/9 PASS.

Three ACs resolved as deviations (not gaps):
1. **"Shared DomainCard body across views" — SUPERSEDED by research.** The index grid card
   and the committed positioned map `DomainCard` are structurally incompatible (the map card
   derefs `position.x/y` and crashes without a dagre pass). Tree + map each own their node
   markup; the shared surface is the data record + `Ring`. This is the correct design, not a
   shortcut — documented in `.memory/research/unified-graph-views/276-implementation-findings.md`.
2. **"_site deploy on /{repo}/ subpath" — paths verified, full assembly not run.** All paths are
   document-relative (`../assets`, per-output `mapHref`); verified on a local server + verify-links.
   A real `_site` assembly only happens on a v* tag deploy; not exercised this session. Low risk —
   pages.yml copies `library/**` verbatim (incl. the redirect stub) and the paths match the
   proven per-domain scheme.
3. **"Browser folded into #274" — browser VERIFIED; automation fold-in delegated.** The 9/9
   click-through covers the AC behaviors. A conditional two-view assertion was added to
   `run_index_checks` (fires when `.view-toggle` is present); driving the gate's server to hit
   the aggregate index is #274's parameterization scope.

Also: fixed `verify-links.py` to strip `?query`/`#frag` before file resolution (general
correctness, surfaced by the stub's canonical link). `GlobalMapView.js` is now unreferenced
dead code (left in place; a future cleanup can remove it). Per-domain `lessons/index.html`
pages keep the old IndexView (single-domain surface, out of scope) — but note regenerating one
now yields the unified page.

Unblocks #277 (ADR). #266 (concept cross-domain edges) builds on this Map view.
