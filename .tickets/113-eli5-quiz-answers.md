---
id: "113"
title: "Feature: ELI5 mode for quiz answers"
status: open
blocked_by: []
---

# Feature: ELI5 mode for quiz answers

## What to build

When a quiz answer is revealed (either after the user responds or on demand), offer an "Explain like I'm five" toggle/button that generates a simplified, plain-language version of the criteria-based answer. The current answers are written for someone who already understands the domain — ELI5 mode rephrases using analogies, simpler vocabulary, and shorter sentences for when the concept hasn't clicked yet.

## Acceptance criteria

- [ ] Quiz answer reveal includes an ELI5 button/toggle
- [ ] ELI5 text uses analogies and avoids jargon (or defines it inline)
- [ ] Works on both the interactive quiz page and SR review cards
- [ ] ELI5 explanations are generated alongside criteria answers (or on-demand via server)
- [ ] Doesn't replace the full answer — shown in addition to it
