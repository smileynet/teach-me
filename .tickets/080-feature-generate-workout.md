---
id: "080"
title: "Feature: generate workout-fundamentals example — 2 topics + quizzes"
status: done
priority: high
blocked_by: []
type: feature
tags: [platform]
---

# Feature: generate workout-fundamentals topics

## What to do

Generate 2 additional topics for the workout-fundamentals example workspace (already has 1 lesson on progressive overload).

### Steps
1. Review existing MISSION.md and lesson 0001
2. Generate MAP.md if not present (5-7 topics covering exercise science fundamentals)
3. Generate 2 topic lessons (e.g., "Recovery & Adaptation", "Programming Basics")
4. Generate quiz pages for all topics with lessons
5. Verify structure matches the workspace pattern

### Expected result
```
examples/workout-fundamentals/
  MISSION.md (exists)
  RESOURCES.md (exists)
  maps/workout-fundamentals.MAP.md (new)
  lessons/0001-progressive-overload.html (exists)
  lessons/0002-*.html (new)
  lessons/0003-*.html (new)
  lessons/quiz/*-quiz.html (new)
  learning-records/questions/*.jsonl (update)
  reference/*.html (new)
```

## Validation

- `mise run verify` passes
- Playwright: lessons load, quiz pages have questions, nav works

## Resolution (2026-08-12)

TBD
