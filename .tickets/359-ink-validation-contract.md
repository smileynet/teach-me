---
id: "359"
title: "Reconcile missing Ink validation skill contract"
status: open
priority: high
type: docs
blocked_by: ["335"]
tags: ["arch-review", "skills", "ink"]
validation_criteria:
  - "Every documented Ink validation route resolves to a maintained workflow"
---

# Reconcile missing Ink validation skill contract

## Intent

Reconcile the ticket and skill contract for Ink validation with the maintained `mise` workflows.

## Context

The skill deep dive found #200 claims a nonexistent `.kiro/skills/ink-validate/SKILL.md`; Git history offers no evidence it existed. Current steering and `mise run ink:validate`/`ink:validate-gd` provide the real path.

## What to build

Choose whether Ink validation needs a dedicated skill or should remain a scoped workflow in existing skills/steering, then correct all stale references and document responsibilities.

## Acceptance criteria

- [ ] #200 and project documentation no longer claim an unavailable skill.
- [ ] The maintained owner, commands, prerequisites, and strict/optional behavior are documented in one authoritative location.
- [ ] Relevant teaching/generation skills link to the validation contract without duplicating operational detail.
- [ ] A clean environment and an Ink fixture demonstrate the documented commands and expected skip/fail behavior.
