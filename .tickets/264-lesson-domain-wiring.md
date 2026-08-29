---
id: "264"
title: "Lesson mark-complete POSTs to /api/map/null/ — data-domain never wired into lesson pages"
status: open
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

- [ ] Generated lesson pages carry the domain (via `data-domain` or equivalent) so
      LessonActions builds `/api/map/{real-domain}/{slug}/status`
- [ ] Clicking mark-complete on a served example lesson fires `POST` to the real-domain URL
      and returns 200 `{ok:true}` (Playwright round-trip)
- [ ] Mount-time `GET .../status` fires and seeds the button from the overlay
- [ ] The button does NOT show "Complete" if the POST fails (revert optimistic update)
- [ ] `mise run verify` EXIT 0 (verify-interactive still green)

## Validation

Serve an example workspace (`python tools/serve-bg.py --workspace examples/oidc-rust`),
Playwright-load a lesson, click mark-complete → confirm POST hits the real domain, returns
200, overlay file updates, and the button reflects persisted state (reload → still complete).
