---
id: "341"
title: "Enforce local-only learner progress in the shared repository"
status: done
priority: high
blocked_by: ["332", "338"]
type: fix
tags: ["arch-review", "platform"]
validation_criteria:
  - "Progress updates in every domain change only gitignored local overlay files"
  - "git status stays clean after local progress updates"
  - "Static deployment contains no .user directory or learner progress records"
---

# Enforce local-only learner progress in the shared repository

## Intent source

User decision, 2026-09-16: this is a shared repository. Users may persist progress locally,
but learner progress must never become durable repository content.

## Context

Read ADR 0012, ADR 0014, #255, #258, `tools/lib/overlay.py`, `.gitignore`, and
`tools/assemble-site.sh`. `demo-status.json` is showcase fixture data, not real progress.

## What to build

Make the local-only boundary executable and documented. Real progress and SR history persist
under gitignored user-local paths, work across every domain, remain out of committed generated
artifacts, and are stripped from static deployment output.

## Acceptance criteria

- [x] Progress and SR paths are documented as local-only user data
- [x] Every domain writes progress only beneath an ignored `.user/` root
- [x] `git status --short` stays empty after progress updates from a clean checkout
- [x] MAP.md, generated HTML, and demo fixtures never receive personal progress
- [x] Static assembly recursively excludes `.user/` and tests enforce it
- [x] Demo fixtures cannot be overwritten through learner-progress APIs
- [x] Reset/export behavior, if exposed, affects only local user state
- [x] `mise run verify` and `mise run site-dry-run` exit 0

## Out of scope

Shared team progress, cloud synchronization, accounts, authentication, and CRDTs.

## Resolution

The committed `learning-records/` question banks are now explicitly read-only fixtures.
`questions.py` reads a private topic copy when present and otherwise reads that fixture, but
all card creation, review scheduling, review logs, and lifecycle rewrites copy-on-write to
`.user/learning-records/`. The lifecycle tool no longer writes `QUESTIONS_DIR` directly.
Export remains read-only.

`library/README.md` now documents the public fixture versus private learner-state paths.
New tests prove reviews, appends, and lifecycle mutations leave their fixture byte-identical,
and create a temporary Git repository to prove a `.user` progress update leaves
`git status --short` empty. The tests run in the core verification gate. Existing map-page
and status API regressions cover the same no-personal-state rule for MAP/HTML/demo data.

Evidence: `mise run site-dry-run` → 12 deployment assertions including no `.user/` output;
`mise run verify` → 50 tests, 20 interactive checks, and 5 Ink transcripts pass (74.06s).
