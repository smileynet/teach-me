---
id: "116"
title: "Feature: Customizable fonts and text size"
status: done
blocked_by: []
tags: [platform]
---

# Feature: Customizable fonts and text size

## Research Summary

Research covered WCAG standards, e-reader prior art (Kindle/Kobo/Apple Books), open-source readers (Readium), and implementation patterns. Full findings in `.scratch/research/116-*.md`.

**Key insights:**
- Font size is the #1 most-adjusted setting (used by 85%+ of e-reader users who change any setting)
- Converged UI pattern: "Aa" icon → floating panel → live preview → persist via localStorage
- WCAG 1.4.4 requires 200% resize without breakage; 1.4.12 requires tolerating user spacing overrides
- FOUC prevention requires a synchronous inline `<script>` in `<head>` before CSS loads
- System font stacks preferred (zero download); only OpenDyslexic needs self-hosting (~60KB)
- Reading speed varies 35% between best/worst font per individual — one-size-fits-all is measurably suboptimal

## What to build

A typography preferences panel accessible from any lesson page. Uses CSS custom properties for dynamic values, localStorage for persistence, and a blocking head script to prevent flash of default styles.

### Controls (ordered by usage frequency)

| Control | Options | Default |
|---------|---------|---------|
| Font size | 5 steps: S (14px), M (16px), L (18px), XL (20px), XXL (22px) | M (16px) |
| Font family | Serif (Palatino), Sans (system-ui), Dyslexia-friendly (OpenDyslexic) | Serif |
| Line spacing | Compact (1.5), Default (1.7), Relaxed (2.0) | Default |
| Content width | Narrow (600px), Default (740px), Wide (900px) | Default |

### Architecture

1. **CSS variables** on `:root` — `--font-size-base`, `--font-family-body`, `--line-height-body`, `--max-width-content`
2. **Blocking head script** — inline `<script>` reads localStorage before first paint, applies vars
3. **Preact component** — `TypographyPanel.js` renders the "Aa" trigger + floating panel
4. **Scoping rules:**
   - Body text: fully user-controlled
   - Headings: scale proportionally from base (calc multipliers)
   - Code blocks: always monospace, size scales proportionally
   - SVG diagrams: unaffected (own sizing)
   - UI chrome (nav, buttons): unaffected

### UI Pattern

- Trigger: "Aa" button fixed in top-right (next to theme toggle position)
- Panel: floating dropdown below trigger, 250px wide
- Controls: segmented buttons for discrete options (not sliders)
- Live preview: changes apply immediately as user clicks
- Dismiss: click outside or press Escape

## Acceptance criteria

- [x] "Aa" button visible on all lesson pages (fixed position, top-right area)
- [x] Panel shows font size, font family, line spacing, and content width controls
- [x] Changes apply immediately without page reload
- [x] Preferences persist across page loads and sessions (localStorage)
- [x] No FOUC — preferences applied before first paint via blocking head script
- [x] Doesn't break layout, diagrams, or code blocks at any setting combination
- [x] WCAG compliant: supports 200% browser zoom on top of largest font setting without overflow
- [x] Works on mobile (touch targets ≥ 44px, panel responsive)
- [x] OpenDyslexic font self-hosted in assets/vendor/ (no external requests)
- [x] Blocking script weighs < 1KB (inline, no network request)

## Implementation Plan

1. Add CSS custom properties for typography to `assets/style.css` (replace hardcoded values)
2. Create `assets/typography-prefs.js` — inline blocking script (~500 bytes)
3. Create `assets/components/TypographyPanel.js` — Preact component
4. Self-host OpenDyslexic WOFF2 in `assets/vendor/`
5. Add "Aa" mount point to lesson scaffold
6. Update existing lessons to include the head script

## Prior Art References

- Kindle: "Aa" icon, tabbed panel (Font/Layout), 14 size steps, 13 font families
- Readium: CSS custom properties architecture, Preferences API
- Apple Books: named themes, A+/A- buttons, slider for spacing
- Research: < 15% of users keep publisher defaults (Readium data)

## Validation

- [x] Aa button visible on lesson page (fixed top-right)
- [x] Clicking Aa opens panel with Size, Font, Spacing, Width controls
- [x] Changing font size applies immediately (verified: 16px → 20px)
- [x] Changing font family applies immediately (serif → sans → dyslexic)
- [x] Preferences persist after page reload (localStorage)
- [x] No layout breakage at any combination (including XXL + Dyslexic + Wide)
- [x] mise run verify passes

## Resolution (2026-08-14)

Typography panel: CSS vars, blocking head script, Preact component, OpenDyslexic. All 29 lessons updated.
