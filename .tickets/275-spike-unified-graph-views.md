---
id: "275"
title: "Spike: index + global-map as two views over one domain-graph island"
status: done
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

## Pre-spike findings (research + code review, 2026-08-30)

Dispatched review + research BEFORE prototyping (raw: `.scratch/subagent-raw/275-*.md`,
`.scratch/research/{view-toggle,shared-data-views}.md`). Several questions are already
answered by inspection; the spike now mostly VERIFIES them in a prototype + makes the two
subjective UX/design calls.

**Q1 data superset — ANSWERED (verify).** The map island is a near-superset; only genuine
deltas are the index's depth-0 filter + `MISSION.md`, and the map's edges/islands. Union shape:
`domains[]{slug, title, description, depth, parent, total, complete, inProgress, mapHref}` +
`edges[]` + `islands[]` + top-level `mission` + `stats`. Key unification: index keys by
`domain`, map by `slug`, SAME value — pick `slug`. **Mission is PAGE-level** (one MISSION.md
per scan-dir, same object to every card) — keep it a top-level island field; NO map_parser
change needed.

**Q2 one generator — ANSWERED (clean).** Inputs already unified (both use `map_parser.load_map`
+ `overlay.status_map_for_map`); only node-record shaping is copy/pasted (title fallback,
completion comprehensions, `map_href`, `find_maps`). Extract `build_domain_graph(scan_dir,
output_file)` emitting the superset; list view filters `depth===0` client-side; `MISSION.md`
parse becomes a separate `build_mission()` bolt-on. **Bug-guard: pass the UNIFIED output path
into `build_domain_graph` so `map_href` relpath anchors on `library/` — else every domain link
404s.**

**COUNT-CLOBBER — CONFIRMED BLOCKER (was a caution, now a prerequisite).** Committed pages ship
real demo counts (ink 3/5, iceberg 2, godot 2 — verified in the HTML) sourced from a GITIGNORED
`.user/status-overlay.json` that `pages.yml:143` even deletes. Any regen on a fresh checkout
re-bakes them to 0. #271 dodged this by NOT regenerating (hand-patched CSS). #276 MUST
regenerate (it merges the generators), so this must be fixed first: **commit a demo overlay
under `library/**/.user/` (un-gitignore under library only) so regen is idempotent, and stop
deleting the library overlay at pages.yml:143.** Needs the demo topics' ULID node-ids
(recoverable from each MAP.md). → This likely warrants its own prerequisite ticket blocking #276.

**Q3 toggle UX — RESEARCH-DECIDED, one call to feel.** Default to LIST (System-1 legible;
graphs are hairball-prone as a cold landing). Segmented `List | Graph` control (not an on/off
switch). Persist `viewMode` to localStorage with a VALIDATED fallback to `list`, applied at a
sync head-script PRE-PAINT (matches the repo FOUC rule / typography-prefs.js) — deferring it
flashes. `global-map.html` → redirect to `index.html?view=map` selects map on first load, then
localStorage takes over. The remaining subjective call: confirm list-default feels right vs the
graph (the reason you raised the reframe) — decide on the served prototype.

**Q4 shared card — ANSWERED (feasible, 2 decisions).** One reconciled `DomainCard`: props
`{domain, mission?, position?}` — the PRESENCE of `position` is the list-vs-map signal (no
`variant` prop). Conditional: absolute `left/top` only when position present; description gated
on `domain.description`; mission fold on `mission?.why`; `is-child` on `depth>0` (harmless on
list). Two genuine DECISIONS the spike must settle: (a) adopt the tri-state ring everywhere
(index's always-`--success` ring is arguably a bug); (b) pick ONE stat-text style (index
"N to explore · M in progress" vs map "N topics, M in progress").

**Q5 deploy — ANSWERED (simplifies, ADR-0015 holds).** Merged page stays `library/index.html`
(depth-1, `../assets`) — the existing shared-root asset copy (pages.yml:64) already satisfies it;
no new copy, root redirect unchanged, `map_href` values identical. `global-map.html` →
generator-emitted redirect stub → `index.html?view=map` (keeps old URLs + verify-links green).
No lesson/reference HTML links to global-map.html (blast radius small; repoint map-page
breadcrumb/forest nav).

**Q6 scale — prototype/reason.** Confirm the map view at 9 nodes and reason about 15+ (research:
graphs hairball without progressive disclosure / clustering — argues for keeping LIST default
regardless of domain count).

**Q7 map layout — taller-than-wider (research CORRECTED my first call).** The forest at
`rankdir:'TB'` is very wide (measured 2118×581, H/W 0.27) because a depth-0/1 tree fans siblings
horizontally per rank. I first prototyped `rankdir:'LR'` (measured 1128×1023, H/W 0.91) and was
about to recommend it — but research REJECTS LR for depth hierarchies: LR rotates depth onto the
horizontal axis (landscape, fights a portrait canvas) and doesn't aid parent→child comprehension
(eye-tracking evidence; LR only helps horizontal PROCESS flows). The LR prototype was tall only
because the ISLANDS stacked vertically, not because the tree improved. CORRECTED direction:
 - **Keep TB** (root-on-top, depth = vertical scroll axis — the hierarchy convention).
 - **Wrap the wide sibling tier into 2-3 columns/rows** so siblings don't overflow width (trade
   horizontal spread for vertical scroll while staying TB). This is the real fix for the width.
 - **Fix the islands duplication** (research: never render the same node in BOTH canvas and
   sidebar — we do exactly that today; false-proximity + double-identity). Pick ONE home: either
   pack islands into a labeled canvas tray, OR sidebar-only and OMIT from the graph. Sidebar-only
   also removes their layout distortion.
 - **Consider a spanning-tree layout + overlaid `leads_to` edges** (data is mostly parent/child +
   a few cross edges) rather than full Sugiyama/dagre — standard pattern, but only if the column-
   wrap TB doesn't suffice. Defer unless needed.
 - Safe + local: EdgeLayer is a dumb renderer (`orient="auto"` arrowheads, consumes dagre points)
   → ZERO edge changes for any direction. GlobalMapView layout is FULLY ISOLATED from MapView
   (separate dagre graphs) → no leak. Only 2 consumers of dagre/EdgeLayer.
 - This is a #276 map-view layout task; the spike records the corrected direction + evidence.

**Q8 responsive / adaptive width — PROTOTYPED + screenshot-verified (Playwright, 4 widths).**
The map is absolute-positioned from a fixed-px graph, so unlike the flow-based list it does NOT
reflow for free. Screenshots at 1440/900/600/390:
 - Fixed 698px canvas: at 600px MKToon clips off-screen; at 390px EVERY card clips right. Unusable on mobile.
 - List view: perfect at every width (single-column flow, full text) — confirms it's the naturally-responsive representation.
 - FIX prototyped: width-aware `computeLayout` — a resize handler reads `.dag-container` width and
   picks `wrapCols` = clamp(1..3, floor(avail/350)). Re-shot: 600px→1 col (348px), 390px→1 col
   (clean vertical chain, 348×1117, no clipping), desktop→2 cols. Verified in screenshots.
 - Emergent: at 1 column all edges flow DOWNWARD (the shared-child upward-edge wrinkle disappears);
   the single column doubles as a rough topological spine.
 - **Responsive strategy for #276:** list view = flow, naturally responsive, the default (mobile-perfect
   as-is). Map view = resize-driven re-layout (ResizeObserver → adaptive wrapCols), collapsing to one
   vertical column on mobile. Two desktop polish items: (a) cap+center the canvas (currently left-anchored,
   wastes right half of a wide viewport) or use width for a 3rd column; (b) style `leads_to` edges distinctly
   from `parent` edges (the upward-edge case in multi-column). Both are #276 polish, not spike.
 - Evidence: `.scratch/spike-275/shots/*.png` (map-{1440,600,390}, list-390) + image analysis in session.

**Architecture (research):** one SSOT + derived projections — the depth-0 list is a
`useMemo(() => nodes.filter(n => n.depth===0))`, NOT stored state (storing derived state is the
#1 sync-bug trap). Shared card branches ONLY on presentation; split only if data shapes diverge.

## REVISED two-view model (user decision, 2026-08-30) — Tree | Map

After spiking three viz types (dagre, sectioned card-grid, indented tree) with screenshots at
desktop+mobile, the model changed:
- **Primary/default view = INDENTED TREE** (Option B, `IndentedTreeView.js`) — REPLACES the flat
  list/card-grid. WAI-ARIA `tree` pattern: explicit parent/child nesting, compact (whole forest at
  a glance), accessible by default, `leads_to` as inline "→ also leads to X". Desktop compact;
  mobile functional (indent a bit cramped — a #276 polish item).
- **Secondary view = dagre NODE-LINK MAP** (Option C) — KEPT but ITERATED to be genuinely good.
  This is a LOWER bar than "primary nav" (the tree owns that), so the earlier "drop dagre for nav"
  research still holds — dagre survives only as the optional relationship view.
- Toggle is now **Tree | Map** (not List | Map).

### Map (Option C) iteration plan — research-ranked, small-graph priorities
Build order (research: at 9-30 nodes the graph already fits, so classic hairball advice inverts):
1. **Responsive fit-to-view via CSS transform** (NOT SVG viewBox — nodes are HTML `<a>` cards with
   rings + CSS hover; SVG-ifying loses that). Wrap `.dag-canvas` in `transform: translate()scale()`,
   `transform-origin:0 0`; cards + SVG EdgeLayer scale together; `computeLayout`/EdgeLayer untouched.
   Fit = math on `layout.width/height`. Kills dead-canvas / no-reflow. `.dag-container` becomes a
   fixed-height overflow-clip frame.
2. **Edge-type encoding + legend** — biggest decorative→useful lever. Today parent & leads_to render
   IDENTICALLY (EdgeLayer only branches `type==='related'`). Make: SOLID = parent (structural),
   DASHED = leads_to (navigational); arrowheads = direction only; color redundant reinforcement;
   LEGEND showing the non-color cue (WCAG 1.4.1). Edit EdgeLayer per-type style map + 2nd marker.
   NOTE vocab mismatch: EdgeLayer knows 'related'/'prereq' (MapView); forest uses 'parent'/'leads_to'
   — branch on those, keep bare-array back-compat (EdgeLayer/DomainCard are SHARED with MapView).
3. **Hover-neighbor-highlight + fade the rest** — onMouseEnter/onFocus on DomainCard → hoveredSlug
   state → adjacency from layout.edges → EdgeLayer highlight class. Answers "what connects to what".
4. **Click-to-navigate + tooltip** (card is already an `<a href>`).
5. Edge-type filter toggle = optional stretch. SKIP free zoom/pan, expand-collapse, force/drag.

### Layout polish (research): fix dead space + backward edges WITHOUT the manual grid
- REVERT the spike's `wrapCols` hand-rolled grid (SpikeMapView.js:56-99) — it abandons dagre, only
  handles parent edges, rebuilds edges as naive straight lines (makes cross-edges WORSE). Base =
  plain dagre `computeLayout`.
- KEEP the spike's `dropIslands` filter (kills dead canvas) — islands go to a sidebar/tray, ONE home.
- Correct forest-packing = per-connected-component dagre + bounding-box packing (not a manual grid).
- Backward-arrow/shared-child fix = raise `weight`/`minlen` on structural parent edges (keeps them
  short/straight; pushes shared children down-rank); `acyclicer:'greedy'` if cycles.
- Curved edges: selective only (separate a solid+dashed pair between the same nodes); default straight.
- Isolation confirmed: forest layout is separate from per-topic MapView (its own dagre) — safe.

## Spike remaining work (throwaway)

The heavy questions are answered by review. The prototype now VERIFIES + makes the calls:

1. Build the unified island (one `build_domain_graph` prototype) + reconciled `DomainCard` +
   `List | Graph` segmented toggle (localStorage, pre-paint restore) in `.scratch/` or a branch.
2. Serve `--lan`; make the two design calls on the real thing: (a) list-vs-graph default feel,
   (b) tri-state ring everywhere + which stat-text style.
3. Confirm the count-overlay fix shape (commit a demo overlay) unblocks idempotent regen — enough
   to size the prerequisite ticket.
4. Findings doc: Q1-Q6 answered w/ evidence + the two design decisions + a recommendation, and
   whether the count-overlay work should be a separate ticket blocking #276.

## Acceptance criteria

- [x] Prototype renders Tree⇄Map from ONE unified island with a persisted toggle (throwaway)
- [x] Viz TYPE reconsidered (user push): 3 types spiked (dagre / sectioned grid / indented tree) w/ screenshots
- [x] Count-overlay fix validated as prereq → spun out as #278 (blocks #276)
- [x] Findings doc answers Q1-Q8 w/ code refs + screenshots; recommends PROCEED
- [x] Recommendation on splitting the count-overlay fix into a prerequisite ticket blocking #276 (→ #278)
- [x] Feeds #276 plan (updated to Tree|Map + iterated map) + #277 ADR options (no production code shipped from spike)

## Resolution (closed 2026-08-30)

PROCEED with #276. Decided: unified page, **Tree** (primary, replaces list — ARIA tree, accessible,
compact) **| Map** (secondary, ITERATED dagre — fit-to-view + edge-type encoding/legend +
hover-neighbor-highlight + islands sidebar). All prototyped + browser-verified in `.scratch/spike-275/`;
final findings in `.scratch/spike-275/FINDINGS.md`. Prereq #278 (commit library demo overlay).
Two mid-spike corrections recorded (LR mis-call; reverted wrapCols manual grid) — the viz-type
reconsideration only surfaced because the user pushed to research alternatives rather than patch dagre.

## Validation

Serve the prototype `--lan` for human view; toggle list↔map, confirm both render from one island,
counts survive a regen with the committed demo overlay. Findings reviewed before #276 starts.
