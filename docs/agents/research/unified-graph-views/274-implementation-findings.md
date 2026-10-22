# #274 Implementation Findings (research + review, 2026-08-31)

Synthesis of 4 subagents (2 Playwright/nav research, 2 internal contract review). Full
detail in `.scratch/research-274/`. Headline: this is a **rewrite**, not a parameterization
— the map page is now a Preact app and the old suite's entire contract is dead.

## The old suite is stale on TWO axes (not just iceberg-hardcoded)

1. **Broken filename:** hardcodes `modern-data-analytics-stacks-map.html`; the real file is
   `data-analytics-map.html`. Steps 9 & 11 `goto` a 404 today.
2. **Dead contract (Preact rewrite):** NO `window.TOPICS`, NO `selectTopic()`, NO
   `#detail-panel` / `#suggestion-banner` / `#mark-complete-btn`, and the hardcoded fills
   `#dcfce7`/`#dbeafe` appear nowhere in generated HTML. Every symbol the old suite drives is gone.
3. **Orphaned:** not in any mise task or `mise run verify` — a manual script, which is why
   the rot went unnoticed.

## Current contract to write AGAINST (map-contract.md, file:line-cited)

- **Data island** (stable across all 9 maps): `JSON.parse($('#page-data').textContent)` →
  `{title, orientation, topics[], leadsTo[], edges[]}`. Each topic:
  `{id(ULID), slug, title, why, prereqs(ULID[]), status, lessonPath}` (generate_map_page.py:270-289).
  `lessonPath` = renamed `lesson_file` (null if none).
- **DOM hooks** (assert on these, not globals):
  - render-ready: `.dag-canvas[data-render-complete="true"]` (MapView.js:99) — poll instead of sleep.
  - per topic: `.topic-card[data-topic-id="<ULID>"]` (TopicCard.js:34).
  - status: `.badge.complete|.in-progress|.not-started` (StatusBadge.js:14) OR `topics[i].status` — NOT fill hex.
  - open lesson: `a.btn.primary[href]` in the card (GenButton.js:44), or `topics[i].lessonPath`.
  - prereqs inline: `ul.prereq-list[aria-label="Recommended prerequisites"]`, `li.prereq-item.met/.unmet`.
  - related: `.leads-to-btn[data-domain]` (MapView.js:118).
  - state API (module-scoped, NOT window): store.js getTopicState/setTopicStatus, keyed by ULID.
- **Breadcrumbs:** the ticket's "2+2 vs 3+3 sub-map" variance DOES NOT EXIST. Every map emits a
  uniform 2-crumb `All Lessons > <Domain>` (page_template.py:348-351, verified all 9). Real depth
  variance is by page TYPE: map=2 crumbs, lesson=3 crumbs (page_template.py:177-181). Latent bug
  (not #274's job): map crumb hardcodes `index.html` with no `../` — breaks only if a map is
  generated at depth>1 (all depth-1 now).

## Domain discovery (domain-discovery.md)

- Parse `library/index.html` `#page-data` -> `domains[]` = `{slug, mapHref, depth, total, ...}`.
  5 roots: godot-gamedev, data-analytics, ink-godot, oidc-rust, workout-fundamentals.
- Enter: Tree `a.ti-row[data-domain="{slug}"]` (default) or Map `a.im-card[data-domain="{slug}"]`
  (`?view=map`). Islands in Map view have NO data-domain (target by href).
- **slug != folder:** data-analytics lives under `iceberg-workspace/`; godot sub-maps under
  `godot-gamedev/`. ALWAYS take the folder from `mapHref.split('/')[0]`.
- Under `library/` root serve: `/index.html` = aggregate; `/{folder}/lessons/{domain}-map.html`.
  `/api/map/*` UNRELIABLE at library root (MAPS_DIR falls back to iceberg) — discover from island.
- **Cue matrix caveat:** all 5 roots are in-progress ON DISK, but overlay counts are gitignored
  and re-bake to 0 on a clean checkout. Derive cue expectations from FILE PRESENCE, not the
  island counts. empty->orientation and all-complete->no-resume can't be exercised from real
  domains (none are empty/complete) — need synthetic fixtures OR assert only existing states.

## Playwright best practices (playwright-param.md, nav-testing.md)

- Loop-of-test (one reported case per domain), per-domain screenshot + attribution. This suite
  uses raw `sync_playwright` (not the pytest runner), so that = one labelled call per domain with
  its own try/except + screenshot + result row (the existing report() pattern, looped).
- Assert NAVIGATION not link-presence: click -> `expect(page).toHaveURL(regex)` -> assert landed
  heading. Prefer `get_by_role('link', name=...)` over CSS (doubles as a11y assertion).
- AVOID `networkidle` + hard `sleep()` (old suite is full of `time.sleep(3)` — flaky). Poll
  `.dag-canvas[data-render-complete="true"]` + web-first retrying assertions.
- Scope breadcrumb clicks to the `aria-label="Breadcrumb"` landmark.

## Revised scope (a REWRITE of test-navigation.py)

1. Discover domains from the aggregate island (no hardcoded slugs/filenames).
2. Per-domain journey: aggregate (enter via `.ti-row[data-domain]`) -> map (poll render-complete)
   -> open a lesson (topics[i].lessonPath) -> its quiz -> breadcrumb back-nav. Per-domain pass/fail + screenshot.
3. Replace ALL dead selectors per the cheat sheet. Assert nav via toHaveURL + heading.
4. Breadcrumb click-through: 2-crumb maps, 3-crumb lessons — assert real nav.
5. Index cue matrix: assert states that EXIST (resume — all 5 in-progress); empty/all-complete
   need synthetic fixtures (defer or fixture).
6. Wire into a mise task (`test:nav`) via the browser agent; document in visual-qa/serve skill.
   Recommend NOT in core `verify` (slower browser journey).

NOT in scope (already in #276 verify-interactive): two-view toggle + tree keyboard.

## Ticket corrections for the resolution
- "2+2 vs 3+3 breadcrumb" premise is wrong — maps are uniform 2-crumb; real coverage is
  map(2)/lesson(3) per-type + the depth-aware `../` prefix on lesson crumbs.
- The stale map filename means the suite is already broken, not merely narrow.
