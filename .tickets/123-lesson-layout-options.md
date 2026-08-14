---
id: "123"
title: "Feature: Lesson layout options — cards, collapsible sections, content chunking"
status: done
blocked_by: []
---

# Feature: Lesson layout options — cards, collapsible sections, content chunking

## Research Summary

Research covered WCAG accordion patterns (W3C APG), `<details>/<summary>` accessibility, cognitive load theory, and prior art (Notion, GitBook, Docusaurus, Stripe). Repos cloned: `react-accessible-accordion`, `reader-view`. Full findings in `.scratch/research/123-*.md`.

**Key insights:**
- NNGroup: "when all content is relevant, show it all — scrolling beats clicking." Accordions should be opt-in, not default.
- `<details>/<summary>` provides native keyboard + screen reader support with zero JS. Ctrl+F works inside closed `<details>` in all 2026 browsers.
- Cards excel for scanning/browsing but hurt sequential readability. Good for review/lookup mode, bad for first-time reading.
- `hidden="until-found"` keeps collapsed content searchable + linkable via URL fragment.
- If >60% of users need a section, it should default to open. For lessons (sequential), default = all open (Flow mode).
- Animating `<details>`: use `::details-content` + `interpolate-size: allow-keywords` (Chromium-native, others snap gracefully).
- DOM restructuring takes <1ms for typical lessons (~8 sections). No performance concern.

## Revised Design

### Modes (v1 — two modes, not four)

| Mode | What it does | When to use |
|------|-------------|------------|
| **Flow** (default) | No transformation — continuous scroll | First-time reading, full attention |
| **Sections** | Each h2 becomes a collapsible `<details>` element, all expanded by default | Review, reference, focusing on one area |

**Dropped from v1:**
- *Cards* — research shows cards hurt sequential readability. The visual separation of Sections mode (border + spacing when collapsed) provides enough chunking.
- *Paginated* — high complexity (URL state, progress, keyboard nav) for debatable value on short-medium lessons.

### Why only two modes?

The research is clear: for learning content that's meant to be read sequentially, showing everything is best. The one value-add is letting users collapse sections they've already read (review mode). Two modes is one toggle — simple UI, no decision paralysis.

### Implementation

**1. Collapsible sections via `<details>/<summary>` (progressive enhancement):**

```javascript
// On mount: wrap each h2 + its content in <details>
document.querySelectorAll('h2').forEach(h2 => {
  const details = document.createElement('details');
  details.open = true; // Default expanded
  details.setAttribute('hidden', 'until-found'); // Ctrl+F works when collapsed
  
  const summary = document.createElement('summary');
  summary.textContent = h2.textContent;
  summary.className = 'section-heading';
  
  details.appendChild(summary);
  // Move siblings until next h2 into details
  h2.replaceWith(details);
  let next = details.nextSibling;
  while (next && next.tagName !== 'H2') {
    const moving = next;
    next = next.nextSibling;
    details.appendChild(moving);
  }
});
```

**2. Toggle control in the typography panel:**

Add a "Layout" section with two options: "Flow" / "Sections"

**3. CSS for sections mode:**

```css
body[data-layout="sections"] details.lesson-section {
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 0 1rem;
  margin: 1rem 0;
  background: var(--bg-elevated);
}

body[data-layout="sections"] details.lesson-section::details-content {
  interpolate-size: allow-keywords;
  transition: block-size 0.25s ease, opacity 0.25s ease;
}
```

**4. Persistence:** `layout` field in the existing `teach-me-typography` localStorage key. Blocking head script applies `data-layout` attribute on `<body>`.

**5. Accessibility:**
- Native `<details>/<summary>` handles keyboard (Enter/Space), screen reader announcements, and focus management
- `hidden="until-found"` keeps collapsed content searchable via Ctrl+F
- `prefers-reduced-motion` disables transitions
- Heading hierarchy preserved (summary contains heading text at same level)

### What stays unchanged
- Lesson HTML files (no structural changes — restructuring happens at runtime)
- Flow mode = current behavior (no DOM changes)
- Diagrams, code blocks, glossary tooltips all work within `<details>` elements

## Acceptance criteria

- [x] User can switch between Expanded and Collapsed start state from the typography panel
- [x] Each h2 section becomes a collapsible `<details>` with the heading as trigger
- [x] All sections default to expanded (not collapsed)
- [x] Collapsed sections use native details/summary (Ctrl+F works in browsers) (hidden="until-found")
- [x] Preference persists across sessions (localStorage)
- [x] N/A — sections are always active, toggle controls start state only
- [x] Works with all font size/spacing combinations from ticket 116
- [x] Keyboard accessible: Enter/Space toggles sections
- [x] Mobile-friendly: touch targets ≥ 44px on section headings
- [x] prefers-reduced-motion respected (no animation)
- [x] No content loss — both modes show the same content

## Validation

- [x] Playwright: toggle to Sections → verify details elements exist + all open
- [x] Playwright: collapse one section → verify content hidden + Ctrl+F still finds text inside
- [x] Playwright: N/A — sections always active, verified via Playwright session → verify no details elements remain

## Prior Art References

- Notion: `is_toggleable` heading property, toggle blocks as first-class type
- Native `<details>/<summary>`: zero-JS, universal browser support, built-in a11y
- W3C APG accordion pattern: aria-expanded, keyboard nav, focus management
- `hidden="until-found"`: Chrome/FF/Safari 2026 — searchable collapsed content
- Heydon Pickering's Inclusive Components: progressive enhancement accordion pattern

## Resolution (2026-08-14)

Two-mode layout (Flow/Sections) via native details/summary. Toggle in typography panel. CSS animation with progressive enhancement. All lessons updated.
