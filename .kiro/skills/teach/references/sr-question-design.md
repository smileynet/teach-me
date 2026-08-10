# SR Question Design

After writing a lesson, generate 3-5 spaced repetition questions. These test **conceptual understanding** — can the learner explain the idea, not recite details.

## Core principle

Questions require the learner to **reconstruct reasoning from their mental model**. Each targets one relationship. Think "tomographic cuts" — collectively they trace the model's edges.

## How to generate

```python
from tools.questions import Card, append_card

card = Card(
    prompt="Why does Iceberg need a manifest list layer?",
    expected_answer="Should mention: (1) groups manifests atomically per snapshot, (2) catalog points to one list, not N manifests. Bonus: enables snapshot isolation.",
    question_type="explain",
    lesson_id="0001-iceberg-metadata-tree",
    tags=["iceberg", "metadata"],
)
append_card("iceberg-on-aws", card)
```

## Question patterns

| Pattern | Tests | Example |
|---------|-------|---------|
| "Why does X work this way?" | Mechanism | "Why use a tree instead of listing?" |
| "What would happen if..." | Prediction | "What if you skip compaction?" |
| "When would you choose X over Y?" | Transfer | "When does hidden partitioning win?" |
| "How is X different from Y?" | Discrimination | "CoW vs in-place update?" |
| "Your team hits [scenario]..." | Real-world | "Query is slow on 10M files. What's likely?" |
| "What problem does X solve?" | Purpose | "What breaks without isolation?" |

## Expected answer format

Criteria to check against — NOT scripts to reproduce:

```
Should mention: (1) [key idea], (2) [key relationship].
Bonus: [deeper insight].
```

## What NOT to ask

- Definition parroting ("What is X?")
- Yes/no questions
- Enumeration ("List the layers")
- Compound questions (two in one)
- Questions answerable by pattern-matching lesson text

## Rules

- One relationship per card
- 3-5 cards per lesson maximum
- Test the model, not the words
- Include one mission-scenario question
- Understand before encoding (only for concepts already taught)
