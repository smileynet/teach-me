---
id: "264"
title: "Lesson mark-complete POSTs to /api/map/null/ — data-domain never wired into lesson pages"
status: done
blocked_by: []
tags: ["platform"]
---

# Lesson mark-complete POSTs to /api/map/null/ — data-domain never wired into lesson pages

## Why (found during #258 Playwright validation)

The lesson "✓ Mark complete" button (LessonActions.js) builds its status API URL as
`/api/map/{domain}/{slug}/status`, but `domain` resolves to `null` on every example
lesson page. Result: the POST goes to `/api/map/null/oidc-auth-flows/status` → HTTP 404
`{"detail":"No MAP.md found for domain 'null'"}`. The button still *optimistically*
flips to "✓ Complete", so the UI lies — nothing persisted.

Pre-existing (NOT caused by #258 — that changed only the endpoint's backing store, which
curl-validates green with an explicit domain). `LessonActions.js` domain resolution dates
to commit 6b76473 (2026-08-14); `page_template.py` never emitted `data-domain`.

## Root cause (verified)

`mountLessonActions()` (assets/components/LessonActions.js ~L79-95) reads the domain from
`document.querySelector('script[data-domain]')` or `#lesson-actions[data-domain]`:
```js
domain: source.dataset.domain || null,
```
No lesson page carries `data-domain` (grep: 0 of all `examples/*/lessons/*.html`), and
`tools/lib/page_template.py` doesn't emit it. So `domain` is always `null`. The mount-time
`GET .../status` is also skipped (LessonActions early-returns when `!domain`).

## Findings (research + review, 2026-08-29)

Evidence: `.scratch/review/lesson-gen-surface.md`, `.scratch/review/lessonactions-mount.md`,
`.scratch/research/optimistic-ui.md`, `.scratch/research/config-island-vs-attr.md`.

- **Scope is ALL 30 example lesson pages, uniform** (not "4+"). Every lesson loads the bar
  via `page-shell.js` → `mountLessonActions()`; NONE carry domain config, so mark-complete
  is uniformly broken. Full list in the review. No special hand-built subset.
- **Use data-* attributes, NOT a JSON island.** Config research: flat 3-scalar payload →
  data-* (no parse, colocated, auto HTML-escaping). Decisive: `mountLessonActions` ALREADY
  queries `script[data-domain]` — emitting a `<script data-domain data-lesson-id
  data-map-page data-topic-title>` needs ZERO LessonActions mount change. Less code than an
  island.
- **`render_lesson_page` has domain_slug/lesson_id/title in scope** (params L145-146); emit
  the config script through `_base_page` (escaped via `_esc`). No code caller exists — it's
  an agent-invoked library, so existing example pages must be BACKFILLED (bodies live only in
  the committed HTML; regeneration impossible). Precedent: `tools/migrate-add-breadcrumbs.py`
  (idempotent regex inject). Backfill MUST read each page's OWN breadcrumb `*-map.html` href
  for domain_slug (godot-gamedev has 4 maps — do NOT hardcode per workspace).
- **Optimistic-UI fix** (LessonActions.js `handleToggleComplete` L42-53): the bug is both
  `.then` (no `res.ok` check — fetch resolves on 4xx/5xx) AND `.catch` set the target status.
  Fix: snapshot priorStatus → `setStatus('saving')` → `.then`: `if(!res.ok) throw` else set →
  `.catch`: revert to priorStatus + `setError(...)`. Add `const [error,setError]=useState(null)`.
  NO new 'error' status branch (keep enum one-axis: loading/idle/complete/saving); surface
  error as `title=` + an `aria-live="polite" role="status"` span (accessibility research).
- **#199 coordination:** #199 flagged `lesson_id` as a dead param to delete — this gives it a
  real use; do NOT delete it.

## What to build

- **Emit `data-domain` (and `data-lesson-id`, `data-map-page`) into every generated lesson
  page.** `page_template.py` (or the page-shell bootstrap) should write a
  `<script data-domain="{domain}" data-lesson-id="{slug}" data-map-page="{domain}-map.html">`
  (or set those attrs on `#lesson-actions`). The domain is known at generate time (it's the
  MAP.md domain the lesson belongs to).
- **Backfill the 4 example lesson pages** that ship with a mark-complete button (or
  regenerate them).
- **Don't apply the optimistic DOM "Complete" state until the POST returns 200** — on
  failure, revert + surface the error (no silent-lie button; AGENTS.md "no silent buttons").

## Acceptance criteria

- [x] `render_lesson_page` emits a `<script data-domain data-lesson-id data-map-page
      data-topic-title>` so LessonActions builds `/api/map/{real-domain}/{slug}/status`
- [x] All 34 committed example lesson pages backfilled with the config (idempotent — re-run
      0 updated/34 skipped; domain_slug read from each page's own breadcrumb `*-map.html`:
      0004→godot-toon-shaders, 0001→godot-gamedev, blender/→blender-texture-prep)
- [x] Clicking mark-complete on a served example lesson fires `POST` to the real-domain URL
      and returns 200 `{ok:true}` (Playwright: POST /api/map/oidc-rust/... → 200)
- [x] Mount-time `GET .../status` fires and seeds the button from the overlay (Playwright:
      GET /api/map/oidc-rust/oidc-auth-flows/status → 200; reload persists 'complete')
- [x] The button does NOT show "Complete" if the POST fails — reverts to prior status +
      shows an `aria-live` error (Playwright failure-path: 500 → reverted + "Could not save")
- [x] `mise run verify` EXIT 0 (verify-interactive 8/8 green; fixed a brittle
      `button:first-child` quiz selector exposed by the now-rendering map link)

## Validation

Serve an example workspace (`python tools/serve-bg.py --workspace examples/oidc-rust`),
Playwright-load a lesson, click mark-complete → confirm POST hits the real domain, returns
200, overlay file updates, and the button reflects persisted state (reload → still complete).

## Resolution (2026-08-29)

render_lesson_page emits a data-* config script (domain/lesson-id/map-page/topic-title) before page-shell.js via a _base_page lesson_actions param; LessonActions' existing script[data-domain] query consumes it (no mount change). Backfilled all 34 committed example lessons with tools/migrate-add-lesson-actions.py (idempotent; domain slug from each page's own breadcrumb *-map.html — handles godot's 4 maps). Fixed the silent-lie: handleToggleComplete snapshots prior status, checks res.ok, reverts + shows an aria-live error on failure; no new status branch. Fixed a positional quiz-button selector in verify-interactive exposed by the now-rendering map link. Note: #199 must NOT delete lesson_id (now used for the config script).
