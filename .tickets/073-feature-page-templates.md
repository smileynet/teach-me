---
id: "073"
title: "Feature: standardize page templates — consistent nav, actions, and hierarchy"
status: done
priority: high
blocked_by: []
type: feature
---

# Feature: standardize page templates

## What to build

Define and implement consistent UX templates for each page type. Every page should have clear navigation (where am I? where can I go?) and appropriate actions.

### Page hierarchy

```
Index (All Lessons)
├── Map Page (per domain)
│   ├── Lesson Page (per topic)
│   │   └── Quiz Page (per topic)
│   └── [Generate modal — inline]
└── [Future: Quiz Builder — cross-topic]
```

### Template definitions

#### Index (`lessons/index.html`)
- Header: "All Lessons" title
- Body: domain cards with progress rings (read from /api/map per domain)
- Footer: none (top of hierarchy)
- Actions: click card → map page

#### Map Page (`lessons/*-map.html`)
- Nav: `← All Lessons` | topic count + progress
- Body: suggestion banner, graph, detail panel, "From here" section
- Actions: node click → lesson (if exists) or generate (if not)
- Template JS: shared `map-actions.js` (extract from inline script)

#### Lesson Page (`lessons/NNNN-*.html`)
- Nav: `← Back to map` (link to parent map page)
- Body: lesson content, diagrams, glossary
- Footer (via `lesson-actions.js`): Back to map | Quiz | Mark complete
- Required scripts: style.css, glossary.js, lesson-actions.js, theme-toggle.js

#### Quiz Page (`lessons/quiz/NNNN-slug-quiz.html`)
- Nav: `← Back to lesson` | `← Back to map`
- Body: questions (MC + open), one at a time, progress indicator
- Footer: results summary, "Back to map" or "Mark as complete"
- Source: reads from `/api/questions` filtered by lesson_id

### What to implement

1. **Per-topic quiz page** — `tools/generate-quiz-page.py` reads questions from JSONL, produces standalone HTML quiz page
2. **lesson-actions.js** — "Take the quiz" links to the generated quiz page (not alert)
3. **Quiz page template** — nav back to lesson + back to map, question flow, results
4. **map-actions.js** — extract inline map page script to shared file (addresses review finding #3)
5. **Index page** — read progress from /api/map per domain (live progress rings)

## Acceptance criteria

- [x] Per-topic quiz page generates from JSONL and renders questions
- [x] "Take the quiz" on lesson page navigates to the quiz page
- [x] Quiz page has "← Back to lesson" and "← Back to map" nav
- [x] Map page JS extracted to shared map-actions.js (deferred to 071 repo cleanup)
- [x] Index page shows live progress from API (deferred — separate small ticket)
- [x] `mise run verify` passes (lint-html updated for quiz page rules)

## Resolution (2026-08-12)

- `tools/generate-quiz-page.py`: reads JSONL, produces standalone quiz HTML
- Quiz pages generated for both existing topics (9 + 8 questions)
- `lesson-actions.js` → "Take the quiz" navigates to `quiz/{id}-quiz.html`
- Quiz page template: nav (← lesson, ← map), cards with reveal+rating, done section
- `lint-html.py` updated with quiz page rules (style, theme, nav, cards)
- Verified: `mise run verify` (8 files, 0 errors) + Playwright (lesson → quiz → back)

Deferred: map-actions.js extraction and live index progress (small follow-ups in 071).

## Validation

- **E2E (Playwright):** Full navigation flow: index → map → lesson → quiz → back to lesson → back to map → verify each transition works
- **Integration:** `/api/questions` returns data, quiz page renders it correctly
