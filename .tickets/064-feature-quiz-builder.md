---
id: "064"
title: "Feature: quiz availability page + cross-topic quiz builder"
status: open
priority: low
blocked_by: []
type: feature
---

# Feature: quiz availability page + cross-topic quiz builder

## Problem

Quizzes are currently per-topic (generated alongside lessons) but there's no way to:
1. See which topics have quizzes available at a glance
2. Combine questions from multiple topics into a mixed review session
3. Choose a quiz scope ("just this topic" vs "everything I've learned")

## What to explore

### Quiz availability page
- List all topics with quiz status (has questions / no questions / N questions)
- Launch a quiz for any single topic
- Visual indication of last-reviewed date and which topics are "due"

### Cross-topic quiz builder
- Select multiple topics → combine their questions into one session
- "Quiz me on everything" button that pulls from all topics with questions
- Weighted selection: prioritize topics with lower mastery / longer since review
- Shuffle order across topics (interleaving)

### Integration points
- Topic lesson pages: "Take the quiz →" link at bottom (or "Generate quiz" if none exists)
- Map page: nodes link directly to lessons (not detail panel) when lesson exists; quiz access from within the lesson
- SR system: quiz builder respects spaced repetition scheduling

## Deliverable

A standalone page (or section of the index page) showing quiz availability, plus a "start quiz" flow that combines questions from selected topics.

## Validation

- **E2E (Playwright):** Navigate to quiz page → verify topics with questions shown → select 2 topics → start quiz → verify questions from both topics appear → complete quiz → verify results shown
- **Integration:** `/api/questions` already returns per-lesson counts; extend or add `/api/quiz/build` endpoint that returns shuffled questions from selected topics
