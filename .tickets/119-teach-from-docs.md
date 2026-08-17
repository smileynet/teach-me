---
id: "119"
title: "Feature: Teach me a doc or book — generate lessons from source material"
status: open
blocked_by: []
---

# Feature: Teach me a doc or book — generate lessons from source material

## What to build

Point the agent at a document (PDF, URL, book, API docs) and it generates a topic map and lessons from that source material. Primary use case: "I need to learn this 50-page spec — break it into lessons for me."

## Decomposed into ticket chain

This feature is delivered by tickets 135-142 + 143-147 (backlog):

```
135 [DONE] Research: chunking, provenance, multi-source synthesis
 ├── 136 [HIGH] Apply patterns across teach-me
 ├── 137 Spike: PDF extraction quality
 └── 138 Spike: MAP.md from doc structure
      └── 139 Feature: source ingest pipeline
           ├── 140 Feature: provenance-tracked questions
           │    └── 141 Feature: multi-source enrichment
           │         ├── 143 [low] Automated conflict detection
           │         └── 144 [low] Compounding reference docs
           └── 142 Feature: quick quiz from section
      └── 147 [low] Adaptive chunking

136 → 145 [low] Situation index navigation
136 → 146 [low] Author-as-perspective teaching
```

## Acceptance criteria (from original ticket)

- [ ] User can provide a file path (PDF, MD, HTML) or URL as source material
- [ ] Agent reads/fetches the source and identifies teachable concepts
- [ ] Generates a MAP.md with topic ordering derived from the document structure
- [ ] Lessons cite the source document (page numbers, sections) rather than web sources
- [ ] Works with the existing generate-topic pipeline (research phase reads the doc instead of web)
- [ ] Handles documents up to ~100 pages / 50K words (chunking strategy for longer)
- [ ] Quick mode: "quiz me on chapter 3" without generating full lessons

## Key architectural decisions (from research #135)

1. Hybrid chunking: headings first → normalize to 800-2000 words with 2-4 objectives
2. Fidelity split: lessons simplify for cognitive load, reference docs preserve source faithfully
3. Passage-level provenance: source_quote → objective → bloom_level → question
4. L1/L2/L3 stratification: core in lesson, practices in SR, conflicts gated by mastery
5. Raw source preserved immutably with JSON manifest for re-validation
6. Conflicts surfaced in reference docs and mastery-gated SR cards, not initial lessons
7. "Could They Answer This?" gate: every question must trace to a specific source passage
