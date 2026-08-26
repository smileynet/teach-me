---
id: "099"
title: "Convert quick-check.py (SR review) to Preact output"
type: feature
status: done
priority: medium
blocked_by: ["095"]
work_order: 5
tags: [platform]
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

- [x] Review page shows due cards one at a time
- [x] Click/tap reveals answer
- [x] Quality rating buttons record response
- [x] Progress shows cards remaining
- [x] Completion summary at end
- [x] Theme toggle works
- [x] Loads offline (vendored deps)

## Context & Sources

- **Pattern:** Data island (due cards JSON in page) — see `.scratch/research/python-to-preact-templating.md`
- **Helper:** `tools/lib/preact_page.py` — `render_page()` with SR card data
- **Current code:** `tools/quick-check.py` (397 lines) — generates vanilla HTML review page from due cards
- **SR engine:** `tools/sm2.py` — SM-2 algorithm, `tools/questions.py` — card/review data model
- **Components:** New `ReviewCard`, `QualityRating`, `ReviewDeck` in `assets/components/`
