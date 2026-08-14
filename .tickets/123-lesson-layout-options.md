---
id: "123"
title: "Feature: Lesson layout options — cards, collapsible sections, content chunking"
status: open
blocked_by: []
---

# Feature: Lesson layout options — cards, collapsible sections, content chunking

## What to build

User-controllable layout modes for lesson content. Instead of one long scrolling page, offer options to break content into visual chunks: card-based sections, collapsible/expandable headings, or paginated view. Reduces cognitive load and lets users focus on one concept at a time.

Layout modes:
- **Flow** (current default) — continuous scroll, all sections visible
- **Cards** — each h2 section becomes a distinct card with borders/spacing
- **Collapsible** — sections collapse to headings, expand on click (accordion)
- **Paginated** — one section per "page" with prev/next navigation

## Acceptance criteria

- [ ] User can switch between layout modes from a control on the lesson page
- [ ] Card mode: each h2 section wrapped in a visually distinct card (border, background, spacing)
- [ ] Collapsible mode: sections collapse to just their h2 heading, click to expand
- [ ] Current section stays expanded/visible on page load (via URL hash or localStorage)
- [ ] Preference persists across sessions (localStorage, same pattern as typography prefs)
- [ ] Diagrams and code blocks remain fully visible within their section
- [ ] Works with all font size/spacing combinations from ticket 116
- [ ] Mobile-friendly: cards stack, collapse touch targets ≥ 44px
- [ ] No content loss — all modes show the same content, just structured differently
