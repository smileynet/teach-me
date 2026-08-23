---
status: accepted
date: 2026-08-23
---

# ADR 0008: Component Abstraction Strategy

## Context

With ~15 interactive elements and a zero-build stack (Preact + HTM + Signals, no bundler), we needed a decision framework for when to extract a Preact component vs when CSS alone suffices. Without this, each new UI element triggered a "should this be a component?" discussion. Ticket #173 (CodeBlockToolbar) was the forcing function — it started as two separate tickets (#162 copy, #168 download) before we recognized they belong in one progressive-enhancement component.

This extends ADR 0005 (Preact adoption) by defining the *boundary* between Preact territory and CSS-only territory.

## Decision

### The Flowchart

```
Does it need JavaScript to function?
├─ No → CSS class/attribute selector (Level 0–2)
│       e.g., .key-concept, .note, pre[data-file]::before
└─ Yes → Does it work (degraded) without JS?
    ├─ Yes → Progressive enhancement (Level 3–4)
    │       e.g., CodeBlockToolbar, Glossary tooltips, Collapsible sections
    └─ No → Full Preact component (Level 5)
            e.g., QuizView, MapView, GenerationStream
```

### Bright Lines

**Always a component** (Level 4–5):
- Has keyboard navigation requirements
- Manages internal state across interactions
- Consumes external services (API, SSE)
- Has 3+ interactive variants that share logic

**Never a component** (Level 0–2):
- Pure visual styling (colors, spacing, borders)
- Static layout patterns (grid, flex arrangements)
- Content that reads correctly without JS

### Rule of Three (gray zone)

- First use: inline CSS/HTML
- Second use: extract a CSS class
- Third use: evaluate whether JS adds value → if yes, make it a component

### Current Inventory

| Level | Elements | Count |
|-------|----------|-------|
| 0–2 (CSS) | key-concept, note, lesson-meta, next-steps, comparison, code blocks (filename, diff, fragment), SVG, tables | ~15 |
| 3–4 (Enhancement) | CodeBlockToolbar, glossary terms, collapsible sections, theme toggle, progressive reveal | 5 |
| 5 (Full) | QuizView, MapView, IndexView, LessonActions, TypographyPanel, GenerationStream, ReviewView | 7 |

## Alternatives Considered

- **Storybook** — requires a bundler, breaks zero-build architecture, overkill for ~15 components
- **Web Components (custom elements)** — Shadow DOM fights our global CSS theming; no benefit for internal-only components
- **Everything as components** — over-abstraction; a CSS class is simpler, faster to parse, and doesn't require JS to render

## Consequences

- New UI elements start as CSS-only unless they clearly need JavaScript
- The showcase page (`assets/showcase.html`) demonstrates all levels for design review
- Components mount via page-shell.js in a fixed order (documented in that file's header)
- Progressive enhancement components (Level 3–4) must render acceptably without JS loaded (filename labels via `::before`, glossary terms readable as plain text)
- This ADR is the authority when someone proposes a new component — reference the flowchart
