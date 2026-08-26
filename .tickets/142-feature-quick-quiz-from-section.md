---
id: "142"
title: "Feature: quick quiz mode — 'quiz me on chapter 3' without full lesson generation"
status: done
blocked_by: ["139"]
tags: [source-ingest, platform]
---

# Feature: quick quiz mode

## What to build

Comprehension testing from a source section without generating full lessons. User says "quiz me on chapter 3" and gets immediate questions derived from that section's content.

Flow:
1. Identify the relevant chunks from the ingested source
2. Generate 4-6 questions directly (mix of archetypes + interactive types)
3. Render quiz page immediately
4. No MAP.md, no lesson, no reference doc — just questions from the material

Use cases:
- "I just read chapter 5, test my understanding"
- "Quiz me on the authentication section of this spec"
- "Check if I understood the key points of this paper"

## Acceptance criteria

- [x] User can specify a section/chapter of an ingested source
- [x] Questions generated from that section's content (4-6 mixed types)
- [x] Quiz page rendered immediately (no lesson generation step) — conversational via quiz-me skill
- [x] Questions have provenance (trace to the specific section)
- [x] Works with the "Could They Answer This?" gate
- [x] Accessible via both CLI command and in-chat request
