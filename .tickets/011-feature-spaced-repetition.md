---
id: "011"
title: "Feature: quiz question bank for spaced repetition (post-MVP)"
status: open
priority: low
blocked_by: ["003"]
type: feature
---

# Feature: quiz question bank for spaced repetition

## Post-MVP — build after core teaching flow is proven

## What to build

Optionally generate and store quiz questions in a structured format (JSON) so they can be surfaced later for spaced repetition review.

## Design sketch

- Each lesson generates quiz questions as part of authoring
- Questions are stored in `quizzes/<lesson-number>.json` alongside the lesson
- A review mode (`/quiz-me` with no specific topic) pulls questions weighted by:
  - Time since last seen (spacing)
  - Previous correct/incorrect history (difficulty)
  - Mission relevance
- localStorage tracks per-question history (last seen, streak, ease factor)
- Optional: Leitner box system (simple) or SM-2 algorithm (robust)

## Format

```json
{
  "lesson": "0001-iceberg-metadata-tree",
  "questions": [
    {
      "prompt": "What problem does Iceberg's manifest file solve?",
      "options": [...],
      "correct": 0,
      "explanations": [...],
      "sources": [...],
      "tags": ["metadata", "manifests", "query-planning"]
    }
  ]
}
```

## Why post-MVP

- Core teaching flow (lessons + immediate quizzes) needs to work first
- Spaced repetition adds complexity (scheduling, persistence, UI for review sessions)
- Need real usage data to calibrate intervals

## Acceptance criteria

- [ ] Quiz questions stored as JSON alongside lessons
- [ ] Review mode surfaces questions weighted by spacing + difficulty
- [ ] History persists in localStorage (or a file the agent can read)
- [ ] Integrates with `quiz-me` skill
