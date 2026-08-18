---
id: "149"
title: "Spike: YAKE + regex for concept extraction and dependency detection from chunks"
status: open
blocked_by: ["138"]
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

- [ ] YAKE extracts meaningful concepts from technical PDF chunks
- [ ] Regex catches explicit forward/backward references
- [ ] First-mention heuristic produces plausible prerequisite edges
- [ ] Working script with NetworkX graph output
- [ ] Dependency weight: yake + networkx only (no torch, no spacy required)
