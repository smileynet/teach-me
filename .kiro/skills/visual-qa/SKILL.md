---
name: visual-qa
description: "Run visual QA on lesson pages — exercise interactive components, capture screenshots, report findings. Use after UI changes or feature additions. Trigger: visual qa, check the ui, screenshot all pages, verify components, test the lessons visually, check glossary visuals."
metadata:
  type: process
  invocation: both
  practice: null
---

# Visual QA

Exercise interactive components in lesson pages, capture screenshots at each interaction state, and produce a structured report.

## Two Modes

### Full check (all pages, all components)

```bash
mise run visual-qa
```

Runs against every `lessons/*.html` page. Detects which components are present, exercises each one, captures screenshots, and reports pass/fail.

### Feature-focused check (one component across all pages)

```bash
mise run visual-qa:focus -- glossary
mise run visual-qa:focus -- quiz
mise run visual-qa:focus -- reveal
mise run visual-qa:focus -- diagrams
```

After building or modifying a specific component, run focused mode to exercise only that feature. Faster, and the output is scoped to what you just changed.

## When to use

| Situation | Mode |
|-----------|------|
| After modifying `assets/glossary.js` or `glossary.css` | `--focus glossary` |
| After running the jargon skill on a lesson | `--focus glossary` |
| After modifying quiz or reveal components | `--focus quiz` / `--focus reveal` |
| After writing a new lesson with diagrams | `--focus diagrams` |
| Before closing a visual feature ticket | Full check |
| After any change to `assets/style.css` | Full check |
| CI / pre-push validation | Full check |

## Output

Screenshots and a manifest go to `.scratch/visual-qa/`:

```
.scratch/visual-qa/
├── manifest.json              # structured results (machine-readable)
├── 0001-iceberg-metadata-tree/
│   ├── full-page.png
│   ├── glossary-hover.png
│   ├── glossary-tray-term.png
│   ├── glossary-tray-list.png
│   └── ...
└── spike-quiz-test/
    ├── quiz-initial.png
    └── quiz-answered.png
```

### manifest.json

```json
{
  "summary": {"pages": 5, "interactions": 23, "checks_passed": 15, "checks_failed": 0}
}
```

Exit code: 0 = pass, 1 = failures.

## What it checks per component

| Component | Checks |
|-----------|--------|
| Glossary | Terms resolve to definitions, hover shows tooltip, click opens tray, back shows list, escape closes |
| Quiz | Options render, clicking answer shows green/red feedback |
| Progressive reveal | Steps detected, Next button advances through all, each step captured |
| Diagrams | SVG elements have non-zero bounding boxes |
| All | No JavaScript console errors |

## Interpreting results

A **pass** means the component behaves correctly (opens, closes, renders). It does NOT check visual aesthetics — for that, open the screenshots and review against `.kiro/steering/visual-teaching.md`.

A **fail** means a component is broken: tooltip doesn't appear, tray won't open, quiz gives no feedback, SVG has zero dimensions. Fix the component before shipping.

## For deeper visual review

After the tool runs, load screenshots for image analysis:

```
Read .scratch/visual-qa/manifest.json for results.
If failures: read the failing screenshots and diagnose.
If pass but want aesthetics review: read screenshots and compare against
visual-teaching.md color vocabulary and spatial contiguity rules.
```

## Dependencies

- `playwright` Python package (installed via `mise run setup`)
- Chromium browser (install via `playwright install chromium`)
- No running server needed — uses `--serve` flag to auto-start one
