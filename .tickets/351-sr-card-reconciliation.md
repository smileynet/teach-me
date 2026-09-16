---
id: "351"
title: "Define stable card identity across edits and regeneration"
status: open
priority: medium
type: design
blocked_by: ["349"]
tags: ["arch-review", "sr", "identity"]
validation_criteria:
  - "Editing a public card has deliberate, testable effects on a learner schedule"
---

# Define stable card identity across edits and regeneration

## Intent

Define how authored card changes preserve, supersede, or retire learner state instead of relying on blind JSONL append behavior.

## Context

Current UUID card IDs and append-only generation make equivalent regenerated cards duplicate and reset schedules, while retaining IDs silently changes content under existing schedules. The TF-IDF work in #170 must remain advisory rather than an automatic mutator.

## What to build

Specify and implement explicit authoring operations for retain, in-place edit, replacement/supersession, retirement, deletion, and move between topics.

## Acceptance criteria

- [ ] The contract distinguishes retained IDs, content edits, replacements, retirements, deletions, and topic moves.
- [ ] Each operation documents and implements its learner-state, event-history, and Anki-export effect.
- [ ] Generation detects duplicate IDs and does not silently append equivalent cards.
- [ ] Supersession is explicit and leaves an auditable relationship rather than silently resetting review state.
- [ ] TF-IDF similarity can advise an author but never automatically merges or mutates cards.
- [ ] Regression fixtures cover all supported reconciliation paths.
