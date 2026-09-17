---
id: "361"
title: "Align learner-dialog skill writes with local-only state"
status: in_progress
priority: high
type: bug
blocked_by: ["341"]
tags: ["arch-review", "skills", "privacy"]
validation_criteria:
  - "Learner-dialog skills never direct durable personal state into committed paths"
---

# Align learner-dialog skill writes with local-only state

## Intent

Align teaching and quiz skill instructions with the shared-repository rule that learner progress is local-only and never durable repository content.

## Context

The skill review found `quiz-me` directs writes under `learning-records/` and `NOTES.md`, paths that may be committed. This conflicts with #341 and the local progress architecture.

## What to build

Route all learner-specific notes, quiz outcomes, progress, and preferences to the approved local workspace overlay. Clarify which authored artifacts may be committed.

## Acceptance criteria

- [ ] Every learner-dialog skill names the approved local-only path or service for personal state.
- [ ] No active skill instructs an agent to create/update learner progress in a tracked path.
- [ ] The local workspace is created or diagnosed gracefully on first use.
- [ ] Prompt fixtures confirm quiz outcomes, notes, and pace preferences stay local while authored curriculum remains shareable.
- [ ] `.gitignore`, deployment assembly, and skill instructions describe the same ownership boundary.
