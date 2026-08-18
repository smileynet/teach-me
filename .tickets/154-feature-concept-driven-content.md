---
id: "154"
title: "Feature: concept extraction as input to glossary, quiz, and completeness checks"
status: open
blocked_by: ["149", "150"]
priority: medium
type: feature
---

# Feature: concept-driven content generation

## Problem

Currently, glossary term selection and question writing are fully LLM-driven with no programmatic input. The agent guesses which terms are domain-specific and which concepts deserve questions. This leads to:
- Inconsistent term coverage (some lessons over-annotate, others miss key terms)
- No structural signal for question difficulty stratification (L1/L2/L3)
- No way to verify completeness after generation ("did we cover all key concepts?")

## What to build

Use `extract_concepts.py` output (#149) to inform three existing processes:

### 1. Glossary seeding

Feed the generate-topic pipeline a candidate term list from YAKE extraction:
- Top N concepts per chunk → "these terms probably need glossary entries"
- Agent still decides definitions (creative work), but starts from a data-derived list
- Reduces missed terms and over-annotation

### 2. Question generation hints

Pass concept metadata to the question-writing step:
- **Foundational-ness score** → high-score concepts get L1 questions; low-score get L2/L3
- **Prerequisite edges** → suggest "explain why X depends on Y" framing
- **Defined-in vs used-in** → "explain X in context of Y" questions when concept spans chunks

### 3. Completeness verification

Post-generation check: does every concept above a threshold have:
- At least one glossary entry OR inline explanation?
- At least one SR question that tests it?
- A reference doc mention?

Report gaps as warnings (not blockers — some concepts are too minor to quiz on).

## Integration points

| Process | Current trigger | New input |
|---------|----------------|-----------|
| Jargon skill | Agent reads lesson, picks terms | Agent receives YAKE candidate list |
| generate-topic step 4 (SR questions) | Agent writes from lesson content | Agent receives concept scores + edges |
| check-topic-completeness.py | Checks file existence only | Also checks concept coverage |

## Acceptance criteria

- [ ] extract_concepts.py can run on lesson HTML content (not just PDF chunks)
- [ ] generate-topic skill receives concept list as context for jargon + questions
- [ ] check-topic-completeness.py reports concept coverage gaps
- [ ] Question L-level assignment correlates with foundational-ness score
- [ ] At least 80% of top-10 concepts per lesson have a glossary entry or question

## Non-goals

- Not replacing the agent's creative judgment — providing structured input
- Not requiring extract_concepts.py to run on every lesson (opt-in enrichment)
- Not changing the question/glossary format — same JSONL + glossary-data JSON
