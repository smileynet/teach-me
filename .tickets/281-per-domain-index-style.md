---
id: "281"
title: "Decide per-domain lessons/index.html style (old IndexView vs unified two-view)"
status: done
blocked_by: []
tags: [platform]
---

# Decide per-domain lessons/index.html style (old IndexView vs unified two-view)

## Context

#276 rewrote `generate_index_page.py` to produce the unified Tree|Map page (UnifiedView).
But the five per-domain `lessons/index.html` pages were NOT regenerated — they still use
the old `IndexView` (card-grid dashboard, single domain). This creates two conditions:

1. **Inconsistency:** the aggregate is unified, per-domain pages are old-style. Not broken
   (both render, verify passes), but visually different.
2. **Latent behavior change:** anyone who regenerates a per-domain index now gets the
   unified page — which shows a Tree|Map toggle for a single domain (one node, no edges).
   That's functional but odd.

## Options

**A. Detect single-domain in the generator, skip the toggle/map-view.** The generator
checks `len(roots) <= 1 and len(edges) == 0` and emits the old-style IndexView (or a
simplified UnifiedView with the toggle hidden). Per-domain pages get a clean single-domain
dashboard; the aggregate gets the full toggle. Cost: a conditional branch in the generator +
possibly keeping IndexView alive.

**B. Regenerate per-domain pages to unified, accept the toggle.** A single domain with
one root and zero edges renders a tree with one item and a map with one card — harmless if
not visually impressive. Ship it for consistency, revisit if it looks bad. Cost: regenerate
5 pages, accept the diff churn.

**C. Leave as-is (don't regenerate).** Per-domain pages keep the old style. The
inconsistency is cosmetic; lesson breadcrumbs ("All Lessons") land on these pages and they
still work. Cost: none now, but drift accumulates if IndexView and UnifiedView diverge.

## Acceptance criteria

- [x] A decision is made and documented (ADR or ticket resolution)
- [x] Per-domain `lessons/index.html` pages are in the chosen style
- [x] No verify regression

## Resolution

**Option A, content-driven.** `generate_index_page.py` `main()` now branches on
`single = data["stats"]["domainCount"] <= 1 and not data["edges"]`:
- single (no cross-domain edges) → clean `IndexView` via a trimmed `_INDEX_MODULE_SCRIPT`
  (keeps the #279 load-time `resolveProgress` count override against the domain's `topicIds`;
  drops the Tree|Map view-resolution block + the demo-takeover banner), `include_dagre=False`.
- has edges (sub-maps) → `UnifiedView` unchanged.

The discriminator is **edge-presence, not node count** — and it's content-driven (add a
sub-map → the page auto-gains the relationship view; no per-page config, no style toggle —
the modal-switch anti-pattern the "Single-Axis Preferences" steering warns against). Of the 5
regenerated per-domain pages: oidc-rust, workout-fundamentals, ink-godot → IndexView (no
toggle); godot-gamedev (4 nodes/5 edges) + iceberg-workspace (2 nodes/1 edge) → UnifiedView
(they have real sub-map structure the toggle navigates). `IndexView` stays live.

Added `tools/check-index-drift.py` (in `mise run verify`): regenerates the aggregate + all
per-domain index pages IN PLACE + `git diff` — non-empty = drift, fail. In-place (not temp)
is required because `map_href` is document-relative to the output's real `../maps/` sibling; a
temp copy can't reproduce the committed hrefs (and cross-drive temp breaks `os.path.relpath`
on Windows — both found + fixed during impl). This prevents the exact stale-artifact drift
that motivated #281.

Decision recorded as an ADR 0016 amendment (Consequences → per-domain resolution).

**Verification:**
- Render (single-workspace serve, no root-normalization): oidc-rust `mounted, toggle=False,
  cue=1`; godot-gamedev `mounted, toggle=True, cue=1` — both correct.
- `mise run check-maps` 10/10; `mise run verify` EXIT 0 (drift guard clean once pages committed).

**Follow-up filed — #284:** serve.py's `_root_index` normalizer shadows per-domain pages
under a multi-domain root serve (they're live on the deployed static host but unreachable via
`mise run serve` on `library/`). Serve-routing concern (ADR 0015 territory), out of #281's
style scope.

## References
- `tools/generate_index_page.py` — the unified generator (`build_page_data`, `main`); a
  single-domain branch (Option A) would gate on `len(roots) <= 1 and not edges` here.
- `assets/components/IndexView.js` — the old card-grid still used by per-domain pages (would be
  kept for Option A/C, retired for Option B).
- `assets/components/UnifiedView.js` — the two-view component per-domain pages would adopt for Option B.
- The 5 per-domain pages: `library/{godot-gamedev,iceberg-workspace,ink-godot,oidc-rust,workout-fundamentals}/lessons/index.html`.
- ADR 0016 Consequences ("grid retirement is AGGREGATE-only; per-domain deferred to #281") — the
  decision this ticket owns; record the outcome as an ADR 0016 amendment or a new ADR.
- Lesson breadcrumbs' "All Lessons" crumb lands on these per-domain `lessons/index.html` (verify-links #273 guard) — whatever style is chosen must keep that target valid.

**Leaning (not decided):** Option A (single-domain branch → keep the clean grid) avoids a
one-node Tree|Map toggle that adds no value for a single domain; but Option C (leave as-is) is
zero-cost if the cosmetic inconsistency is acceptable. Decide against the #279 direction first —
if #279 moves to load-time rendering, the generator changes anyway.
