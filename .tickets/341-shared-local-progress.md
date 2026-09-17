---
id: "341"
title: "Enforce local-only learner progress in the shared repository"
status: in_progress
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

- [ ] Progress and SR paths are documented as local-only user data
- [ ] Every domain writes progress only beneath an ignored `.user/` root
- [ ] `git status --short` stays empty after progress updates from a clean checkout
- [ ] MAP.md, generated HTML, and demo fixtures never receive personal progress
- [ ] Static assembly recursively excludes `.user/` and tests enforce it
- [ ] Demo fixtures cannot be overwritten through learner-progress APIs
- [ ] Reset/export behavior, if exposed, affects only local user state
- [ ] `mise run verify` and `mise run site-dry-run` exit 0

## Out of scope

Shared team progress, cloud synchronization, accounts, authentication, and CRDTs.

## Resolution

TBD
