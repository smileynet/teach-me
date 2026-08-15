---
id: "113"
title: "Feature: ELI5 mode for quiz answers"
status: done
blocked_by: []
---

# Feature: ELI5 mode for quiz answers

## What to build

When a quiz answer is revealed (either after the user responds or on demand), offer an "Explain like I'm five" toggle/button that generates a simplified, plain-language version of the criteria-based answer. The current answers are written for someone who already understands the domain — ELI5 mode rephrases using analogies, simpler vocabulary, and shorter sentences for when the concept hasn't clicked yet.

## Acceptance criteria

- [x] Quiz answer reveal includes an ELI5 button/toggle — DIVERGED: implemented as always-visible "Another angle" callout (no toggle — research showed always-visible is better UX)
- [x] ELI5 text uses analogies and avoids jargon (or defines it inline)
- [ ] Works on both the interactive quiz page and SR review cards — quiz only; SR review deferred
- [x] ELI5 explanations are generated alongside criteria answers (or on-demand via server) — pre-generated in JSONL `eli5` field
- [x] Doesn't replace the full answer — shown in addition to it
