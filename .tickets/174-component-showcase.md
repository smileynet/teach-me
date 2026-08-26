---
id: "174"
title: "Component showcase page for design review"
status: open
blocked_by: []
tags: [platform]
---

# Component showcase page for design review

## Context

With ~15 components and a zero-build architecture, Storybook is overkill. But we still need a way to:
1. See all components in their meaningful states at a glance
2. Spot visual regressions after CSS changes
3. Have design review conversations (human browses, AI gets Playwright screenshots)
4. Validate dark/light theme consistency across all elements

A single HTML page that renders every component variant replaces Storybook for our scale.

## What to build

### `assets/showcase.html`

A self-contained page that imports and renders all components + CSS patterns in key states. Organized by abstraction level:

**Section 1: CSS-only patterns** (no JS needed to verify)
- `.key-concept` block
- `.note` / callout (info, warning, error variants)
- `.lesson-meta` header
- `.next-steps` section
- `.comparison` grid
- `<details>` / collapsible
- Tables (standard + prior art style)
- Inline `<code>` and block `<pre><code>`
- Code blocks with `data-file` (filename label via ::before)
- Code blocks with `data-mode="diff"` (warning border)
- Code blocks with `data-mode="fragment"` (dashed border)
- SVG diagram (with CSS var colors)
- Buttons (primary, secondary, disabled)

**Section 2: Progressive enhancement** (JS adds behavior)
- Glossary term with tooltip
- Collapsible sections (LayoutMode)
- CodeBlockToolbar (copy + download states: idle, copied, no-download, with-download)
- Progressive reveal (step 1, mid, final)
- Theme toggle (dark → light transition)

**Section 3: Full components** (Preact-rendered)
- LessonActions bar (with quiz, without quiz, completed state)
- TypographyPanel (open, showing each setting)
- TopicCard (not-started, in-progress, complete)
- Inline quiz (prompt, revealed answer)

### Mise task

```toml
[tasks."showcase"]
run = "python -m http.server 8788 --bind 0.0.0.0 --directory assets"
description = "Serve component showcase at http://localhost:8788/showcase.html"
```

### Integration with visual-qa

Extend `mise run visual-qa` to include the showcase page:
- Capture dark + light mode screenshots
- Compare against baseline (pixel diff)
- Report any visual regressions

## Acceptance criteria

- [ ] `assets/showcase.html` exists and renders all CSS patterns from Section 1
- [ ] Progressive enhancement components mount and function (Section 2)
- [ ] Full components render in representative states (Section 3)
- [ ] Page works in both dark and light theme (toggle included)
- [ ] `mise run showcase` serves it
- [ ] `mise run visual-qa` includes showcase in its screenshot capture
- [ ] No external dependencies (uses existing vendored Preact/HTM/Signals)
