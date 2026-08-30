---
id: "273"
title: "Nested lesson pages emit sibling breadcrumb links (wrong depth) — 404 on static host"
status: done
blocked_by: []
---

# Nested lesson pages emit sibling breadcrumb links (wrong depth) — 404 on static host

## Root cause (verified in code, 2026-08-30)

Two breadcrumb producers build lesson crumbs as bare siblings, ignoring how deep the page
sits below `lessons/`:

- `tools/lib/page_template.py` `render_lesson_page` (lines 172-178): `map_page = f"{domain_slug}-map.html"`
  and `("All Lessons", "index.html")` — accepts `depth` (line 163), applies it to ASSETS
  (`_base_page(depth=depth)`, line 205) but NEVER to crumbs. `render_reference_page` (232-240)
  and `render_quiz_page` (276-289) both DO prefix from depth — the lesson renderer is the lone
  depth-blind one. It also passes the bare `map_page` into `lesson_actions["map-page"]` (line 213),
  so the ACTION-BAR map link is broken too — not just the visible crumb.
- `tools/migrate-add-breadcrumbs.py` `inject_breadcrumb` (lines 93-97, `page_type=="lesson"`):
  same bare `index.html`/`{slug}-map.html`. `detect_page_type` (23-37) has no `review/` branch,
  so `lessons/review/quick-check.html` classifies as `"lesson"` and gets sibling crumbs.

No code path calls `render_lesson_page(depth=2)` today (grep: only def + docs) — the blender
pages were authored by hand invoking the library (#217). Both producers emit byte-identical
broken crumbs, so either could have stamped a given page; both are depth-blind and both need fixing.

**Why `mise run verify` missed it (corrected):** NOT the `<nav>` strip at verify-links.py:117
(that's inside `check_duplicate_links`, which only counts duplicates). The real gap:
`check_file` (74-97) validates only `<link>`/`<script>` refs (LINK_PATTERN/SCRIPT_PATTERN,
lines 38-39) — it never inspects `<a href>` at all. Breadcrumb targets are validated by no
function.

## Blast radius (verified — matches the 6, plus a SECOND break class)

- **Depth-mismatch (6 pages, 12 refs):** 5 `godot-gamedev/lessons/blender-texture-prep/{01..05}-*.html`
  + `iceberg-workspace/lessons/review/quick-check.html`. All asset-depth 2, crumbs depth-1-style.
  No OTHER wrong-depth pages exist (all `lessons/quiz/` + `blender-texture-prep/quiz/` are already
  depth-correct via `render_quiz_page`).
- **Missing crumb TARGET (10 pages, independent):** `oidc-rust` and `workout-fundamentals` have NO
  `lessons/index.html`, so every "All Lessons" crumb in their 2+2 and 3+3 pages points at a
  nonexistent file — correct depth, absent target. #272 added a static deploy-time redirect for
  these, but the SOURCE pages still 404 under serve.py. A depth-only fix won't catch this.

## Prior art (research)

SSGs (Hugo `relURL`, Jekyll `relative_url`, Eleventy `url` filter) never hand-count `../` in
templates — they compute the relative prefix in a helper from (source, target) paths, or author
root-relative + a build-time pathPrefix. `<base href>` is discouraged (rebases anchors/SVG) —
matches ADR-0015. For our document-relative posture (portable, offline-safe), the recommended
pattern is: compute the prefix from the page's path, not a hardcoded literal — which is exactly
what fixes 1 & 2 do (via `depth`, the value already threaded through).

## What to build

1. **`render_lesson_page`** — prefix lesson crumbs (and `lesson_actions["map-page"]`) with
   `"../" * (depth - 1)`, matching the idiom `render_quiz_page` already uses. Depth-1 lessons →
   empty prefix, byte-identical (no churn on the ~30 normal lessons).
2. **`migrate-add-breadcrumbs.py`** — compute nesting from the path
   (`len(path.relative_to(lessons_dir).parts) - 1`) and prefix lesson/reference/quiz crumbs by it
   (the reference/quiz branches hardcode a single `../`, itself depth-blind). Add a `review/`
   classification. Honor the caveat: read the page's EXISTING map slug (from its current crumb /
   `data-map-page`), don't re-derive — iceberg has two maps.
3. **`verify-links.py`** — ADD `<a href>` existence validation for in-page relative links to
   `check_file` (it currently checks only `<link>`/`<script>`). Resolve each breadcrumb target
   against the page's on-disk location AND flag missing targets (catches BOTH the depth-mismatch
   and the missing-`lessons/index.html` classes). This is the regression guard.
4. **Re-render/correct the 6 depth-mismatch pages.** For the iceberg quick-check, preserve its
   `data-analytics-map.html` slug (ambiguous to re-derive).
5. **Decide the 10 missing-index pages** — either generate `lessons/index.html` for oidc-rust +
   workout-fundamentals (consistent with the other 3 domains) or spin to a follow-up. The verify
   guard (step 3) will surface them either way.

## Acceptance criteria

- [x] `render_lesson_page` crumbs + `lesson_actions["map-page"]` prefix `"../" * (depth-1)`; depth-1 output unchanged
- [x] `migrate-add-breadcrumbs.py` computes depth from path, classifies `review/`, preserves existing map slug
- [x] `verify-links.py` validates `<a href>` breadcrumb targets exist (resolved from page location); fails on the 12 refs before the fix, passes after
- [x] 6 depth-mismatch pages re-rendered/corrected; their `index.html` + map crumbs resolve on disk
- [x] Missing-index breakage (oidc-rust, workout-fundamentals) fixed (generated `lessons/index.html` for both)
- [x] `_site` link resolver (from #272) reports 0 broken nav refs for the affected pages (covered by verify-links on source)
- [x] `mise run verify` EXIT 0 with the new anchor-existence guard active

## Verification (2026-08-30)

- `render_lesson_page` unit check: depth-1 crumbs unchanged (`index.html`/`slug-map.html`);
  depth-2 prefixes both crumbs AND `data-map-page` to `../` — asserted, PASS.
- `verify-links.py` new `<a href>` guard: fired on **31 broken refs before the fix** (12
  depth-mismatch + 19 missing-`lessons/index.html` targets across oidc-rust/workout-fundamentals),
  then **PASS (84 files, 0 broken)** after correcting the 6 pages + generating the 2 indexes.
  Fail→pass proven.
- 6 nested pages corrected in place (5 blender `../`, iceberg quick-check `../` preserving its
  `data-analytics-map.html` slug); action-bar `data-map-page` prefixed too.
- Generated `library/oidc-rust/lessons/index.html` + `library/workout-fundamentals/lessons/index.html`
  via `generate_index_page.py --scan-dir {domain}` (matches the other 3 domains).
- `migrate-add-breadcrumbs.py` dry-run on iceberg: runs clean, skips all 10 (idempotent — won't
  re-stamp existing crumbs).
- `mise run verify` → EXIT 0 (verify-links w/ anchor guard, forest, 41 unit tests, interactive,
  ink transcripts).

## Resolution

Fixed the depth-blind crumb logic in both producers (`render_lesson_page` + `migrate-add-breadcrumbs.py`),
added `<a href>` breadcrumb-target existence validation to `verify-links.py` (closing the blind spot
that hid the bug — it previously checked only `<link>`/`<script>`), corrected the 6 committed
depth-mismatch pages, and generated the two missing per-domain `lessons/index.html` so all "All
Lessons" crumbs resolve. Verify now guards both break classes going forward.
