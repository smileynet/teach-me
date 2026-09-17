---
id: "371"
title: "Served-host console noise: nested-index api/overlay 404 + orphan Mark-complete on quiz/review pages"
status: open
blocked_by: []
tags: ["ux", "server", "components"]
---

# Served-host console noise: nested-index api/overlay 404 + orphan Mark-complete on quiz/review pages

## Intent

Shipped pages should not log 404s or offer actions that cannot succeed.

## Context (found 2026-09-17 during the #368/#369/#370 Playwright walkthrough)

Two pre-existing warts, both graceful-but-noisy, observed serving `library/`:

1. **Per-domain index pages probe a relative `api/overlay`** — the
   `_INDEX_MODULE_SCRIPT` in `tools/generate_index_page.py` fetches `api/overlay`
   relative to the page URL, so `/{domain}/lessons/index.html` hits
   `/{domain}/lessons/api/overlay` → 404 (console error). The catch swallows it and the
   demo floor stands, so behavior is correct — but every nested index visit logs a 404
   on served hosts. The aggregate `/index.html` resolves fine. Fix sketch: bake the
   root-relative-to-workspace prefix into the module script at generate time (pages
   stay document-relative per AGENTS.md — never `/api/...`).
2. **Quiz and quick-check pages render a Mark-complete button with no domain** — these
   pages have no `lesson-actions-config` island, so `LessonActions` falls back to
   `domain=null`; status renders `idle` and clicking Mark complete POSTs to
   `/api/map/null/...` and surfaces "Could not save". Post-#370 the bar on these pages
   is ONLY this orphaned button. Fix sketch: don't mount the action bar at all when no
   config island exists (the template knows the page type), or suppress the completion
   button when `domain` is null.

## Acceptance criteria

- [ ] Per-domain index pages produce no `api/overlay` 404 on served hosts AND still
      resolve the user's overlay when one exists
- [ ] Quiz/review pages show no completion control that cannot persist
- [ ] `mise run verify` exits 0; interactive checks stay green
