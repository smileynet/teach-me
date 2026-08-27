---
id: "232"
title: "verify-interactive.py flaky no_js_errors failure on a 404 resource"
type: bug
status: open
priority: high
blocked_by: []
tags: ["validation", "flaky"]
---

# verify-interactive.py flaky no_js_errors failure on a 404 resource

## Symptom

`mise run verify` (and `uv run python tools/verify-interactive.py`) intermittently
fails the `no_js_errors` check with:

```
✗ no_js_errors: JS errors: ['Failed to load resource: the server responded with a status of 404 (Not Found)']
```

**Intermittent, not deterministic.** Observed 2026-08-27: 1 failure, then 4
consecutive clean runs ("Clean console"). Classic timing/race flake — a resource
that loads inconsistently depending on server-ready timing or lazy load order.

## Impact

Blocks `mise run verify` from passing reliably. Because verify runs steps
sequentially, a failure here also prevents later steps (including the new ink
transcript replay from #228) from running in the same invocation. This is NOT
caused by #228 — the ink transcript step passes standalone under `uv run`.

## What to investigate

1. Which resource 404s? verify-interactive.py captures console errors but doesn't
   log the failing URL. Add the URL to the error message first (cheap, unblocks
   diagnosis).
2. Is it a server-not-ready race (Playwright navigates before the local server
   binds)? Check the serve/wait logic in verify-interactive.py.
3. Is it a lazy-loaded asset (font, icon, vendor chunk) with a wrong/relative path
   that only fires on some page states?
4. Likely related: this file has uncommitted pre-existing changes (see #233) that
   converted verify to `uv run` + added `smoke-draw-diagram.py`. Confirm whether
   the flake predates or was introduced by those changes.
## Cross-session update (2026-08-27, from the #229/#230 session)

**The 404 is NOT a race — it was a deterministic quiz-path mismatch, now fixed.**

Root cause (identified + fixed while resolving #229/#230): the `01-texture-audit` lesson's action bar derives its quiz URL as `quiz/{id}-quiz.html` relative to the lesson (`LessonActions.js:24`) → `lessons/blender-texture-prep/quiz/01-texture-audit-quiz.html`, but the quiz had been generated in the flat `lessons/quiz/` dir. So the quiz nav link 404'd every time the test page was that lesson.

- Traced with a Playwright request-capture: the failing URL was exactly `.../blender-texture-prep/quiz/01-texture-audit-quiz.html` (not a font/favicon/vendor chunk).
- The "intermittent" appearance was `find_test_page` sometimes selecting a *different* page (before the godot-gamedev candidates were added) — not a load-timing race.
- **Fixed:** quiz relocated to the subfolder + made depth-aware (#230, closed). `mise run verify` now shows `no_js_errors: Clean console` and `quiz_button_navigation: exists (200)`, 8/8 interactive, across repeated runs.

Suggest closing #232 as resolved-by-#230 once confirmed on your end — the "add the 404 URL to the error message" AC is still a reasonable cheap improvement to keep (it's what made this diagnosable), but the flake itself is gone.

## Acceptance criteria

- [ ] Failing 404 URL is logged in the error message
- [ ] Root cause identified (race vs bad path vs lazy asset)
- [ ] Fix applied (wait-for-ready, correct path, or ignore-list with justification)
- [ ] `verify-interactive.py` passes 5 consecutive runs
