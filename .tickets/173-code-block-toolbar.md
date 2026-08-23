---
id: "173"
title: "CodeBlockToolbar component: copy + download + filename label"
status: done
blocked_by: []
priority: high
---

# CodeBlockToolbar component: copy + download + filename label

## Context

Tickets #162 (copy button) and #168 (code extraction + download) both target code blocks and would both mount interactive UI into `<pre data-file>` elements. Rather than building two separate systems, they should converge into a single `CodeBlockToolbar` component.

Research (2026-08-19) confirmed:
- Storybook is **not** justified for ~15 components with a zero-build stack
- The right pattern is **progressive enhancement**: CSS handles filename labels automatically via `pre[data-file]::before`, JS adds interactive copy/download buttons
- A **component showcase page** (not Storybook) serves design review needs

## What to build

### 1. CSS layer (zero JS, immediate visual consistency)

Add to `style.css`:
```css
pre[data-file] { position: relative; padding-top: 2.5rem; }
pre[data-file]::before {
  content: attr(data-file);
  position: absolute; top: 0; left: 0; right: 0;
  font-size: 0.75rem; color: var(--text-muted);
  padding: 0.4rem 1rem; border-bottom: 1px solid var(--border);
  font-family: var(--font-family-code);
}
pre[data-mode="diff"] { border-left-color: var(--warning); }
pre[data-mode="fragment"] { border-left-style: dashed; opacity: 0.85; }
```

### 2. JS component (progressive enhancement)

`assets/components/CodeBlockToolbar.js`:
- Queries all `pre[data-file]` elements
- Mounts a small Preact toolbar (copy + download) into each
- Copy uses Clipboard API, shows "Copied!" feedback via shared signal (one at a time)
- Download links to extracted file (HEAD check for existence, hide if absent)
- Strips diff spans on copy (gives clean code, not markup)

Mounted by page-shell.js via `initCodeBlockToolbar()` — same pattern as `initGlossary()`.

### 3. Component showcase page

`assets/showcase.html` — renders every component in meaningful states:
- CodeBlockToolbar: complete, diff, fragment, with/without download
- LessonActions: with quiz, without quiz, complete state
- TypographyPanel: open, closed, each setting
- GlossaryQuiz: tooltip hover, tray open
- Progressive reveal: step 1, step 3, final

Serves as the "design review" page — human browses it, AI can read the source, Playwright can snapshot it.

## Component Abstraction Strategy

### Decision framework (from research):

```
Does it need JavaScript to function?
├─ No → CSS class/attribute selector (Level 0-2)
│       e.g., .key-concept, .note, pre[data-file]::before
└─ Yes → Does it work (degraded) without JS?
    ├─ Yes → Progressive enhancement (Level 3-4)
    │       e.g., CodeBlockToolbar, Glossary tooltips, Collapsible sections
    └─ No → Full component (Level 5)
            e.g., QuizView, MapView, GenerationStream
```

### Bright lines:

**Always a component** (Level 4-5):
- Has keyboard navigation requirements
- Manages internal state across interactions
- Consumes external services (API, SSE)
- Has 3+ interactive variants that share logic

**Never a component** (Level 0-2):
- Pure visual styling (colors, spacing, borders)
- Static layout patterns
- Content that reads correctly without JS

**Rule of three for the gray zone:**
- First use: inline CSS/HTML
- Second use: extract a CSS class
- Third use: consider whether JS adds value → if yes, make it a component

### Current inventory (correctly placed):

| Level | Elements | Count |
|-------|----------|-------|
| 0-2 (CSS) | key-concept, note, lesson-meta, next-steps, comparison, code blocks, SVG, tables | 15 |
| 3-4 (Enhancement) | Collapsible sections, glossary terms, theme toggle, progressive reveal, **CodeBlockToolbar** (new) | 5 |
| 5 (Full) | QuizView, MapView, IndexView, LessonActions, TypographyPanel, GenStream, ReviewView | 7 |

## Why not Storybook

- Storybook requires a bundler (Vite/Webpack) — breaks zero-build architecture
- HTM templates need wrapper functions for stories — friction without value
- ~15 components don't justify the overhead (threshold: ~30+)
- The existing `visual-qa` Playwright approach already captures screenshots
- Design review between AI and human happens in chat with screenshots, not a browsable catalog

**Instead:** Component showcase page + Playwright snapshots + `mise run visual-qa`.

## Acceptance criteria

- [x] CSS styles for `pre[data-file]`, `pre[data-mode="diff"]`, `pre[data-mode="fragment"]` in style.css
- [x] `CodeBlockToolbar.js` component with copy + conditional download
- [x] Mounted via page-shell.js `initCodeBlockToolbar()`
- [x] Copy strips diff spans (outputs clean code)
- [x] Shared signal prevents multiple "Copied!" feedback simultaneously
- [x] Download button appears only when `code/` directory exists (HEAD check)
- [x] `assets/showcase.html` renders all components in key states
- [x] Component abstraction strategy documented in `.memory/` or steering
- [x] Tickets #162 and #168 reference this as parent
