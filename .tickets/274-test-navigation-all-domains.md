---
id: "274"
title: "test-navigation.py: parameterize over all domains (currently iceberg-hardcoded)"
status: open
blocked_by: []
tags: ["platform"]
---

# test-navigation.py: parameterize over all domains (currently iceberg-hardcoded)

## Why (found during #273 validation, 2026-08-30)

`tools/test-navigation.py` is the Playwright user-journey suite (index → map → lesson →
quiz → back-nav). It's hardcoded to **iceberg-workspace**: `modern-data-analytics-stacks-map.html`,
`0001-iceberg-metadata-tree.html`, and clicks the first domain card. It never exercises the
other 4 library domains, so a nav defect in godot-gamedev / ink-godot / oidc-rust /
workout-fundamentals (e.g. the #273 nested-page breadcrumb bug) would not be caught by the
browser suite. #273 added a static `verify-links` guard + a targeted browser click-through,
but the general suite still only sees iceberg.

## What to build

- Parameterize `test-navigation.py` to iterate the served domains — discover them from the
  aggregate `index.html` `page-data` island (the `domains[].mapHref` list) rather than
  hardcoding slugs.
- For each domain: run the core journey (index card → map → a lesson → its quiz → back-nav),
  plus a breadcrumb click-through on any page nested below `lessons/` (from #273: click both
  "All Lessons" and the map crumb, assert real navigation).
- Keep screenshots per domain for review; report pass/fail per domain, not just globally.
- Runs via the `browser` specialist agent against a running server (Playwright not in default agent).
- **Index cue states (#271, added 2026-08-30):** assert the orientation cue on an all-zero
  (empty-state) index and the resume cue ("Continue where you left off → {domain}") on a
  partially-complete / in-progress domain, including the all-complete case (no resume). #271
  got only a one-off subagent browser check + a `verify-interactive` smoke assertion
  (`index_cue_present` = exactly one cue); this suite is the durable home for the full
  empty/resume/all-complete matrix and the resume-link click destination.

## Acceptance criteria

- [ ] Domains discovered dynamically from the aggregate index page-data (no hardcoded slugs)
- [ ] Core journey runs per domain; failures attributed to the specific domain
- [ ] Nested-page breadcrumb click-through covered for every `lessons/{sub}/` page
- [ ] Index cue matrix covered: empty→orientation, in-progress/partial→resume (+ click dest), all-complete→no resume (#271)
- [ ] Suite runnable headless via the browser agent; screenshots captured per domain
- [ ] Documented in the visual-qa / serve-workspace skill so it's discoverable
