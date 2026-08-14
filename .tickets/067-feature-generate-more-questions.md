---
id: "067"
title: "Feature: generate more — add quiz questions to existing topics"
status: done
priority: low
blocked_by: []
type: feature
---

# Feature: "generate more" quiz questions

## Problem

Currently quiz generation is all-or-nothing. Once questions exist for a topic, the button shows "Take the quiz (N questions)" with no way to add more. Users might want:
- More questions after mastering existing ones
- Questions targeting specific sections they found hard
- Different question types (predict, apply, explain) beyond what was initially generated

## What to consider

### UX
- "Generate more questions" button (appears when questions already exist)
- Optional: specify focus area ("I want questions about CDC patterns")
- Append to existing JSONL (don't overwrite)
- Show count before/after: "Added 5 questions (was 8, now 13)"

### De-duplication
- New questions shouldn't repeat existing ones
- Pass existing question prompts as context to kiro-cli
- Or: post-generation dedup pass comparing new vs existing

### Integration
- lesson-actions.js: show "Generate more" alongside "Take the quiz"
- Prompt construction: "generate 5 more questions for {title}, avoiding these existing questions: {list}"

## Validation

- **E2E (Playwright):** Load lesson with existing quiz → click "Generate more" → verify count increases after generation completes → verify no duplicate prompts in JSONL
- **Integration:** POST generation with a "more questions" prompt → verify JSONL grows (not replaced)

## Resolution

Subsumed by ticket 122 (User-configurable quiz question mix and on-demand generation). Ticket 122 includes "generate more on request" as a core feature plus configurable type/difficulty preferences. Closing as duplicate scope.
