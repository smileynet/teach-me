---
id: "343"
title: "Deep-dive the spaced-repetition state and scheduling architecture"
status: in_progress
priority: medium
blocked_by: ["341"]
type: research
tags: ["arch-review", "research"]
validation_criteria:
  - "Review maps every SR command and persisted field to its source of truth"
  - "Scheduler behavior is checked against authoritative sources and executable fixtures"
  - "Every confirmed gap has a focused follow-up ticket"
---

# Deep-dive the spaced-repetition state and scheduling architecture

## Intent source

Follow-up proposed by the 2026-09-16 architecture review and the shared-repository decision
that learner state remains local-only.

## What to review

Review-event history versus derived scheduling state; card identity across regeneration;
SM-2 calculations and grading semantics; leeches, suspension, reset, analytics, and Anki
export; `.user/learning-records` placement; and scheduler-version migrations.

## Context

Read `tools/sm2.py`, `tools/sr-*.py`, `tools/questions.py`, `tools/export_anki.py`, ADR
0012, #255, #170, and #172. Use primary literature and authoritative Anki/FSRS docs.

## Acceptance criteria

- [ ] A data-flow diagram identifies canonical events, derived state, exports, and resets
- [ ] Calculations and grade semantics are verified with executable fixtures
- [ ] Card identity behavior under wording edits is demonstrated
- [ ] Every SR command is checked against local-only repository invariants
- [ ] #170/#172 are reconciled with current architecture
- [ ] Confirmed gaps receive focused tickets; rejected changes include rationale

## Resolution

TBD
