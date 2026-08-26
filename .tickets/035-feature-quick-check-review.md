---
id: "035"
title: "Feature: multiple-choice quick-check review page"
status: done
priority: medium
blocked_by: []
type: feature
tags: [platform]
---

# Feature: multiple-choice quick-check review page

## Current state

A static prototype exists at `lessons/review/quick-check.html` with 3 hand-coded cards (explain + 2 code blocks), reveal/rating interaction, and full CSS variable theming. What remains is **dynamic generation from the JSONL question bank** — a script that reads due cards and produces the page.

## What to build

A lightweight HTML review page (like the quiz component) that presents multiple-choice questions drawn from the SR question bank. Designed for fast validation — the learner clicks through 5-10 questions in 2-3 minutes. Complements the deeper Socratic gate with quick, low-friction knowledge checks.

## Use cases

1. **Session quick-check** — at the start of a session, before new material: "Quick check on what you covered last time" (5 questions, 2 minutes)
2. **Standalone review** — learner wants to practice but doesn't have time for a full Socratic dialog
3. **Mixed with Socratic gate** — quick-check handles factual retention, Socratic handles deeper conceptual understanding. Together they cover both recall and articulation.

## Design sketch

### Question generation

Extend the teach skill to generate two types of SR questions per lesson:
- **Explain-to-colleague** (existing) — for Socratic gate / deep review
- **Quick-check multiple-choice** — for fast validation / the review page

Quick-check questions test the same concepts but with a recognition format:
- 4 options, plausible distractors from adjacent concepts
- All options same length (no "longest is correct" tell)
- Randomized answer position

### Review page (HTML)

```
lessons/review/quick-check.html  (or generated per-session)
```

Uses the existing quiz component (`assets/quiz.js`) with cards drawn from the question bank. Could be:
- Static: agent generates an HTML page with selected questions
- Dynamic: page reads from a JSON file the agent writes before serving

### Integration

| Mode | Tool | Questions |
|------|------|-----------|
| Deep review | quiz-me skill (conversational) | explain-to-colleague cards |
| Quick check | review page (self-service HTML) | multiple-choice cards |
| Mixed | session start | quick-check first, then Socratic if time |

### Question format addition

```json
{
  "question_type": "quick-check",
  "prompt": "Which layer of Iceberg's metadata tree stores column-level statistics?",
  "options": [
    "Catalog entry",
    "Metadata file",
    "Manifest list",
    "Manifest file"
  ],
  "correct_index": 3,
  "explanation": "Manifest files store per-file stats (min/max per column, row count, null counts) that enable partition pruning.",
  "tags": ["iceberg", "manifests", "query-planning"]
}
```

## Open questions

- Generate quick-check questions alongside explain questions in the teach skill, or derive them later?
- Store in the same JSONL file (with `question_type: quick-check`) or separate?
- How to generate good distractors? (Adjacent concepts from the same lesson work well)
- Should quick-check questions feed into SM-2 scheduling, or be schedule-independent?

## Acceptance criteria

- [x] Multiple-choice question type added to Card schema
- [x] teach skill generates 2-3 quick-check questions per lesson alongside explain questions
- [x] Review page (HTML) presents questions using existing quiz component
- [x] Questions drawn from due cards (SR-scheduled) or manually selected
- [x] Correct/incorrect feeds back into review log
- [x] Can be invoked via `mise run sr:quick-check` or opened in browser
- [x] Complements (not replaces) Socratic dialog for deeper review
