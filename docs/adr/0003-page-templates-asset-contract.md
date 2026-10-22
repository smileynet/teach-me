# ADR 0003: Agent-Complete Pages with Shared Asset Contract

## Status

Accepted (2026-08-09)

## Context

The quick-check review page was generated with hardcoded hex colors while lessons used CSS variables. Without a template contract, every new page type reinvented its styling — breaking dark mode, theme toggle, and visual consistency.

The question: how should we ensure consistent pages without adding a build step, framework, or SSG?

## Decision

The agent generates complete, standalone HTML documents. Consistency comes from a **shared asset contract** (not a template engine or build system):

1. **Shared `style.css`** with CSS custom properties — the single source of visual truth
2. **Page scaffolds** in `assets/scaffolds/` — the agent reads the matching scaffold before generating a page type
3. **Custom Elements** only for genuinely interactive widgets (glossary, quiz, progressive-reveal, theme-toggle)
4. **No build step** — pages work from `file://` and simple HTTP servers
5. **Regeneration over synchronization** — when structure changes, regenerate affected pages

## Alternatives Considered

| Alternative | Why rejected |
|-------------|-------------|
| Static site generator (Eleventy, Hugo) | Adds build step and template language; the agent IS the template engine |
| Web Components for everything | Over-engineering for static content; most pages are read-only |
| Client-side includes (fetch + inject) | Breaks `file://`; adds JS dependency for basic structure |
| Markdown → HTML build | Loses precise HTML control; agent already outputs HTML natively |

## Consequences

- Agent reads `assets/scaffolds/<type>.html` before generating a new page
- All styling uses CSS variables — hardcoded hex is a violation
- `theme-toggle.js` required in every page (dark/light mode support)
- New page types require a new scaffold (documented in `assets/scaffolds/README.md`)
- No external tooling needed to view pages — open in any browser
