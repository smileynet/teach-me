---
id: "106"
title: "Remove deprecated vanilla JS + old Graphviz map generator"
type: chore
status: open
priority: low
blocked_by: ["096", "097", "098", "099", "101", "102", "103"]
---

# Remove deprecated vanilla JS + old Graphviz map generator

## What to build

Delete legacy code once all pages are converted to Preact. Only after all consumers are migrated.

## Files to remove

- `assets/lesson-actions.js` (replaced by `assets/components/LessonActions.js`)
- `assets/progressive-reveal.js` (replaced by `assets/components/ProgressiveReveal.js`)
- `assets/quiz.js` (replaced by `assets/components/InlineQuiz.js`)
- `assets/glossary.js` (replaced by `assets/components/GlossaryTerm.js`)
- `assets/theme-toggle.js` (integrated into Preact shell or kept as standalone — evaluate)
- Old Graphviz generation code in `generate_map_page.py` (the current `generate_dot()` function and related SVG template)
- `tools/spike-dag-cards.html` (superseded by production map page)
- `tools/spike-alpine-d3dag.html` (spike complete)
- `tools/spike-preact-dagre.html` (spike complete)

## Acceptance Criteria

- [ ] No page references removed files
- [ ] `mise run verify` passes (all link checks, all tests)
- [ ] git log preserves history of removed files
- [ ] No functional regression in any page

## Gate

This ticket ONLY opens after all of 096-103 are done. Do not partially remove.
