---
id: "349"
title: "Separate committed card definitions from local learner state"
status: in_progress
priority: high
type: refactor
blocked_by: ["341"]
tags: ["arch-review", "sr", "privacy"]
validation_criteria:
  - "Reviewing a card never changes a committed question bank"
  - "An empty local store still exposes every committed card definition"
---

# Separate committed card definitions from local learner state

## Intent

Keep shareable card definitions in version control while keeping every learner's schedule and lifecycle state in a local-only overlay.

## Context

The SR deep dive found that `tools/lib/questions.py` mixes definitions with mutable schedule state and falls back to a committed `learning-records/` path. This violates the local-progress boundary in #341 and hides public definitions when an empty local store exists. Card IDs are not graph ULIDs; preserve that distinction.

## What to build

Define a public definition format and a local state format keyed by canonical card ID. Load the effective review view by joining them without copying definitions into learner storage. Migrate existing local state safely and make all SR commands use the new boundary.

## Acceptance criteria

- [ ] Reviewing, suspending, resetting, retiring, or generating local learning state never writes to a committed question-bank path.
- [ ] A new or empty local overlay still exposes all committed card definitions.
- [ ] Local state is keyed by stable card ID and contains no duplicated card content unless explicitly justified by a migration record.
- [ ] Existing learner state is migrated without silently losing review history or due dates.
- [ ] `sr`, `sr:review`, lifecycle commands, quick-check, and Anki export use the same definition/state boundary.
- [ ] Regression tests prove a clean Git worktree after review and lifecycle operations.
