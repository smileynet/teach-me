---
id: "147"
title: "Feature: adaptive chunking — adjust chunk size based on content complexity and learner pace"
status: open
blocked_by: ["139"]
priority: low
tags: [source-ingest]
---

# Feature: adaptive chunking

## Context

Research finding (135-chunking): the default 800-2000 word / 2-4 objective chunk is a heuristic. Real documents vary — dense spec sections need smaller chunks, narrative sections can be larger. Learner pace varies too.

## What to build

Adjust chunk boundaries based on:
- **Content complexity** — dense/technical sections split smaller; narrative/motivational sections stay larger
- **Concept density** — count distinct concepts introduced; split when >4 per chunk
- **Learner signals** — if SR data shows poor retention on a topic, suggest splitting its lesson into sub-lessons

Complexity heuristics:
- Code block density
- Jargon term frequency (from glossary)
- Sentence complexity (clauses per sentence)
- Prior knowledge assumptions (references to undefined terms)

## Acceptance criteria

- [ ] Complexity scoring function for document sections
- [ ] Chunk boundaries adjust based on complexity (denser = smaller chunks)
- [ ] Concept density check prevents >4 new concepts per lesson
- [ ] SR retention data can trigger "split this lesson" suggestion
- [ ] Default heuristic still works when no adaptive signal available
