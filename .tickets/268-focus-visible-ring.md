---
id: "268"
title: "a11y: add high-contrast :focus-visible ring (UA default near-invisible on dark)"
status: done
blocked_by: []
priority: high
tags: ["platform"]
---

# a11y: high-contrast focus ring

## Why (found in UX audit, 2026-08-29)

Every interactive element (index/global-map domain cards, map node buttons, lesson action
bar, links, glossary terms) falls back to the UA-default focus outline
(`rgb(16,16,16) auto 1px`) — near-invisible on the dark theme background. Keyboard users
can't see where focus is. Fails WCAG 2.4.11 (Focus Appearance) + the project's own a11y
guidance. Confirmed on all four page types via Playwright (.scratch/ux/shots/).

## What to build

- Add a global `:focus-visible` rule in `assets/style.css` using a token: ring ≥2px, ≥3:1
  contrast vs adjacent (WCAG 2.4.11). Use an existing accent/focus custom property; add a
  `--focus-ring` token if none fits. Applies in BOTH themes (define value per theme).
- Ensure `.btn`, `.topic-card`/`.domain-card` links, breadcrumb links, and `.term` (if
  focusable) all pick it up. Never `outline: none` without a replacement.

## Acceptance criteria

- [x] `:focus-visible` ring visible on buttons, card links, breadcrumb links in dark AND light
- [x] Ring ≥2px and ≥3:1 contrast against adjacent background (WCAG 2.4.11)
- [x] No `outline: none` left without a visible replacement
- [x] `mise run verify` EXIT 0 (verify-interactive still green)

## Validation

Playwright: tab through index, global-map, a domain map, a lesson; confirm a visible focus
ring on each interactive element in both themes.

## Resolution (2026-08-30)

style.css: --focus-ring token per theme + global :focus-visible (a/button/[tabindex]/summary) 2px solid var(--focus-ring), offset 2px. Keyboard-only (no ring on mouse). Applies to all page types (all link style.css via _base_page).
