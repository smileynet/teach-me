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

## Quiz from Source Section

When the user says "quiz me on chapter 3" or "test me on the auth section" and `source-chunks/{domain}.json` exists:

1. Run `python tools/match_section.py source-chunks/{domain}.json "chapter 3"` to find matching chunks
2. Read the matched chunk content — this is the material to quiz from
3. Ask 3-5 questions using the patterns below, drawn entirely from the matched content
4. Populate `source_section` and `source_page` when recording answers

This skips SR card lookup — it's immediate comprehension checking on material the learner just read. Frame it as "let's check if this landed" not as a test.

## How to quiz

1. **Read the workspace state** — check `./learning-records/`, `./lessons/`, and `./reference/` to understand what the user has been taught.
2. **Pick the scope** — if the user named a topic or lesson, quiz on that. Otherwise, quiz across recent learning records — prioritise material that hasn't been tested yet.
3. **Ask in rounds** — 3-5 questions per round. Ask conceptual questions (see below).
4. **Wait for answers** — don't reveal correct answers until the user responds.
5. **Evaluate against criteria, not exact wording** — check whether the learner's response hits the key relationship/mechanism. Multiple valid phrasings are expected. Don't penalize missing details that aren't central.
6. **Give immediate feedback** — acknowledge what they got right, clarify what they missed (one sentence), cite the source.
7. **Record results** — if the user demonstrates solid understanding of something new, write a learning record. If they reveal a gap, note it in `NOTES.md` for the next lesson to address.

## Question design

Questions should test whether the learner holds a working mental model — can they explain the concept, not recite it.

### Patterns to use

- **"Why does X work this way?"** — tests mechanism reasoning
- **"What would happen if [thing changed]?"** — tests prediction from model
- **"How would you explain [concept] to [person from their mission]?"** — tests articulation
- **"What's the difference between X and Y?"** — tests discrimination
- **"Your team is seeing [symptom]. What's likely happening?"** — tests real-world transfer

### Patterns to avoid

- "What is X?" / "Define X" — tests vocabulary, not understanding
- "List the N things that..." — tests enumeration, not structure
- "True or false: X" — too shallow, no retrieval effort
- Anything answerable by pattern-matching lesson wording

### Evaluating responses

When the learner answers, check for:
1. **Core idea present?** — Did they hit the essential relationship/mechanism?
2. **Reasoning sound?** — Can they explain WHY, not just WHAT?
3. **No major misconceptions?** — Are they conflating things that are importantly different?

If all three: strong response. If 1-2: partial, ask a follow-up to probe deeper. If none: the concept needs re-teaching.
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
    prompt="Why does [concept they conflated or missed] matter here?",
    expected_answer="Should mention: (1) [the key relationship they missed]. Bonus: [the distinction they conflated].",
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
