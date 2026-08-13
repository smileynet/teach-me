---
id: "099"
title: "Convert quick-check.py (SR review) to Preact output"
type: feature
status: open
priority: medium
blocked_by: ["095"]
work_order: 5
---

# Convert quick-check.py (SR review) to Preact output

## What to build

Spaced repetition quick-check review page as Preact — card flip interaction, quality rating buttons, progress through due deck.

## Deliverables

- Data island with due cards (prompt, answer, metadata)
- `ReviewCard` component: shows prompt, click to reveal answer
- `QualityRating` component: 1-5 rating buttons after reveal
- `ReviewDeck` component: manages card queue, progress, completion
- Signal state: current card, revealed, ratings history

## Acceptance Criteria

- [ ] Review page shows due cards one at a time
- [ ] Click/tap reveals answer
- [ ] Quality rating buttons record response
- [ ] Progress shows cards remaining
- [ ] Completion summary at end
- [ ] Theme toggle works
- [ ] Loads offline (vendored deps)
