---
id: "349"
title: "Separate committed card definitions from local learner state"
status: done
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

- [x] Reviewing, suspending, resetting, retiring, or generating local learning state never writes to a committed question-bank path.
- [x] A new or empty local overlay still exposes all committed card definitions.
- [x] Local state is keyed by stable card ID and contains no duplicated card content unless explicitly justified by a migration record.
- [x] Existing learner state is migrated without silently losing review history or due dates.
- [x] `sr`, `sr:review`, lifecycle commands, quick-check, and Anki export use the same definition/state boundary.
- [x] Regression tests prove a clean Git worktree after review and lifecycle operations.

## Resolution

Committed question JSONL files are now definition-only: the legacy `schedule`, `suspended`,
and `mastered` fields were removed from all eight shipped banks. Learner state lives in the
ignored `.user/learning-records/card-state.json` document as `{card_id: {schedule,
suspended, mastered}}`. `read_cards()` joins public/private definitions with that state, so
an empty local overlay cannot hide the public library. Reviews and lifecycle operations now
write state only; local generated cards are private definitions without state fields.

Legacy full-card private copies from the prior copy-on-write implementation migrate per topic:
their schedule/lifecycle fields move into `card-state.json`, public definitions reappear, and
private-only definitions are retained in definition-only form. The migration record in the
state document prevents repeated conversion.

Evidence: focused SR-state tests cover review, lifecycle, empty-overlay visibility, migration,
definition-only storage, and a clean temporary Git worktree; `mise run verify` → 52 tests,
20 interactive checks, and 5 Ink transcripts pass (76.09s).
