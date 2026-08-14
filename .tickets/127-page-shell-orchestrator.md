---
id: "127"
title: "Refactor: Page shell orchestrator — single entry point replaces self-mounting components"
status: open
blocked_by: ["126"]
priority: high
---

# Refactor: Page shell orchestrator

## Problem

Each Preact component self-mounts independently:

| Component | Mount strategy | Creates own mount point? |
|-----------|---------------|--------------------------|
| `GlossaryQuiz.js` | DOMContentLoaded → querySelectorAll | No (annotates existing elements) |
| `LessonActions.js` | DOMContentLoaded → getElementById or createElement | Yes |
| `TypographyPanel.js` | DOMContentLoaded → getElementById or createElement | Yes |
| `LayoutMode.js` | DOMContentLoaded → querySelectorAll h2 | No (restructures existing DOM) |
| `glossary.js` | DOMContentLoaded → querySelectorAll .term | No (attaches event listeners) |

This causes:
- **Race conditions**: LayoutMode restructures DOM that glossary.js is attaching listeners to
- **Fragile mounting**: each component independently decides when/where to mount
- **N imports per page**: adding a component = editing every lesson HTML to add `import` line
- **No initialization order**: components compete for DOMContentLoaded

Real bug caused by this: LayoutMode's "restore Flow" innerHTML replacement killed all other components' mount points (required re-importing everything).

## Solution

One `assets/page-shell.js` module that lesson pages load:

```javascript
// page-shell.js — THE single entry point for all lesson page behavior
import { prefs, effectiveTheme } from './preferences.js';
import { initGlossary } from './components/GlossaryQuiz.js';
import { mountLessonActions } from './components/LessonActions.js';
import { mountTypographyPanel } from './components/TypographyPanel.js';
import { applyLayout } from './components/LayoutMode.js';

// Initialization order matters:
// 1. Preferences already loaded (signals populated from localStorage)
// 2. Layout restructuring (must happen before glossary attaches to .term elements)
// 3. Glossary (annotates terms, attaches hover/click listeners)
// 4. LessonActions (bottom bar — mount point)
// 5. TypographyPanel (fixed position — mount point)

function init() {
  applyLayout(prefs.value.sectionsCollapsed);
  initGlossary();
  mountLessonActions();
  mountTypographyPanel();
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', init);
} else {
  init();
}
```

**Lesson HTML becomes:**
```html
<script type="module" src="../assets/page-shell.js"></script>
```

ONE import. No per-component imports. No self-mounting logic in components.

## Component Changes

Each component loses its auto-mount IIFE and exports a pure function instead:

- `GlossaryQuiz.js`: remove auto-init block, export `initGlossary()`
- `LessonActions.js`: remove `mount()` + DOMContentLoaded listener, export `mountLessonActions()`
- `TypographyPanel.js`: remove `mount()` + DOMContentLoaded listener, export `mountTypographyPanel()`
- `LayoutMode.js`: remove `init()` + DOMContentLoaded listener, export `applyLayout(collapsed)`
- `glossary.js`: absorbed into page-shell (or kept as non-module for legacy pages, loaded by shell)

## Key Context

- ADR 0005: Preact components adopted — this refactor completes the migration from autonomous scripts to orchestrated components
- Islands architecture research: Fresh/Astro use this exact pattern (orchestrator discovers + mounts)
- `glossary.js` is a non-module IIFE — must either be converted to ESM export or loaded by shell via dynamic script injection
- Blocked by ticket 126 (preferences module) because shell imports preferences
- Research: `.scratch/research/arch-page-shell.md` (417 lines, orchestrator patterns from Fresh/Astro/11ty)

## Sources

- [Fresh Islands Architecture](https://fresh.deno.dev/docs/concepts/islands) — orchestrator discovers `data-island` markers
- [Preact blog: Islands Architecture](https://preactjs.com/blog/islands/) — partial hydration with shared state
- [patterns.dev Islands Architecture](https://www.patterns.dev/posts/islands-architecture) — independent islands with shared signals
- [Inclusive Components: Collapsible Sections](https://inclusive-components.design/collapsible-sections/) — PE pattern for DOM manipulation

## Acceptance criteria

- [ ] Single `page-shell.js` is the only module import in lesson HTML
- [ ] Components export mount/init functions (no self-mounting logic)
- [ ] Initialization order is explicit and documented in page-shell.js
- [ ] Adding a new component = register in page-shell.js, zero HTML file changes
- [ ] Removing `glossary.js` non-module script from lessons (functionality in shell)
- [ ] Layout changes don't break other components (shell re-initializes after restructuring)
- [ ] All existing functionality preserved (tooltips, action bar, typography, sections)

## Validation

- [ ] `mise run verify` passes (all 7 interactive checks + 37 static)
- [ ] Playwright: tooltips work after switching sections collapsed→expanded
- [ ] Playwright: all components mount correctly on fresh page load
- [ ] Lesson HTML files contain exactly ONE `<script type="module">` tag (the shell)
- [ ] No `import '../assets/components/...'` in lesson HTML files
