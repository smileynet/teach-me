---
id: "342"
title: "Reconcile governing architecture documents with the shipped system"
status: open
priority: high
blocked_by: ["335"]
type: docs
tags: ["arch-review", "platform"]
validation_criteria:
  - "ui-contracts.md describes page-shell.js as implemented"
  - "map-format-spec.md documents ULIDs, typed edges, and no committed learner status"
  - "ADR 0014 and README describe the reconciled shared-library/local-state architecture"
---

# Reconcile governing architecture documents with the shipped system

## Problem

The UI spec calls `page-shell.js` unimplemented, the MAP spec embeds learner status and omits
the ULID/typed-edge schema, ADR 0014 remains proposed after implementation, and README blurs
the committed library with local workspace/state.

## Context

Read `.memory/specs/ui-contracts.md`, `.memory/map-format-spec.md`, ADRs 0012/0014/0016,
`README.md`, and #335. Reconcile ticket records first so docs cite honest as-built evidence.

## What to build

Establish one current description of committed shared content, immutable graph identity,
typed relationships, the implemented page shell, and local-only learner state.

## Acceptance criteria

- [ ] UI contracts describe the implemented page-shell interface
- [ ] MAP format matches `map_parser.py` for IDs, edges, prerequisites, and state exclusion
- [ ] ADR 0014 status is reconciled with an as-built note
- [ ] README distinguishes library, workspace, `.user` state, and demo fixtures
- [ ] No current document instructs users to commit learner progress
- [ ] Links resolve and `mise run verify` exits 0

## Resolution

TBD
