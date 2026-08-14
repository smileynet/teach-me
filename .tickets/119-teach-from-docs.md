---
id: "119"
title: "Feature: Teach me a doc or book — generate lessons from source material"
status: open
blocked_by: []
---

# Feature: Teach me a doc or book — generate lessons from source material

## What to build

Point the agent at a document (PDF, URL, book, API docs) and it generates a topic map and lessons from that source material. Primary use case: "I need to learn this 50-page spec — break it into lessons for me." The agent reads the source, identifies key concepts, builds a MAP.md, and generates lessons that teach the material with the same quality as web-researched topics.

Secondary use case: "Quiz me on this doc" — comprehension testing without full lesson generation.

## Acceptance criteria

- [ ] User can provide a file path (PDF, MD, HTML) or URL as source material
- [ ] Agent reads/fetches the source and identifies teachable concepts
- [ ] Generates a MAP.md with topic ordering derived from the document structure
- [ ] Lessons cite the source document (page numbers, sections) rather than web sources
- [ ] Works with the existing generate-topic pipeline (research phase reads the doc instead of web)
- [ ] Handles documents up to ~100 pages / 50K words (chunking strategy for longer)
- [ ] Quick mode: "quiz me on chapter 3" without generating full lessons
