---
id: "126"
title: "Refactor: Unified preferences module — consolidate theme, typography, layout into one deep module"
status: open
blocked_by: []
priority: high
---

# Refactor: Unified preferences module

## Problem

User preferences are scattered across 5 files with 2 localStorage keys and 2 reactivity mechanisms:

| File | Owns | Storage | Reactivity |
|------|------|---------|-----------|
| `assets/typography-prefs.js` | font size, family, line-height, width | `teach-me-typography` | None (blocking IIFE) |
| `assets/components/TypographyPanel.js` | Same + layout | `teach-me-typography` | useState |
| `assets/components/LayoutMode.js` | layout (sections) | reads `teach-me-typography` | Custom event |
| `assets/components/store.js` | theme signal | None (reads DOM attr) | Preact signal |
| `assets/theme-toggle.js` | theme toggle | `teach-me-theme` | None (IIFE, orphaned) |

Adding a new preference requires touching a blocking script, a component, and potentially a store. No locality.

## Solution

One `assets/preferences.js` module:

```javascript
// preferences.js — THE source of truth for all user preferences
import { signal, effect, computed } from '@preact/signals';

const STORAGE_KEY = 'teach-me-prefs-v1';
const DEFAULTS = {
  theme: 'auto',        // 'auto' | 'light' | 'dark'
  fontSize: '16px',
  fontFamily: 'serif',  // 'serif' | 'sans' | 'dyslexic'
  lineHeight: '1.7',
  maxWidth: '740px',
  sectionsCollapsed: false,
};

// Exported signals — components import directly, no prop drilling
export const prefs = signal(load());
export const effectiveTheme = computed(() => {
  if (prefs.value.theme !== 'auto') return prefs.value.theme;
  return matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark';
});

// Auto-persist + auto-apply CSS vars
effect(() => { save(prefs.value); applyToDOM(prefs.value); });

export function set(key, value) { prefs.value = { ...prefs.value, [key]: value }; }
export function reset() { prefs.value = { ...DEFAULTS }; }
```

One blocking head snippet (~200 bytes inline in template):
```javascript
// Inlined in <head> before CSS — prevents FOUC
(function(){try{var p=JSON.parse(localStorage.getItem('teach-me-prefs-v1'));
if(!p)return;var s=document.documentElement.style;var d=document.documentElement;
if(p.fontSize)s.setProperty('--font-size-base',p.fontSize);
if(p.fontFamily)s.setProperty('--font-family-body',p.fontFamily);
if(p.lineHeight)s.setProperty('--line-height-body',p.lineHeight);
if(p.maxWidth)s.setProperty('--max-width-content',p.maxWidth);
var t=p.theme==='auto'?(matchMedia('(prefers-color-scheme:light)').matches?'light':'dark'):p.theme;
d.setAttribute('data-theme',t);}catch(e){}})();
```

## Migration

1. On first load, check for legacy keys (`teach-me-typography`, `teach-me-theme`)
2. Merge into new schema under `teach-me-prefs-v1`
3. Delete legacy keys
4. `_migrated: true` flag prevents re-running

## Key Context

- ADR 0005: Preact + Signals adopted — signals are the project's reactivity model
- `TypographyPanel.js` currently uses `useState` (local) not signals (global) — this refactor aligns it
- `theme-toggle.js` is orphaned (no page loads it) — delete after this ticket
- `store.js` has `theme` signal + `toggleTheme()` but nothing calls them from lesson pages
- Research: `.scratch/research/arch-preferences.md` (408 lines, full cascade/schema/migration patterns)

## Sources

- [Preact Signals docs](https://preactjs.com/guide/v10/signals/) — effect() for auto-persistence
- [developit's persistedSignal gist](https://gist.github.com/developit) — signal + localStorage pattern
- [CodeFronts anti-FOUC](https://codefronts.com/) — inline head script pattern
- [web.dev color-scheme](https://web.dev/articles/color-scheme) — meta color-scheme + auto resolution

## Acceptance criteria

- [ ] Single `preferences.js` module exports signals for all preferences
- [ ] Single localStorage key (`teach-me-prefs-v1`) replaces both legacy keys
- [ ] Legacy key migration works (old preferences preserved on first load)
- [ ] One blocking head snippet (< 300 bytes) handles all pre-paint application
- [ ] `TypographyPanel.js` reads/writes from signals (no local useState for prefs)
- [ ] `LayoutMode.js` reads from signals (no independent localStorage read)
- [ ] `theme-toggle.js` deleted (functionality moved to panel)
- [ ] `store.js` theme signal removed (consolidated into preferences.js)
- [ ] Adding a new preference = add to DEFAULTS + add UI row. No other files touched.

## Validation

- [ ] Playwright: change theme → persists on reload
- [ ] Playwright: change font size → persists on reload
- [ ] Playwright: open in fresh incognito → defaults applied, no errors
- [ ] Playwright: set preferences in old format → migration runs, new format used after
- [ ] `mise run verify` passes (all 7 interactive + 37 static checks)
- [ ] No FOUC visible on page load with any preference combination
