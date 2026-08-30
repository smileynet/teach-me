---
id: "273"
title: "Nested lesson pages emit sibling breadcrumb links (wrong depth) — 404 on static host"
status: open
blocked_by: []
---

# Nested lesson pages emit sibling breadcrumb links (wrong depth) — 404 on static host

## Why (found during #272 static-deploy validation, 2026-08-30)

Pages that live in a `lessons/{subdir}/` folder emit breadcrumb links authored as if the
page were directly in `lessons/` — they point to `index.html` and `{domain}-map.html` (or
`{track}-map.html`) as **siblings**, but those targets live one level UP in `lessons/`.
The breadcrumb depth is off by one for nested pages.

serve.py masks the `index.html` half (its `_root_index` rewrites any nested `**/index.html`
to the served-root aggregate), but the map-link half breaks even under serve.py, and both
break on a static host. Found by the #272 `_site` link resolver — 12 broken relative refs,
all this one class:

- `library/godot-gamedev/lessons/blender-texture-prep/*.html` (5 pages) →
  `blender-texture-prep-map.html` + `index.html` (both actually at `lessons/`, need `../`).
- `library/iceberg-workspace/lessons/review/quick-check.html` →
  `data-analytics-map.html` + `index.html` (both at `lessons/`, need `../`).

Root cause is in the breadcrumb generation: nested-page crumbs use a bare relative target
instead of prefixing `../` per nesting level (the same `"../" * depth` logic the asset
prefix already uses in `page_template._base_page`). The breadcrumb builder
(`page_template._breadcrumb` / `render_lesson_page` crumbs, and the blender/quick-check
generators) does not account for pages nested below `lessons/`.

NOT a #272 deploy concern — #272 assembles assets at correct depth (0 asset misses). This
is a page-authoring/generation defect. Fix at the generator so re-generated pages get the
right depth, then re-render the affected committed pages.

## What to build

- Fix the breadcrumb depth calc so a page at `lessons/{sub}/…` prefixes `../` per level
  below `lessons/` for the "All Lessons" (`index.html`) and domain/track map crumbs.
- Re-render the 6 affected committed pages (5 blender sub-track + iceberg quick-check).
- Add a check (extend `tools/check-maps-forest.py` or verify-links) that resolves breadcrumb
  targets from each page's actual on-disk location, so this regression is caught in `verify`.

## Acceptance criteria

- [ ] Breadcrumb generator prefixes `../` correctly for pages nested below `lessons/`
- [ ] All 6 affected pages re-rendered; their `index.html` + map crumbs resolve on disk
- [ ] A `verify` check resolves breadcrumb targets relative to page location (regression guard)
- [ ] `_site` link resolver (from #272) reports 0 broken nav refs for these pages
