---
status: accepted
date: 2026-08-13
---

# ADR 0005: Preact + HTM + Signals for UI Components

## Context

The project generates interactive HTML pages (map views, quizzes, SR review) from Python scripts. The original approach used Graphviz for SVG graphs + inline vanilla JS for interactivity. This didn't scale — every new feature required reimplementing layout, theming, and reactivity in template strings.

## Decision

Adopted **Preact + HTM + Signals + dagre** as the UI component layer.

- **Preact** (4KB) — component model with hooks, no build step via ESM
- **HTM** (1KB) — tagged template literals replace JSX (no compiler needed)
- **Signals** (2.8KB) — fine-grained reactivity for SSE streaming and state
- **dagre** (30KB) — DAG layout computation for topic map cards

All deps vendored locally in `assets/vendor/` (no CDN dependency at runtime). Import maps resolve bare specifiers.

## Alternatives Considered

- **Alpine.js** — works for simple directives but degrades on large DOM trees (>100 nodes), no component model, d3-dag ESM timing issues
- **Solid.js** — best performance but requires compilation (hard constraint violation)
- **Lit** — viable but Shadow DOM fights global CSS theming
- **Vanilla JS** — what we had; doesn't compose, every page reinvents reactivity

## Consequences

- Python generators emit a static HTML shell + JSON data island; Preact reads and renders
- Components in `assets/components/` are reusable across page types
- SSE generation uses a standalone signal service (`assets/services/generation.js`)
- Old vanilla JS files (`lesson-actions.js`, `quiz.js`, `glossary.js`) retained during migration of existing lesson content but deprecated for new pages
- Import map must appear before any `type="module"` script in the HTML
