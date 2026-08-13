---
id: "103"
title: "Convert quiz.js + glossary.js to Preact components"
type: feature
status: open
priority: low
blocked_by: ["095"]
---

# Convert quiz.js + glossary.js to Preact components

## What to build

Inline quiz interactions (embedded in lessons) and glossary term tooltips as Preact components.

## Deliverables

- `assets/components/InlineQuiz.js` — multiple choice / open answer within a lesson
- `assets/components/GlossaryTerm.js` — hover/click tooltip showing term definition
- Both mount as islands in static lesson HTML (custom elements or mount-point divs)

## Acceptance Criteria

- [ ] Inline quiz renders question + choices, reveals answer on selection
- [ ] Glossary terms show tooltip on hover/focus with definition
- [ ] Both work in static lesson pages as progressive enhancement
- [ ] Glossary data loaded from `glossary-data` JSON block in page
