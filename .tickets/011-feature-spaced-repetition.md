---
id: "011"
title: "Feature: quiz question bank for spaced repetition (post-MVP)"
status: done
priority: low
blocked_by: []
type: feature
tags: [platform]
---

# Feature: quiz question bank for spaced repetition

## Post-MVP — build after core teaching flow is proven

## What to build

Generate and store quiz questions in a structured format (JSON) so they can be surfaced later for spaced repetition review. Questions are authored during lesson creation and augmented by the quiz-me skill when it discovers understanding gaps.

## Research findings (2026-08-09)

### Algorithm recommendation: SM-2 now, FSRS later

Start with **SM-2** (~50 LOC, no dependencies, deterministic, 37 years of validation). Migrate to **FSRS** once enough review history accumulates (20-30% fewer reviews for same retention, but needs history to optimize parameters).

**SM-2 core state per card:** `repetitions`, `ease_factor` (≥1.3, starts 2.5), `interval` (days).
**FSRS migration path:** store review history from day one so FSRS can be trained later without losing data.

Leitner is too crude (fixed buckets, no per-card adaptation). Skip it.

### Question design principles (from research)

1. **SRS retains but doesn't teach.** Cards only work AFTER initial understanding. Never generate review cards for material the learner hasn't demonstrated comprehension of (the Socratic gate already ensures this).
2. **"Explain to a colleague why..." > recognition/recall.** Free recall questions (explain, compare, apply) produce stronger retention than cloze or multiple-choice.
3. **One concept per card** (Wozniak's minimum information principle). Complex cards have high failure rates and teach frustration, not knowledge.
4. **3-5 new cards per lesson maximum.** Review overload kills compliance. At our lesson cadence (~every few days), this means ~1-2 new cards/day effective rate.
5. **Track response time** as a secondary signal — a correct answer after 60 seconds of thought ≠ one in 2 seconds.

### Integration pattern (dual source)

**Source 1 — teach skill generates seed questions:**
- 3-5 questions per lesson, targeting key concepts
- Prefer relationship questions ("why does X require Y?") over isolated facts
- Include one "apply to your mission scenario" question per lesson
- Write to `learning-records/questions/lesson-NNN.json`

**Source 2 — quiz-me skill fills gaps:**
- When Socratic dialog reveals a gap, that gap becomes a new SR card
- Questions personalized to the learner's specific confusion points
- Appends to the same question bank with `generated_by: "quiz-skill"` provenance

### Data format

```json
{
  "id": "uuid-v4",
  "version": 1,
  "content": {
    "type": "explain|compare|apply|predict",
    "prompt": "Explain to a colleague why Iceberg uses manifest files instead of listing all data files in the catalog.",
    "expected_answer": "Manifest files allow atomic operations on large file sets without locking the catalog. The catalog only points to the current manifest list, enabling snapshot isolation.",
    "difficulty_tier": "understand"
  },
  "provenance": {
    "lesson_id": "0001-iceberg-metadata-tree",
    "section_heading": "Metadata Tree",
    "generated_by": "teach-skill",
    "generated_at": "2026-08-09T00:00:00Z"
  },
  "schedule": {
    "algorithm": "sm2",
    "interval_days": 1,
    "ease_factor": 2.5,
    "repetitions": 0,
    "due_date": "2026-08-10",
    "last_reviewed": null,
    "last_quality": null
  },
  "review_history": [],
  "tags": ["iceberg", "metadata-layer", "manifest"]
}
```

### File organization

```
learning-records/
  questions/
    lesson-0001.json    # Questions from lesson 1 (array of cards)
    lesson-0002.json    # Questions from lesson 2
  reviews.jsonl         # Append-only review events (for future FSRS training)
```

### Known pitfalls to avoid

| Pitfall | Mitigation |
|---------|-----------|
| Ease factor death spiral (SM-2) | Floor ease at 1.3; consider periodic reset for chronic-lapse cards |
| Cards disconnected from context | Always store provenance; link back to lesson section |
| Lesson updated but cards stale | Flag cards whose source section was modified; offer regeneration |
| Returning after long absence | Batch overdue reviews by priority; don't punish ease for the gap |
| Testing recognition not understanding | Default to "explain why" format; avoid multiple-choice |
| Review pile grows unbounded | Cap active cards; graduate cards with interval >6 months |

### Prior art (most relevant to teach-me)

| Project | Key lesson for us |
|---------|-----------------|
| **Orbit** (Matuschak) | Embedded-in-prose model; questions appear in reading context. Most relevant architecture for our approach. |
| **Anki** | Don't fragment into sub-decks (kills interleaving). 20 new/day max even for dedicated study. |
| **SuperMemo** | "Twenty rules of formulating knowledge" — minimum information principle is non-negotiable. |
| **Obsidian SR plugin** | Reviews entire notes, not just cards — maintaining conceptual models alongside facts. |
| **Quantum Country** | Proved that embedded SRS prompts dramatically improve long-term retention over reading alone. |

### Sources

- [SM-2 algorithm](https://github.com/cnnrhill/sm-2) — reference implementation
- [FSRS in 100 lines](https://borretti.me/article/implementing-fsrs-in-100-lines) — migration target
- [FSRS benchmark](https://github.com/open-spaced-repetition/fsrs-benchmark) — 20-30% improvement data
- [Gwern: Spaced Repetition](https://gwern.net/spaced-repetition) — comprehensive literature review
- [Matuschak: How to write good prompts](https://andymatuschak.org/prompts/) — question design
- [Orbit source](https://github.com/andymatuschak/orbit) — embedded SRS architecture
- [SuperMemo Twenty Rules](https://www.supermemo.com/en/blog/twenty-rules-of-formulating-knowledge)

## Acceptance criteria

- [x] SM-2 scheduler implemented (~50 LOC, in `tools/` or `assets/`)
- [x] teach skill generates 3-5 questions per lesson in structured JSON
- [x] Questions use explain-to-colleague format (not recognition/recall)
- [x] quiz-me skill can append gap-discovered cards to the bank
- [x] Review mode surfaces due cards weighted by SM-2 schedule
- [x] Review history stored as JSONL (future FSRS training data)
- [x] Provenance tracked: which lesson/section generated each card
- [x] Cap of 5 new cards per lesson enforced
- [x] Cards with interval >6 months graduated to "mastered" (no further review)
- [x] Graceful handling of returning-after-absence (batch overdue, don't punish ease)

## Resolution (2026-08-09)

Implemented as three modules in `tools/`:
- `sm2.py` — SM-2 scheduling algorithm (pure functions, no dependencies)
- `questions.py` — JSONL card storage per topic + review log
- `review.py` — CLI for due cards, stats, and recording reviews

Skills updated:
- `teach` — generates 3-5 SR questions per lesson
- `quiz-me` — appends gap-discovered cards when understanding gaps emerge
