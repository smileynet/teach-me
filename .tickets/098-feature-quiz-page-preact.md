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
