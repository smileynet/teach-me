# #276 Implementation Findings (research + code review, 2026-08-31)

Synthesis of 4 subagent passes (2 external research, 2 internal review) that refine the
#276 plan. Prototypes in `.scratch/spike-275/`; this doc is the durable "build against"
reference. All internal claims are file:line-cited in `.scratch/research-276/`.

## Corrections to the initial plan

1. **There are TWO `DomainCard`s, not one.** `IndexView.js` defines a LOCAL grid card
   (props `{domain, mission}`, keyed `domain.domain`, reads `domain.description`). The
   committed `assets/components/DomainCard.js` is a POSITIONED map node (props
   `{domain, position}`, keyed `domain.slug`) that dereferences `position.x/y`
   unconditionally — it **crashes without a dagre layout pass**. So the tree view MUST
   use its own row markup (the spike's `.ti-row` is correct). "Shared DomainCard body
   across views" is NOT viable as stated — the three views (grid/tree/map) need three
   node representations. Shared piece is the `Ring` concept + the data record, not the card.

2. **Node-key mismatch.** IndexView reads `domain.domain`; map + tree read `domain.slug`.
   Unify on `slug` in the emitted `#page-data`; components must agree.

3. **`mapHref` is output-path-relative — do NOT bake it into the shared record.**
   `map_links.map_href` does `os.relpath(target, output_file.parent)` — same domain,
   different href per output file. Compute `mapHref` at data-island build time with the
   correct output path. The real MAP.md `path` MUST survive into the shared record (both
   overlay-root inference and href depend on the `maps/`-parent rule).

4. **Keep TWO page_template functions.** `render_index_page` (no breadcrumb, no dagre,
   title "{t} — teach-me") vs `render_map_page` (breadcrumb [All Lessons › domain],
   include_dagre=True, title "Map: {t}"). Merging them is unnecessary; the merged
   generator calls both. Do NOT merge the view JS either.

5. **Depth filtering is OPPOSITE.** Index keeps depth-0 only; forest keeps depth-0 AND
   depth-1 sub-maps as nodes. `build_domain_graph` must return ALL depths; each view
   filters. `find_maps` already excludes depth-2+ via the `--` stem check.

## The unified page architecture (revised)

- **Single page `library/index.html`, ONE `#page-data` superset:**
  `{domains, edges, islands, stats, mission}`. Today index lacks edges/islands; map
  lacks stats/mission — the merge supplies both.
- **Shared header ABOVE the toggle** (mission + #271 start/resume cue + stats). Feed each
  view only `{domains, edges, islands}`; keep header state out of the views. This keeps
  the #271 cue markup where verify-interactive's `run_index_checks` expects it.
- **Three node representations, one data record:** grid card (retire — replaced by tree
  as default), tree row (`.ti-row`, no position), map card (`.im-card`, positioned).

## Shared-core extraction (generators)

New `tools/lib/domain_graph.py`:
- `find_maps(scan_dirs: list[Path]) -> list[Path]` — ONE impl (adopt index's fuller
  version: root + direct `*.MAP.md` + rglob, skip `--`). Delete forest's thinner copy.
- `build_domain_graph(paths) -> list[record]` — load once, compute completion once.
  Record = `{path, domain, title, description, depth, parent, leads_to, total, complete,
  in_progress}`. Kills the duplicated `_completion`/`parse_map_meta` completion math.
- `build_forest_edges(records) -> (edges, islands)` — lifted verbatim from
  `build_forest` 87-101 (parent + leads_to edges; islands = untouched-by-edge).
- MISSION.md parse stays in the index projection (fragile presentation logic — do NOT
  hoist). Drop the dead `math` import. Insert `sys.path` once at module top.
- CLI: one script, `--view index|global|both` (default both), so `index:generate` and
  `map:global` collapse toward one entry point; each still writes its own file with
  output-anchored hrefs.

## Tree view — WAI-ARIA gaps to close (research)

The spike `IndentedTreeView` has `role=tree/treeitem/group` + `aria-level` but is MISSING
the full APG pattern. For accessible PRIMARY nav (the whole point of choosing tree), add:
- `aria-expanded` on PARENT treeitems only (never end nodes — mislabels them as parents).
- `aria-posinset` + `aria-setsize` per item (breaks "where am I" for AT without them).
- Keyboard model: arrows navigate, Right/Left expand-collapse, Home/End jump, type-ahead
  for >7 root nodes; single tabindex roving. (W3C APG treeview.)
- On activation, move focus to the destination's level-1 heading.
- Distinguish focus from selection visually.
Source: https://www.w3.org/WAI/ARIA/apg/patterns/treeview/ [L4:verified].
Prior art: Obsidian's global graph is decorative-not-nav (positions shift each load,
crowds at depth ≥2) — validates tree-as-nav, graph-as-secondary.

## Map view — dagre + fit-to-view (research)

- Measure node HTML offscreen (`getBoundingClientRect`) BEFORE `dagre.layout`; node x,y is
  CENTER — offset by w/2,h/2. Edges as ONE SVG polyline layer BEHIND absolute HTML nodes.
- Fit-to-view: `scale = min(vpW/gW, vpH/gH)` clamp ≤~1.5; one CSS
  `transform: translate() scale()` with `transform-origin:0 0` (crisp text, cheap).
- Set `edgeLabelSpace:false` (no edge labels) — dagre otherwise inserts dummy label
  nodes that inflate spacing.
- **Disconnected-component packing** (the deferred growth item): dagre has NO built-in
  packing — connected-components pass, layout each, bin-pack bounding boxes (shelf/row for
  a few; polyomino packing is research-grade — Freivalds/Dogrusoz/Kikusts 2001; Cytoscape
  exposes `packComponents`). Confirms "do NOT hand-roll a grid" — use the CC+pack approach
  when we get there.
- WCAG 1.4.1: edge-type color must be paired with a second cue (dash pattern + distinct
  arrowhead marker) + legend. Spike already does solid=parent/dashed=leads_to + 2 markers
  + legend — compliant.

## EdgeLayer reconciliation

Committed `EdgeLayer.js` signals dashed on `type==='related'`; the spike's inline map SVG
uses `type==='leads_to'`. TWO options: (a) extend EdgeLayer to treat `leads_to` as dashed
and reuse it, or (b) keep the spike's inline edges (it also adds legend + 2 arrowhead
markers + hover-fade that EdgeLayer lacks). Recommendation: keep the spike's inline edges
for the map view (richer), preserve EdgeLayer's bare-array/`related` back-compat for
per-topic MapView untouched.

## FOUC toggle — exact precedent

`assets/typography-prefs.js` = blocking, import-free IIFE in `<head>` reading
`localStorage['teach-me-prefs-v1']`, applying before paint (scaffolds load it in-head).
`assets/preferences.js` owns the `teach-me-prefs-v1` schema + `prefs` signal.
Toggle plan: add a `mapView: 'tree'|'map'` field to the prefs schema, restore it via a
tiny blocking head script mirroring typography-prefs.js, AND read `?view=map` transiently
on load (for the global-map.html redirect stub). No existing view-toggle key today.

## Inbound-link / verify impact (retiring global-map.html → redirect stub)

- **No committed page hard-links index↔global-map** — the only repoint is the one-way
  redirect stub. No "View global map" button to fix.
- `verify-interactive.py` `_INDEX_PAGES` probes index.html for the #271 cue — the merged
  app MUST keep the cue markup or update assertions. NO global-map interactive check.
- `verify-links.py` #273 breadcrumb guard validates "All Lessons" crumbs land on
  index.html (survives). Redirect stub has no nav → passes.
- `pages.yml` copies `library/**` verbatim (`cp -rL`); the redirect stub must ship in
  `library/` so it's copied. `:62`/`:74` comments naming global-map.html are stale-doc,
  not functional breaks.
- `lint-html.py` index-page rules (needs style.css + theme-toggle.js) must still be met.

## Sequencing

Still blocked by #278 (committed demo overlay) — regenerating this page zeros demo counts
(ink 3/5, iceberg 2, godot 2) without it. #278 first, then #276.

## Second pass (2026-08-31) — gap-filling research + review (`.scratch/research-276b/`)

Fills the "how" the first pass only flagged as needs. Two findings SIMPLIFY the plan.

### SIMPLIFY 1 — no new unified template wrapper needed
`render_index_page` (page_template.py:305-324) is ALREADY the right base for the unified page:
no breadcrumb, index-style title, `include_page_shell=False`. It diverges from
`render_map_page` on exactly TWO axes + title: breadcrumb (index omits) and dagre (index omits
→ False by omission). Fix: add a 2-line `include_dagre=False` PASSTHROUGH to
`render_index_page` and forward it to `_base_page` (backward compatible). Then call it with
`include_dagre=True` for the unified page. The dagre-in-`<head>` + page-data-before-module
ordering `render_map_page` already uses works unchanged (page_template.py:158-163). CAVEAT:
`lint_index` (lint-html.py:78-89) requires `id="app"` in the body — the unified header+toggle
must mount into `#app` (it does). Loading dagre on the index does NOT break any lint rule (the
dagre check is a positive map-only check, not a prohibition).

### SIMPLIFY 2 — the toggle rides existing prefs infra, no new head script
`preferences.js` DEFAULTS (:25-34) + single key `teach-me-prefs-v1` (:17); `load()` spreads
`{...DEFAULTS, ...stored}` (:78). Adding `mapView: 'tree'` at :33 is PURELY ADDITIVE — no
version bump, no migration. `prefs` is a signal (:83); `set()` immutably replaces (:139-141);
one `effect()` saves + applies (:106-110). The Preact island reads `prefs.value.mapView`
REACTIVELY (unlike page-shell.js:33's one-shot read). NO separate blocking head script needed
UNLESS a pre-paint data-attribute is required for first-paint gating (only then touch
`applyToDOM` :96-103). Do NOT create a separate `teach-me-map-view` key — put it in the blob
(keeps the single-source auto-persist contract). No key-collision risk (additive field).

### PRECISION 1 — toggle architecture (research)
Parse the JSON island ONCE at module scope (`const data = JSON.parse(el.textContent)`), never
per-render. Render BOTH views and toggle with CSS `display:none` (NOT conditional unmount —
that discards scroll/hover/focus and rebuilds). Precedence on load:
`view = urlParam ?? storedPref ?? default`; WRITE-THROUGH the resolved value to localStorage;
on user toggle update signal → write localStorage → `history.replaceState` (replace, not push).
Sources: Klepov keep-mounted, preact/signals, SO 5476049.

### PRECISION 2 — tree keyboard (WAI-ARIA APG, verified)
Use ROVING TABINDEX (one treeitem `tabindex=0`, rest `-1`; arrows move real focus + rewrite
tabindex) — native `:focus` + SR tracking work automatically. NEVER mix with
aria-activedescendant. Key handlers (APG-exact): Right=open/first-child; Left=close/parent;
Down/Up=next/prev VISIBLE (no open); Home/End=first/last visible; Enter=activate (follow link);
type-ahead=char→next match (esp. >7 roots). Expand/collapse toggles `aria-expanded` only —
focus STAYS on the node. On activation, move focus to the destination's level-1 heading. Bugs
to avoid: multiple/zero `tabindex=0`, `aria-expanded` on end nodes, Up/Down through collapsed
descendants.

### PRECISION 3 — verify assertions to add
`run_index_checks` (verify-interactive.py:340-388) currently asserts index_renders,
index_cue_present, index_no_js_errors. ADD: (a) toggle present, (b) both views render (click
Map → map island/SVG mounts; click Tree → `.index-view`/tree returns), (c) hover-highlight
(reuse the tooltip-hover idiom :161-176), optional persist-across-reload. `test-navigation.py`
(#274 fold-in) = append numbered steps 15/16/17 (Toggle→Map, →Tree, hover) to its linear
run_tests() using existing report()/screenshot() idioms; the report table auto-picks them up.

### #279 coordination (new since first pass)
#279 will move progress from build-time baking → load-time read with demo fallback. Keep the
counts in `#page-data` (no-JS fallback) but structure the island so #279 can add a client-side
overlay read WITHOUT reshaping it. Don't architect the generator so build-time baking is the
ONLY path. "Don't paint into a corner" — no extra work now.
