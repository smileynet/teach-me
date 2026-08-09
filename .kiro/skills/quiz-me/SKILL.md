---
name: quiz-me
description: "Test my retention — quiz me on what I've learned so far. Trigger: quiz me, test me, check my understanding, what have I learned, review session."
metadata:
  type: process
  invocation: user-only
  practice: null
---

The user wants to test their retention. This is not a grilling session (plan-sharpening) — it is knowledge verification.

## SR-Powered Review Mode

If spaced repetition cards exist (`learning-records/questions/*.jsonl`), check what's due first:

```bash
python tools/sr-status.py          # quick health check
python tools/review.py             # list due cards
python tools/review.py <topic>     # filter to one topic
```

When cards are due, prefer surfacing them as conversational questions (the learner explains, you assess quality 0-5 and record via `review.py --review ID QUALITY`). This integrates naturally with the Socratic dialog below.

If the user asks to "review" or "practice" without specifying a topic, use due cards across all topics (interleaved). If they name a topic, filter to that topic.

## How to quiz

1. **Read the workspace state** — check `./learning-records/`, `./lessons/`, and `./reference/` to understand what the user has been taught.
2. **Pick the scope** — if the user named a topic or lesson, quiz on that. Otherwise, quiz across recent learning records — prioritise material that hasn't been tested yet.
3. **Ask in rounds** — 3-5 questions per round. Mix question types:
   - Recall (define X, what does Y do)
   - Application (given this situation, what would you do)
   - Discrimination (what's the difference between X and Y)
4. **Wait for answers** — don't reveal correct answers until the user responds.
5. **Give immediate feedback** — correct/incorrect, plus a one-line explanation citing the source.
6. **Record results** — if the user demonstrates solid understanding of something new, write a learning record. If they reveal a gap, note it in `NOTES.md` for the next lesson to address.

## Question design

- Each answer option should be the same length (no "longest answer is correct" tells)
- Randomise correct answer position
- Include plausible distractors drawn from adjacent concepts
- For application questions, use scenarios tied to the user's mission

## Source links on answers

Every answer (correct AND incorrect) should include links to authoritative sources. These help the learner verify and deepen understanding.

**Quality rules for source links:**
- Link to **specific page sections** (use #anchors when available), not top-level docs pages
- Each link must **directly help answer the question** — could someone read that section and determine why this answer is correct/incorrect?
- Prefer multiple targeted links over one generic one (e.g., both the Iceberg spec section AND the AWS implementation docs)
- Include a `section` note explaining what the linked page covers and why it's relevant
- **Never link to generic overviews** (e.g., "AWS S3 Documentation" home page) — find the specific subsection

**Format in HTML:**
```html
<div class="quiz-option"
  data-explanation="Why this is correct/incorrect."
  data-sources='[
    {"url":"https://...#section","label":"Source Name","section":"What this covers and why it matters"},
    {"url":"https://...#section","label":"Another Source","section":"Complementary perspective"}
  ]'>
  Answer text
</div>
```

## After the quiz

Summarise: what was solid, what needs review. Suggest whether the user is ready to advance or should revisit material.

## Gap-Discovered Cards

When the quiz reveals a concept the learner can't explain well, generate a spaced repetition card targeting that gap. These cards are personalized to the learner's actual confusion points — not assumed gaps.

### When to generate

- The learner gives a wrong or incomplete answer that reveals a conceptual gap (not just a memory lapse)
- The learner asks "wait, how does that work?" during feedback — they thought they understood but didn't
- The learner conflates two concepts that are importantly different

### How to generate

```python
from tools.questions import Card, append_card

card = Card(
    prompt="Explain why [concept the learner struggled with]",
    expected_answer="[The key insight they were missing]",
    question_type="explain",
    difficulty_tier="understand",
    lesson_id="quiz-session",  # or the lesson being quizzed on
    section_heading="",
    generated_by="quiz-skill",
    tags=["gap", "topic-tag"],
)
append_card("<topic-slug>", card)
```

### Rules

- **Only for genuine understanding gaps**, not memory lapses. If they knew it last week but forgot today, the existing card's SM-2 schedule handles that.
- **Frame the question around their specific confusion.** "Explain why X isn't the same as Y" is better than a generic question — it targets exactly where their model broke.
- **1-2 gap cards per quiz session maximum.** Don't overwhelm. The gaps become the focus of the next lesson naturally.
- **Note the gap in NOTES.md too** so the teach skill can address it in the next lesson.
