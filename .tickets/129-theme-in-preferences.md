---
id: "129"
title: "Feature: Theme toggle (dark/light/auto) integrated into preferences panel"
status: open
blocked_by: ["126"]
priority: high
---

# Feature: Theme toggle (dark/light/auto) in preferences panel

## Problem

Users cannot switch between dark and light mode. The CSS supports both themes (`:root` dark vars + `[data-theme="light"]` + `@media (prefers-color-scheme: light)`), but:

- `theme-toggle.js` exists but NO page loads it (confirmed via Playwright — `.theme-toggle` element doesn't exist)
- `store.js` has a `toggleTheme()` function and `theme` signal — nothing calls them
- The `@media (prefers-color-scheme: light)` rule auto-applies for system-light users, but there's no manual override

This is a half-migrated feature: ADR 0005 deprecated the vanilla JS approach but no Preact replacement was built.

## Solution

Add a "Theme" row to the preferences panel (part of the unified preferences module from ticket 126):

```
THEME
[Dark]  [Light]  [Auto]
```

- **Dark** — `data-theme="dark"` forced on `<html>`, ignores system
- **Light** — `data-theme="light"` forced on `<html>`, ignores system
- **Auto** — remove `data-theme`, let `@media (prefers-color-scheme)` decide

The blocking head script resolves `auto` using `matchMedia('(prefers-color-scheme: light)')` and applies the correct `data-theme` before first paint — no flash.

## CSS Integration

Current CSS already handles both themes:
```css
:root { /* dark mode vars */ }
[data-theme="light"] { /* light mode vars */ }
@media (prefers-color-scheme: light) { :root:not([data-theme="dark"]) { /* light vars */ } }
```

The `auto` mode works by NOT setting `data-theme` at all — the media query fires naturally. For the blocking script, we temporarily set `data-theme` to the resolved value (prevents flash), then the component can manage it reactively.

## Cleanup

After this ticket:
- DELETE `assets/theme-toggle.js` (orphaned, never loaded)
- REMOVE `theme` signal and `toggleTheme()` from `assets/components/store.js`
- Theme is owned entirely by the preferences module

## Key Context

- The `prefers-color-scheme: light` media query was added this session — it works for auto-detection
- The `[data-theme="light"]` selector has been in style.css since the beginning
- SVG diagrams use CSS variables that resolve differently per theme — theme switching is safe
- All SVG text now uses `var(--svg-text)` or `var(--svg-*-text)` — no hardcoded colors to break
- Research: `.scratch/research/arch-preferences.md` (preference cascade: stored → system → default)

## Sources

- [web.dev: Building a color scheme](https://web.dev/articles/building-a-color-scheme) — dark/light/auto pattern
- [web.dev: color-scheme meta](https://web.dev/articles/color-scheme) — `<meta name="color-scheme">`
- [MDN: prefers-color-scheme](https://developer.mozilla.org/en-US/docs/Web/CSS/@media/prefers-color-scheme) — media query reference
- Current style.css lines 1-80 (dark vars) and 42-80 (light vars + media query)

## Acceptance criteria

- [ ] Theme row in preferences panel with Dark / Light / Auto buttons
- [ ] Dark mode: dark background, light text, dark SVG fills
- [ ] Light mode: light background, dark text, light SVG fills
- [ ] Auto mode: follows system preference (respects OS dark/light setting)
- [ ] No flash on page load (blocking script resolves theme before paint)
- [ ] Preference persists across sessions (part of unified prefs key)
- [ ] `theme-toggle.js` deleted from repository
- [ ] `store.js` theme signal/toggleTheme removed

## Validation

- [ ] Playwright (dark): emulateMedia dark → page has dark background
- [ ] Playwright (light): set theme=light in localStorage, reload → light background
- [ ] Playwright (auto): no stored theme + emulateMedia light → light background
- [ ] Playwright: toggle Dark→Light→Auto via panel, verify background changes each time
- [ ] `mise run verify` passes
- [ ] `git log --diff-filter=D -- assets/theme-toggle.js` shows deletion
