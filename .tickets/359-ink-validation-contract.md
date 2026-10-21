---
id: "359"
title: "Reconcile missing Ink validation skill contract"
status: done
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

- [x] #200 and project documentation no longer claim an unavailable skill.
- [x] The maintained owner, commands, prerequisites, and strict/optional behavior are documented in one authoritative location.
- [x] Relevant teaching/generation skills link to the validation contract without duplicating operational detail.
- [x] A clean environment and an Ink fixture demonstrate the documented commands and expected skip/fail behavior.

## Resolution (2026-10-21)

Reconciled the phantom ink-validate skill. Corrected ticket 200 (strikethrough + note: no .kiro/skills/ink-validate/SKILL.md ever existed; Ink validation ships as scoped mise workflows). Made .kiro/steering/ink-authoring.md The validation pipeline the single authoritative contract: a table of 6 checks with command/owner/catches/blocks plus prerequisites (inklecate as a mise [tools] dep, Godot env-only, bink in .venv) and strict/optional behavior. generate-topic and teach SKILLs now link to it without duplicating detail. Fixed play-ink.py to SKIP unbound-EXTERNAL stories (covered by ink:validate-gd) mirroring capture/replay modes.

### Verification
1. ✓ Every documented Ink validation route resolves to a maintained workflow — "Every documented Ink validation route resolves to a maintained mise workflow: all 6 rows in the ink-authoring contract table map to real tasks (ink:validate, ink:validate:strict, ink:play, ink:transcripts, ink:validate-gd, check-lesson.py) confirmed via mise tasks; ink:validate PASSED 9 files 0 errors and ink:play showed documented SKIP on 07_state_bridge unbound-EXTERNAL (8 pass 1 skip 0 fail, exit 0)"
