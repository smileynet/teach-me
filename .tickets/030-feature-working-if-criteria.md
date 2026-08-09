---
id: "030"
title: "Feature: 'it's working if' success criteria for teach skill"
status: open
priority: high
blocked_by: ["028", "029"]
type: feature
---

# Feature: "it's working if" success criteria

## What to build

Add explicit success criteria to the teach skill — observable indicators that the system is functioning well, grounded in the JTBD: "I need to understand this well enough to do my job."

## The JTBD lens

The learner isn't studying for a test. They're learning while delivering. Success = they can have the conversations at work, make the decisions, and advise the teams. The system should optimize for that.

## Proposed criteria

### It's working if:

- First action in an empty workspace is a mission interview — the agent won't teach without knowing WHY
- RESOURCES.md fills before lessons — agent researches, then teaches from sources
- Every lesson cites sources — no teaching from parametric memory
- Lessons give one tangible win tied to the mission — not abstract knowledge for its own sake
- The Socratic gate simulates conversations the learner will actually have at work
- Learning records capture what was *demonstrated*, not just what was *covered*
- Reference docs are scannable at work — a colleague could use one without context
- The glossary defines terms the learner doesn't know (not ones they obviously do)
- Sessions resume from workspace state — the folder is the continuity
- After 3+ lessons, the agent adapts to demonstrated level (doesn't re-explain mastered concepts)

### It's NOT working if:

- The agent produces a lesson without being asked about the mission
- Lessons teach from "what the model knows" without citing sources
- The learner can say "next lesson" without any demonstration of understanding
- Reference docs read like shorter lessons (narrative) instead of compressed lookup artifacts
- The gate asks recall questions ("name the layers") instead of application questions ("explain to a skeptical engineer why...")
- Every lesson re-explains concepts the learner has already demonstrated mastery of
- The workspace accumulates files but the learner can't do their job any better

## Acceptance criteria

- [ ] "It's working if" section added to teach skill
- [ ] Criteria grounded in JTBD, not in skill mechanics
- [ ] "It's NOT working if" anti-patterns documented
- [ ] Criteria are observable (you can tell from the workspace state and dialog)
