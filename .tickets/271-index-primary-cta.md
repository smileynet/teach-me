---
id: "271"
title: "Index UX: add 'what's next' / primary-action guidance for first-time users"
status: open
blocked_by: []
priority: low
tags: ["platform"]
---

# Index primary-action guidance

## Why (found in UX audit, 2026-08-29)

The All Lessons index shows 5 domain cards with no orientation — a first-time user gets no
answer to "what do I do here / where do I start" (learning-UX principle #3: always-answered
"what's next", exactly one obvious primary CTA per screen). Cards are the only affordance.

## What to build

- Add a one-line orientation under the summary ("Pick a domain to start" / "New here? Start
  with X"), or a recommended-next affordance (e.g. highlight the domain with in-progress
  topics, or the first not-started root). Keep it minimal — one line, not a wizard.
- Optionally surface an aggregate "resume" when overlay progress exists (a domain has
  in-progress topics → "Continue: {domain}"). Overlay-derived (reuse status_map).

## Acceptance criteria

- [ ] Index shows a single, clear primary-action / orientation cue for a first-time user
- [ ] When progress exists, a "continue where you left off" affordance appears (overlay-driven)
- [ ] Does not clutter the dashboard (one line / one highlighted card, not a banner stack)
- [ ] `mise run verify` EXIT 0

## Validation

Load index fresh (empty overlay) → orientation cue present. Mark a topic in-progress →
"continue" affordance appears pointing at that domain.
