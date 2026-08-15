# Lesson Components

## Theming (all pages)

Every HTML page MUST use the shared theme. No hardcoded colors.

Required: `style.css` link + `theme-toggle.js` before `</body>`. Use CSS variables only — see `assets/scaffolds/README.md` for the path depth table and variable reference.

## Page Scaffolds

Read `assets/scaffolds/<type>.html` before generating any page. Copy structure, replace placeholders.

| Type | Scaffold | Output |
|------|----------|--------|
| Lesson | `assets/scaffolds/lesson.html` | `lessons/NNNN-slug.html` |
| Reference | `assets/scaffolds/reference.html` | `reference/NNNN-slug.html` |
| Quick-check | `assets/scaffolds/quick-check.html` | `lessons/review/quick-check.html` |

## Diagrams

Every architectural/conceptual explanation needs a visual.

| Diagram type | Tool |
|-------------|------|
| Stack, flow, hub, small graph (≤8 nodes) | `draw-diagram.py --type X` |
| Cycles, state machines, 9+ nodes | `draw-diagram.py --type graph --backend graphviz` |
| Custom/annotated | Raw inline SVG from `assets/svg-patterns.md` |
| Sequence diagrams | D2 (`d2 input.d2 output.svg`) |

Rules: one-line summary above, 5-9 elements max, progressive reveal for 3+ layers, labels ON diagram.

## Glossary Terms

First use of a domain term → wrap in tooltip:
```html
<span class="term" data-term="snapshot">snapshot</span>
```
Include glossary JSON block at bottom (before page-shell.js). After lesson, add terms to `.memory/CONTEXT.md`.

## Collapsible Details

Use `<details>` for optional depth: deep dives, operational notes, prior-concept reminders. Core content stays in the main flow — never hide required understanding.

## Exercises

Test understanding, not recall. "Your customer asks X — explain why the naive approach breaks" beats "List the layers."

Use `<details>` for progressive hints. Frame around the learner's mission context.

## Self-Assessment (review pages)

Rating prompt: **"Could you explain this?"** with plain everyday language options:
- **No** — couldn't explain it
- **Sort of** — got parts but not the full picture
- **Yes** — could walk someone through it

Never use jargon, scores, or technical SRS terminology in learner-facing UI.

## Limitations Framing

When a topic has things the system can't teach (physical skills, subjective judgment, community wisdom), frame them as **"What to pursue alongside this"** — actionable high-value recommendations, not defensive disclaimers.

- ✓ "Get 2-3 coaching sessions for compound lifts"
- ✗ "This system cannot teach you form"

## Footer Scripts (Required)

Every lesson page ends with:

```html
<script type="importmap">
{
  "imports": {
    "preact": "../assets/vendor/preact.module.js",
    "preact/hooks": "../assets/vendor/preact-hooks.module.js",
    "@preact/signals": "../assets/vendor/preact-signals.module.js",
    "@preact/signals-core": "../assets/vendor/signals-core.module.js",
    "htm": "../assets/vendor/htm.module.js"
  }
}
</script>
<script type="module" src="../assets/page-shell.js"></script>
```

This provides: glossary tooltips, collapsible sections, typography panel, and the lesson action bar (← Back to map, Take quiz, Mark complete). The import map MUST appear before the module script. `page-shell.js` is the single entry point — never import components individually.
