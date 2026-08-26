---
id: "030"
title: "Feature: 'it's working if' system performance criteria"
status: done
priority: high
blocked_by: ["028", "029"]
type: feature
tags: [platform]
---

# Feature: "it's working if" system performance criteria

## Context

Pocock's teach skill documentation includes explicit "It's working if" criteria — observable indicators that the system is functioning correctly. These serve two purposes: (1) the skill author can validate the implementation, (2) the user can diagnose when something is off.

We need the same, but grounded in our JTBD: "learn well enough to do my job (architect, advise, explain to teams)." Our criteria should be observable from workspace state and dialog patterns — not self-reported satisfaction.

## Intent

This is a self-evaluation rubric for the teach-me system. Like "It's working if" in Pocock's docs, these criteria tell you whether the system is healthy by looking at its outputs and behaviors. The gate dialog evaluates the *learner*. This evaluates the *system*.

The criteria should be:
- **Observable** — you can verify them from files, dialog transcripts, or workspace state
- **Grounded in JTBD** — tied to "can the learner do their job better?" not "did the skill run correctly?"
- **Actionable** — when a criterion fails, you know what to fix

## What to build

Add an "It's working if" section to the teach skill, followed by "It's NOT working if" anti-patterns.

### Proposed system performance criteria

**It's working if:**

1. First action in an empty workspace is a mission interview — the agent won't teach without knowing WHY the learner needs this
2. RESOURCES.md populates before lessons — the agent researches from real sources, then teaches from what it found
3. Claims in lessons carry citations — a lesson with no links out is teaching from memory
4. Each lesson gives one tangible win tied to the mission — not abstract knowledge untethered from the learner's actual work
5. The gate dialog feels like rehearsing a work conversation — the learner leaves feeling "I could actually say that in a meeting"
6. Learning records capture what was *demonstrated*, not just what was *covered* — and later lessons build on that foundation
7. Reference docs are useful standalone — the learner pulls them up in an architecture review and they help
8. Opening a fresh session and saying "next lesson" continues where it left off — the folder is the continuity
9. The glossary annotates terms the learner doesn't know and skips ones they obviously do
10. A question that needs real-world judgment gets pointed to a community or resource, not just answered

**It's NOT working if:**

1. It produces a lesson before understanding why the learner cares
2. Lessons cite no sources — the agent is teaching from parametric memory
3. The learner can say "next lesson" without any demonstration of understanding
4. Reference docs read like shorter lessons (narrative) instead of scannable lookup artifacts
5. The gate asks "what is X?" instead of "explain to [someone from your mission] why..."
6. Every lesson re-explains concepts the learner has already demonstrated mastery of
7. The workspace accumulates files but the learner can't have better conversations at work

## Validation

- [x] Each "working if" criterion is testable against the Iceberg workspace (our test fixture)
- [x] Criteria don't overlap with gate evaluation (system vs learner is a clean split)
- [x] Anti-patterns point to a specific fix (not just "it's bad")
- [x] A new contributor reading the criteria would know what quality looks like

## Acceptance criteria

- [x] "It's working if" section added to teach skill (7-10 positive criteria)
- [x] "It's NOT working if" section added (5-7 anti-patterns)
- [x] Each criterion is observable without asking the learner to self-report
- [x] Each anti-pattern names what to fix
- [x] Reviewed against current Iceberg workspace to confirm: does lesson 1 pass these criteria?
