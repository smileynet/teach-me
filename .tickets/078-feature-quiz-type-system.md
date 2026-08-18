---
id: "078"
title: "Feature: quiz question type system — MC, open-answer, interactive SVG"
status: done
priority: medium
blocked_by: []
type: feature
---

# Feature: quiz question type system

## Problem

Quiz pages currently render all questions identically (prompt + reveal answer). But we already have three distinct question types demonstrated in the project:

1. **Multiple choice** — spike-quiz-test.html (click an option, get feedback)
2. **Open answer with self-rating** — quick-check cards (think, reveal, rate confidence)
3. **Interactive SVG / diagram recall** — diagram label masking (click to reveal hidden labels)

These should be formalized as a question type system so `generate-quiz-page.py` renders the right UI per question.

## What to build

### Question type meta in JSONL

Add a `render_type` field (or derive from existing `question_type`):

| question_type | render_type | UI |
|---------------|-------------|-----|
| explain, predict, apply | open-answer | Prompt → think → reveal → self-rate |
| quick-check | multiple-choice | Prompt + 3-4 options → click → correct/incorrect feedback |
| diagram-recall | svg-interactive | SVG with masked labels → click to reveal each |

### Template components

Each render type gets its own card template in the quiz page:

- **open-answer**: current card (prompt, reveal button, answer, rating buttons)
- **multiple-choice**: prompt + radio/button options + correct/incorrect state
- **svg-interactive**: inline SVG with `data-step` masked elements + click-to-reveal

### generate-quiz-page.py updates

- Read `question_type` from JSONL
- Map to render type
- Render appropriate card template
- MC questions need an `options` field + `correct_option` in the JSONL
- SVG questions need an `svg_data` field (or reference to a diagram file)

## Prior art (already in this repo)

- `assets/quiz.js` + `assets/quiz.css` — MC component
- `lessons/spike-quiz-test.html` — working MC demo
- `assets/progressive-reveal.js` — SVG label masking
- `lessons/spike-reveal-test.html` — working diagram recall demo

## Acceptance criteria

- [x] Quiz page renders MC questions — SUPERSEDED by #117 (sequence/match/fill types)
- [x] Quiz page renders open-answer questions with reveal + self-rating (already works)
- [ ] SVG recall questions — DEFERRED to #132 (interactive activities exploration)
- [x] All three types can coexist on the same quiz page (QuizView routes on question.type)
- [x] generate-quiz-page.py handles all types (passes through to QuizView)

## Validation

- **E2E (Playwright):** Load a quiz page with mixed question types → click MC option → verify feedback → reveal open answer → verify rating → click SVG label → verify reveal animation
- **Integration:** JSONL with all 3 question types → generate quiz page → verify HTML contains all 3 card templates

## Resolution

Merged into ticket 117 (Interactive quiz components). Ticket 117 has broader scope covering all interactive question types including MC, open-answer, and interactive SVG from this ticket plus drag-drop, fill-blanks, and matching. Closing as subsumed.
