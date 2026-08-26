---
id: "122"
title: "Feature: User-configurable quiz question mix and on-demand generation"
status: open
blocked_by: []
tags: [platform]
---

# Feature: User-configurable quiz question mix and on-demand generation

## What to build

Let users control what kinds of questions get generated and how many. Two capabilities:

1. **Question mix preferences** — user specifies the ratio of question types they want (e.g., "more scenario-based, fewer recall", "50% interactive, 30% open-answer, 20% multiple choice"). Preferences are saved and applied to all future generation.

2. **Generate more on request** — after completing a quiz, user can say "more questions" or "harder questions" and get additional questions generated for the same topic without regenerating the lesson.

## Acceptance criteria

- [ ] User can set question type preferences (stored in workspace config or NOTES.md)
- [ ] Preferences are respected by generate-topic pipeline and quiz-me skill
- [ ] "Generate more" action available from the quiz page (button or command)
- [ ] Additional questions are appended to existing JSONL (not replacing)
- [ ] User can request specific types: "give me more scenario questions about X"
- [ ] Quiz page updates to show the new questions without full page regeneration
- [ ] Preferences include both type (open-answer, MC, interactive) and difficulty (recall, apply, synthesize)
