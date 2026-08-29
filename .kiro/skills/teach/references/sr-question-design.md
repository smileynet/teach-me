# SR Question Design (teach skill)

After writing a lesson, generate spaced-repetition questions that test **conceptual
understanding** — can the learner explain the idea, not recite details.

## The design rules live in one place

Archetypes, criteria format, `eli5`/another-angle, provenance & level tagging, interactive
question types, and difficulty ordering are the **single owner**:
[../../generate-topic/references/sr-question-authoring.md](../../generate-topic/references/sr-question-authoring.md).
Follow it for WHAT to write and HOW to structure each card (including the per-topic count).
This file covers only what's specific to the teach skill's programmatic path.

## Core principle

Questions require the learner to **reconstruct reasoning from their mental model**. Each
targets one relationship. Think "tomographic cuts" — collectively they trace the model's
edges. Test the model, not the words; one relationship per card; include one
mission-scenario question; understand the concept before encoding it.

## How to generate (the teach skill's `Card` API)

```python
from tools.questions import Card, append_card

card = Card(
    prompt="Why does Iceberg need a manifest list layer?",
    expected_answer="Should mention: (1) groups manifests atomically per snapshot, (2) catalog points to one list, not N manifests. Bonus: enables snapshot isolation.",
    question_type="explain",
    lesson_id="0001-iceberg-metadata-tree",
    tags=["iceberg", "metadata"],
)
append_card(card, domain="data-engineering")
```

(`generate-topic` appends JSONL directly instead of using this API — both produce the same
card shape defined by the single owner above.)
