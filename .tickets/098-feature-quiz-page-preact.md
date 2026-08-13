---
id: "098"
title: "Convert generate-quiz-page.py to Preact output"
type: feature
status: open
priority: medium
blocked_by: ["095"]
work_order: 4
---

# Convert generate-quiz-page.py to Preact output

## What to build

Quiz page as Preact components — question cards with answer reveal, score tracking via signals, progress through questions.

## Deliverables

- Data island with questions (from JSONL)
- `QuizCard` component: prompt, answer reveal on click, self-assessment buttons
- `QuizProgress` component: current/total, score summary
- Signal-driven state: current question index, revealed answers, scores

## Acceptance Criteria

- [ ] Quiz page renders questions from JSONL data
- [ ] Click reveals answer with criteria-based evaluation
- [ ] Progress indicator shows position in deck
- [ ] Score summary at end
- [ ] Theme toggle works
- [ ] Loads offline (vendored deps)

## Context & Sources

- **Pattern:** Data island (questions JSON in page) — see `.scratch/research/python-to-preact-templating.md`
- **Helper:** `tools/lib/preact_page.py` — `render_page()` with quiz data serialized
- **Current code:** `tools/generate-quiz-page.py` (217 lines) — produces vanilla HTML quiz from JSONL
- **Questions format:** `learning-records/questions/<topic>.jsonl` — one JSON object per line with prompt, criteria, source
- **Components:** New `QuizCard`, `QuizProgress` components in `assets/components/`
