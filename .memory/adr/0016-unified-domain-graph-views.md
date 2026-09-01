# 0016 — Index and Global Map Are Two Views of One Domain Graph

**Status:** accepted
**Date:** 2026-08-31

> Written after the implementation shipped (#276, commit 53793b1). This is an as-built
> record: the context is reconstructed from the #275 spike, the tickets, and the merged
> code — not from memory — and the consequences below are OBSERVED outcomes, distinguished
> where noted from the decision-time drivers. The technical claims were verified against the
> shipped code by an independent auditor pass (`.scratch/research-277/verify-claims.md`,
> `audit.md`: 18 agree, 0 contradict).

## Context

ADR 0014 made the committed content graph first-class: typed, `why`-annotated edges
(`prereq` / `leads_to` / `related`), immutable ULID node ids, derive-don't-store. This ADR
decides the PRESENTATION layer atop that schema — how the aggregate, cross-domain view of
the graph is rendered.

Before #276, that presentation was **two pages that were really two renderings of one
graph**:

- `generate_index_page.py` → a card-grid "All Lessons" dashboard (`lessons/index.html`).
- `generate_global_map.py` → a dagre "forest map" of domains as nodes (`global-map.html`).

Both walked the same MAP.md files, loaded the same parser, and computed the same per-domain
completion from the same overlay — **the derivation was duplicated** (verified: identical
`status_map_for_map` + sum comprehensions in `parse_map_meta` and `_completion`), and each
page carried its own unrelated `DomainCard` definition. Two generators, one dataset.

Two constraints shaped the choice:

- **#271 (low-cognitive-load landing):** the aggregate landing is the learner's entry
  point and must be scannable and accessible. A node-link graph is poor PRIMARY navigation
  — unstable force/dagre layout, crowding at scale, weak keyboard/screen-reader story
  (WAI-ARIA APG + Obsidian prior art: the global graph is "secondary to the main
  experience", disorienting for wayfinding).
- **ADR 0015 (document-relative assets):** any unified page must keep `../assets`
  document-relative paths and per-output-file `mapHref` — never root-relative — so it
  resolves on localhost AND the GitHub project-pages `/{repo}/` subpath.

The #275 spike (`.memory/research/unified-graph-views/`, `.scratch/spike-275/`) reframed the
problem: these are not two pages, they are **two views over one dataset** — the established
**Multiple Coordinated Views** pattern (Baldonado et al.'s "Rule of Parsimony": add a view
only when one cannot do the job) over a **single source of truth**.

## Decision

**The aggregate index and the global map are ONE page (`library/index.html`) rendering ONE
domain-graph data island as two coordinated views, behind a persisted toggle.** (#276)

1. **One data island, one derivation.** A single `#page-data` island
   `{domains, edges, islands, stats, mission}` feeds both views. The derivation is extracted
   to `tools/lib/domain_graph.py` (`find_maps` + `build_domain_graph` + `build_forest_edges`),
   computing completion ONCE. `generate_index_page.py` is the sole generator; the duplicate
   derivation is gone. `domains` carries ALL depths (0 + sub-maps); `stats` counts depth-0
   domains only (the historical "domains" meaning).

2. **Primary/default view = indented Tree.** A WAI-ARIA tree (`role=tree/treeitem/group`)
   with the full APG roving-tabindex keyboard model. Parent/child = DOM nesting (the
   accessible artifact); `leads_to` shown inline as "→ also leads to X". The Tree is the
   navigation backbone — hierarchy anchors, predictable wayfinding.

3. **Secondary view = iterated dagre Map.** Fit-to-view via a CSS transform (cards stay HTML
   `<a>` nodes), edge-type encoding (solid = parent / dashed = `leads_to`) + legend
   (WCAG 1.4.1), hover-neighbor-highlight, islands in a sidebar. The graph AUGMENTS —
   relationship discovery, not wayfinding.

4. **Persisted toggle.** `mapView: 'tree'|'map'` added to the `teach-me-prefs-v1` signal
   store (additive to DEFAULTS — no migration). Resolution on load:
   `?view=map ?? stored pref ?? 'tree'`, written through to the pref. Both views are
   rendered and swapped with CSS `display:none` (preserves per-view scroll/hover/focus).

5. **`global-map.html` retired to a redirect stub** → `index.html?view=map`. The URL is
   preserved for old links; no live cross-link needed repointing.

## Alternatives considered

- **(a) Keep two separate pages + cross-link only.** Rejected: perpetuates the duplicated
  derivation and the two `DomainCard` definitions the #275 spike proved were one dataset.
  Buys nothing over unification.
- **(b) Replace the index WITH the global map as the landing.** Rejected on the #271
  cognitive-load constraint, corroborated by prior art: a node-link graph is poor primary
  navigation (unstable layout, crowding, weak a11y/keyboard). Obsidian's own community treats
  the global graph as secondary; MDN/Mintlify/VS Code all make a tree/sidebar the primary
  spine. Tree owns nav; the graph is the secondary relationship view.
- **(c) Unified two-view model (chosen).** One island, Tree-primary + Map-secondary,
  persisted toggle. Satisfies #271 (accessible tree default), ADR 0015 (document-relative),
  and removes the duplication — at the cost of the reconciliation work in Consequences.

## Consequences

**Easier:**
- One derivation (`build_domain_graph`), one landing page, one deploy surface. A whole class
  of "two generators drifting" bugs is structurally impossible.
- The default view is accessible primary navigation (Tree, roving-tabindex APG); the Map is
  one click / `?view=map` away for relationship discovery.
- `global-map.html` stays a valid URL (redirect stub) with no cross-links to maintain.
- The Map's fit-to-view scales to the current forest without a dead-canvas sprawl.

**Harder / risks:**
- **Three node representations, not one shared card.** The #276 ticket's "shared DomainCard
  across views" AC was SUPERSEDED by evidence: the grid card and the legacy positioned map card
  (`assets/components/DomainCard.js`, which dereferences a dagre `position` and crashes without a
  layout pass) are structurally incompatible. The shipped views instead use their own row/card
  markup (`IndentedTreeView`'s `.ti-row`, `IteratedMapView`'s `.im-card`) and share only the data
  record + a `Ring`, not a card component. This is the correct design, not a shortcut.
- **Scope of the "grid retirement" is the AGGREGATE page only.** The card-grid `IndexView`
  (and `assets/components/DomainCard.js`) are replaced ONLY on the aggregate landing. Per-domain
  `library/*/lessons/index.html` pages still render the old `IndexView`; regenerating one now
  yields the unified page. That per-domain style decision is deferred to #281 — do NOT read
  this ADR as retiring the grid codebase-wide.
  - **#281 RESOLVED (2026-09-01):** the generator now CONTENT-DRIVES the choice — a
    single-domain page with no cross-domain edges (`domainCount <= 1 and not edges`) renders the
    clean `IndexView` (no Tree|Map toggle — chrome for one zero-edge node); a domain WITH
    sub-maps (real internal `parent` edges — e.g. godot-gamedev, iceberg-workspace) renders the
    `UnifiedView` because the toggle then navigates real structure. The discriminator is
    **edge-presence, not node count**, and it's derived from content (add a sub-map → the page
    auto-gains the relationship view; no per-page config). NOT a style toggle (that would be the
    modal-switch anti-pattern the "Single-Axis Preferences" steering warns against). `IndexView`
    stays live for the single-domain path. A `tools/check-index-drift.py` gate (in `verify`)
    regenerates all index pages in place + `git diff` to prevent the stale-artifact drift that
    motivated #281. KNOWN LIMITATION (follow-up): serve.py's `_root_index` normalizer shadows
    per-domain pages under a multi-domain root serve — they're live on the deployed static host
    but unreachable via `mise run serve` on `library/`. Tracked separately (serve routing, not
    page style).
- **View preference is UI state, NOT the learner state ADR 0014 keeps out of the browser.**
  ADR 0014 §B.6 bars a browser store for LEARNER state (progress/overlay). The `mapView`
  preference in `teach-me-prefs-v1` localStorage is UI presentation state — a distinct
  category. This does not violate 0014; the two must not be blurred.
- **Steering interaction (permitted).** The `Tree | Map` toggle is a PERMITTED distinct-view
  switch under the "Single-Axis Preferences" steering, which is scoped to the reading panel and
  explicitly exempts "genuinely distinct page types" and coordinated multi-property views. It is
  not the discouraged modal toggle that steering warns against.
- **Deferred growth (not a blocker):** multiple root trees stack side-by-side in the Map;
  per-connected-component dagre + bounding-box packing is the fix WHEN domains grow past ~15.
  Do NOT hand-roll a grid (reverted in the spike — it abandons dagre routing).
- `GlobalMapView.js` is now unreferenced (removed). `IndexView.js` remains live for per-domain
  pages until #281.

## Related ADRs

- **Builds on ADR 0014** (committed content graph + minimal overlay) — this is the
  presentation layer atop 0014's schema (typed edges, ULID ids, derive-don't-store).
- **Spans ADR 0012** (two-tier committed library) — the views render the whole library.
- **Obeys ADR 0015** (document-relative assets, unifying root) — `../assets` + per-output
  `mapHref`, never root-relative.
- **Instantiates ADR 0008/0005** — the toggle + views are Level-5 full Preact components on the
  vendored Preact + Signals + dagre stack.

## Implemented by
- **#275** spike (decision + prototypes) → **#276** implementation (commit 53793b1:
  `domain_graph.py`, `UnifiedView`/`IndentedTreeView`/`IteratedMapView`, unified generator,
  redirect stub). **#274** rewrote the nav suite for the new contract.
- Follow-ups (not blocking): **#279** (load-time overlay read may retire the build-time count
  baking), **#281** (per-domain index style), **#282** (index cue-matrix synthetic fixture),
  **#278** (committed demo overlay, already done — keeps regen idempotent).
