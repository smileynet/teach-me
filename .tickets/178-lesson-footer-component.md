---
id: "178"
title: "Theme and componentize end-of-lesson resources section"
status: open
blocked_by: []
---

# Theme and componentize end-of-lesson resources section

## Context

The end of each lesson currently has a scattered collection of sections with no visual grouping:
- Official Documentation (links to Godot docs)
- Prior Art (table of external tutorials/repos)
- Code Files (downloadable shader files)
- What's Next (navigation to next lesson)

These are all **supplementary material** — not the core teaching content — but they render with the same H2 styling as lesson sections, creating a flat information hierarchy. A reader scrolling through can't easily tell where the teaching ends and the resources begin.

## What to explore

### 1. Visual grouping

Design a distinct visual treatment for the "resources footer" that separates it from lesson content:
- Different background (e.g., `--bg-elevated` or `--bg-surface`)
- Horizontal rule or border-top as the divider
- Slightly smaller text or different heading style
- Grouped under one container with a clear "Resources & References" label

### 2. Information hierarchy options

| Option | Description |
|--------|-------------|
| **A. Single footer block** | All resources in one bordered container at the bottom |
| **B. Collapsible resources** | Resources default-collapsed, one-click to expand |
| **C. Tabbed resources** | Tabs: "Docs / Prior Art / Code / Next" |
| **D. Aside panel** | Fixed sidebar on wide screens, inline on mobile |

### 3. Component vs CSS

Decision framework says: does it need JS?
- If just visual grouping → CSS class (`.lesson-resources` wrapper div)
- If collapsible/tabbed → progressive enhancement component
- If content varies per lesson → data island + Preact render

Most likely answer: **CSS wrapper** with optional JS enhancement for collapse. This is a Level 1-2 element (CSS class), not a Level 4-5 component.

### 4. Proposed HTML structure

```html
<footer class="lesson-resources">
  <h2>Resources & References</h2>
  
  <section class="resource-group">
    <h3>Code Files</h3>
    <ul>...</ul>
  </section>

  <section class="resource-group">
    <h3>Official Documentation</h3>
    <ul>...</ul>
  </section>

  <section class="resource-group">
    <h3>Prior Art & Tutorials</h3>
    <table>...</table>
  </section>
</footer>

<div class="next-steps">
  <h3>What's Next</h3>
  <p>...</p>
</div>
```

### 5. CSS treatment sketch

```css
.lesson-resources {
  margin-top: 3rem;
  padding: 1.5rem;
  background: var(--bg-elevated);
  border: 1px solid var(--border);
  border-radius: 8px;
}
.lesson-resources h2 {
  font-size: 1.1rem;
  color: var(--text-muted);
  margin-top: 0;
}
.resource-group { margin-bottom: 1.5rem; }
.resource-group:last-child { margin-bottom: 0; }
.resource-group h3 {
  font-size: 0.95rem;
  color: var(--text);
}
```

### 6. Integration with page_template.py

Options:
- **A.** AI writes the footer HTML directly (current approach, just add the wrapper class)
- **B.** page_template.py accepts `resources` as structured data and renders the footer
- **C.** A post-processing step wraps the last N H2 sections in a footer div

Option A is simplest and matches the architecture-fit research (AI writes HTML, template wraps).

## Acceptance criteria

- [ ] Design decision documented (which visual hierarchy option)
- [ ] CSS for `.lesson-resources` and `.resource-group` in style.css
- [ ] At least one lesson updated to use the new structure
- [ ] Works in dark and light mode
- [ ] Visually distinct from core lesson content (clear hierarchy break)
- [ ] "What's Next" remains outside the resources footer (it's navigation, not reference)
- [ ] Convention documented in visual-teaching.md
- [ ] generate-topic skill instructs to use the footer structure
