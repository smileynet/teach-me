---
id: "149"
title: "Spike: YAKE + regex for concept extraction and dependency detection from chunks"
status: done
blocked_by: []
tags: [source-ingest]
---

# Spike: concept extraction and dependency detection

## Question to answer

Can lightweight NLP (YAKE keywords + regex pattern matching) extract enough concept/dependency signal to build meaningful prerequisite edges — without heavy ML models?

## Approach

**Concept extraction (YAKE):**
- Run YAKE on each chunk → top N keywords per section
- Compare keywords across chunks → identify shared concepts
- "Foundational-ness" score: frequency × how early it appears

**Dependency detection (regex):**
- Forward reference patterns: "see §X", "as described in chapter N", "requires X"
- First-mention heuristic: term defined in chunk A, used without definition in chunk B → B depends on A
- Co-occurrence: terms that always appear together indicate related concepts

**Test corpus:** chunk_pdf.py output from Five Lines of Code + Software Mistakes

## Evaluation

| Metric | Target |
|--------|--------|
| Key concepts extracted per chapter | 5-10 meaningful terms |
| False positive rate (non-concepts) | <30% |
| Forward references detected | >80% of explicit ones |
| First-mention dependencies | Reasonable (manual review) |

## Acceptance criteria

- [x] YAKE extracts meaningful concepts from technical PDF chunks
- [x] Regex catches explicit forward/backward references
- [x] First-mention heuristic produces plausible prerequisite edges
- [x] Working script with NetworkX graph output
- [x] Dependency weight: yake + networkx only (no torch, no spacy required)

## Result

**Answer: Yes.** YAKE + regex + first-mention provides solid concept/dependency signal without heavy ML. Implementation: `tools/extract_concepts.py`.

**Performance on test fixtures:**
- Tutorial doc (10 chunks): 75 concepts, 13 explicit refs, 17 first-mention edges
- Reference doc (11 chunks): 68 concepts, 0 explicit refs (correct), 33 first-mention edges from shared "socket" term
- Foundational-ness scoring correctly identifies "socket" (0.818) and "batch processing" (0.200) as top concepts

**Dependencies:** yake (0.7.3) + networkx only. No torch, no spacy. Total install: 4 packages (jellyfish, segtok, tabulate, yake).

**27 pytest tests pass.** Validates keywords, explicit refs, first-mention edges, scoring, serialization.
