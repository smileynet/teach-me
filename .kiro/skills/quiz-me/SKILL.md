---
name: quiz-me
description: "Test my retention — quiz me on what I've learned so far. Trigger: quiz me, test me, check my understanding, what have I learned, review session."
metadata:
  type: process
  invocation: user-only
  practice: null
---

The user wants to test their retention. This is not a grilling session (plan-sharpening) — it is knowledge verification.

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

## After the quiz

Summarise: what was solid, what needs review. Suggest whether the user is ready to advance or should revisit material.
