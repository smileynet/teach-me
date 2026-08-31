---
id: "274"
title: "test-navigation.py: parameterize over all domains (currently iceberg-hardcoded)"
status: done
blocked_by: []
tags: ["platform"]
---

# test-navigation.py: parameterize over all domains (currently iceberg-hardcoded)

## Why (found during #273 validation, 2026-08-30; scope corrected 2026-08-31 after review)

`tools/test-navigation.py` is the Playwright user-journey suite (index → map → lesson →
quiz → back-nav). Review (`.memory/research/unified-graph-views/274-implementation-findings.md`)
found it is **stale on two axes, not just iceberg-hardcoded** — so this is a REWRITE, not a
parameterization:

1. **Broken filename:** hardcodes `modern-data-analytics-stacks-map.html`; the real file is
   `data-analytics-map.html` (renamed). Steps 9 & 11 `goto` a 404 today.
2. **Dead contract:** the map page is now a Preact + signals app. The suite's symbols —
   `window.TOPICS`, `selectTopic()`, `#detail-panel`, `#suggestion-banner`,
   `#mark-complete-btn`, hardcoded fills `#dcfce7`/`#dbeafe` — **no longer exist** in the
   generated DOM. All must be replaced (cheat sheet in the findings doc).
3. **Orphaned:** not wired into any mise task or `mise run verify` — a manual script, which
   is why the stale filename rotted unnoticed.

Two ticket premises were wrong and are corrected below.

## What to build (rewrite)

- **Discover domains from the aggregate `library/index.html` `#page-data` island**
  (`domains[].slug/mapHref/depth`) — no hardcoded slugs/filenames. NOTE folder ≠ slug
  (data-analytics lives under `iceberg-workspace/`); always take the folder from
  `mapHref.split('/')[0]`.
- **Per-domain journey loop**, one independently-reported case each (own try/except +
  screenshot + result row): aggregate → enter via `a.ti-row[data-domain="{slug}"]` (Tree
  view) → map (poll `.dag-canvas[data-render-complete="true"]`, NOT sleep) → open a lesson
  (`page-data.topics[i].lessonPath` / `a.btn.primary` in the `.topic-card`) → its quiz →
  breadcrumb back-nav. Pass/fail attributed to the specific domain; screenshots per domain.
- **Assert navigation, not link-presence:** click → `expect(page).toHaveURL(regex)` → assert
  landed `<h1>`. Prefer `get_by_role('link', name=...)` over CSS. Scope breadcrumb clicks to
  the `aria-label="Breadcrumb"` landmark.
- **Breadcrumb click-through:** map pages emit a UNIFORM 2-crumb `All Lessons › <Domain>`;
  lesson pages emit 3-crumb `All Lessons › <Domain> › <Title>`. (Correction: the "2+2 vs 3+3
  sub-map" variance in the original ticket does NOT exist — all maps are 2-crumb regardless
  of depth. Real depth variance is by page TYPE, map(2)/lesson(3), with depth-aware `../`
  prefixes on lesson crumbs.) Assert real navigation at each hop.
- **Index cue — resume only (option A):** all 5 real domains are in-progress on disk, so
  assert the resume cue ("Continue where you left off → {domain}") + its click destination.
  The empty→orientation and all-complete→no-resume states can't be exercised from real
  domains (none are empty/complete; overlay counts re-bake to 0 on a clean checkout) →
  DEFERRED to a follow-up ticket (synthetic fixture domain). Not faked here.
- **Wire it in:** add a `test:nav` mise task run via the `browser` specialist against a
  served `library/` root. Recommend NOT in core `verify` (slower browser journey). Document
  in the visual-qa / serve-workspace skill.
- **Latent bug to note (not fixed here):** the map breadcrumb hardcodes `index.html` with no
  `../` prefix — harmless now (all maps depth-1), breaks if a map is ever generated deeper.

NOT in scope — already shipped in #276's `verify-interactive.py`: the two-view Tree|Map toggle
assertion (`index_two_view_toggle`) and the tree keyboard model (`index_tree_keyboard`).

## Acceptance criteria

- [x] Domains discovered dynamically from the aggregate index page-data (no hardcoded slugs/filenames)
- [x] Core journey runs per domain; failures attributed to the specific domain; per-domain screenshots
- [x] All dead selectors replaced with the current Preact contract (page-data island, .topic-card, .badge, lessonPath, etc.)
- [x] Navigation asserted via toHaveURL + landed heading (not link-presence); breadcrumb click-through covered (map 2-crumb, lesson 3-crumb)
- [x] Index resume cue + resume-link destination asserted (empty/all-complete deferred to follow-up per option A)
- [x] Runnable headless via the browser agent (`mise run test:nav`); documented in visual-qa / serve-workspace skill
- [x] Follow-up ticket filed for the empty/all-complete cue matrix (synthetic fixture) — #282

## Resolution (2026-08-31)

Rewrote `tools/test-navigation.py` against the current Preact contract (findings:
`.memory/research/unified-graph-views/274-implementation-findings.md`). It discovers the 5
depth-0 domains from the aggregate `#page-data` island, self-serves the `library/` root
headless, and runs a per-domain journey: aggregate → (Tree row `a.ti-row[data-domain]`) → map
(poll `.dag-canvas[data-render-complete]`) → lesson (`topics[i].lessonPath` / `a.btn.primary`)
→ quiz (LessonActions `.lesson-actions-bar` "Take quiz" button) → breadcrumb back-nav. Nav is
asserted act-then-verify (`wait_for_url` + landed `<h1>`), fresh browser context per domain.

**Verified:** 36/36 checks pass. Quiz navigation actually exercised for 4/5 domains (godot,
data-analytics, oidc, workout — each "1 quiz cards" + quiz→lesson breadcrumb); ink-godot's
first lesson has no quiz yet (legitimate skip). Resume cue → map destination asserted. Clean
server teardown (no orphan). `mise run test:nav` added (NOT in core verify); documented in the
visual-qa skill. `mise run verify` still EXIT 0.

**Ticket corrections made:** (1) the "2+2 vs 3+3 sub-map breadcrumb" premise was wrong — all
maps emit a uniform 2-crumb; real variance is map(2)/lesson(3) per page TYPE, now what the
suite asserts. (2) The suite was already broken (stale `modern-data-analytics-stacks-map.html`
filename + dead Preact-era selectors), so this was a rewrite, not a parameterization.

**Deferred:** empty→orientation and all-complete→no-resume cue states → #282 (synthetic
fixture; can't be produced from the real in-progress library). **Latent bug noted** (not fixed):
map breadcrumb hardcodes `index.html` with no `../` — harmless at depth-1.
