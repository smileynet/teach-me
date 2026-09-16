---
id: "343"
title: "Deep-dive the spaced-repetition state and scheduling architecture"
status: done
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

- [x] A data-flow diagram identifies canonical events, derived state, exports, and resets
- [x] Calculations and grade semantics are verified with executable fixtures
- [x] Card identity behavior under wording edits is demonstrated
- [x] Every SR command is checked against local-only repository invariants
- [x] #170/#172 are reconciled with current architecture
- [x] Confirmed gaps receive focused tickets; rejected changes include rationale

## Resolution

Completed the evidence-backed SR architecture review in `.scratch/research/343-sr-architecture.md`. It verifies the SM-2 implementation shape but documents the combined definition/state model, non-rebuildable review history, identity ambiguity, and unsupported analytics claims. Follow-up tickets #349–#352 capture the required split, event/projection model, reconciliation policy, and analytics repair; #341 remains the cross-cutting local-only boundary. Evidence: fixed-date scheduler fixtures and direct inspection of every SR command.
