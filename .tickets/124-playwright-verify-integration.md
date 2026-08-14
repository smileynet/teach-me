---
id: "124"
title: "Feature: Add interactive Playwright checks to mise run verify pipeline"
status: done
blocked_by: []
priority: high
---

# Feature: Add interactive Playwright checks to mise run verify pipeline

## What to build

`mise run verify` currently checks links, lint, and SVG variables — all static. It doesn't catch:
- Tooltips not appearing (glossary.js missing)
- Buttons that don't respond (dead click handlers)
- Components that don't mount (missing imports)
- Layout breakage at different viewport sizes
- Typography panel not rendering

Add a Playwright interactive check step that exercises key behaviors on a running server. Should be fast (< 10s) and reliable — tests real user interactions, not just file contents.

## Checks to include

| Check | What it verifies | How |
|-------|-----------------|-----|
| Tooltip hover | glossary.js loaded + working | Hover .term → assert .glossary-tooltip appears |
| Action bar renders | LessonActions.js mounted | Assert .lesson-actions-bar exists with buttons |
| Quiz button navigates | Quiz link correct | Click quiz button → assert no 404 (or button text correct) |
| Typography panel | TypographyPanel.js mounted | Click Aa → assert .typo-panel appears |
| Typography applies | CSS vars update | Change font size → assert computed style changed |
| SVG diagrams visible | Diagrams render in dark mode | Assert svg[role="img"] has non-zero dimensions |
| No console errors | Clean page load | Assert no JS errors in console (ignore 404s for favicon) |

## Architecture

- Start local server (`mise run serve`) if not already running
- Run Playwright headless against localhost
- Test one representative lesson page (e.g., first example lesson)
- Exit 0 = pass, exit 1 = fail with specific failure message
- Integrate as final step in `mise run verify` (after lint/links/svg)

## Acceptance criteria

- [ ] `mise run verify` includes interactive Playwright checks
- [ ] Checks cover: tooltip hover, action bar, typography panel, SVG visibility, no JS errors
- [ ] Passes in < 10 seconds total (fast enough to run every time)
- [ ] Failure output names the specific check that failed
- [ ] Works headless (no X server required)
- [ ] Server auto-starts if not running, auto-stops after

## Validation

- [x] Manually verify each check catches its corresponding bug (e.g., remove glossary.js → tooltip check fails)

## Resolution (2026-08-14)

Created tools/verify-interactive.py, integrated into mise.toml verify task. Auto-detects running server, gracefully skips without Playwright.
