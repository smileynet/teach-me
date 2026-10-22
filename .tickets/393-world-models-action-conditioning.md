---
id: "393"
title: "world-models topic 5: action-conditioning"
status: open
blocked_by: ["366", "392"]
priority: medium
validation_criteria:
  - "Lesson library/world-models/lessons/05-action-conditioning.html generated via generate-topic; passes mise run verify"
  - "The DMD-is-action-invariant + gated-module + supervised-term story stated as verified; every claim cited"
tags: ["content"]
---

# world-models topic 5: action-conditioning

Author lesson 5 of the **world-models** domain (setup: #366; prereq: #392 building-a-real-time-world-model).

## What to build

Lesson `library/world-models/lessons/05-action-conditioning.html` via `generate-topic`. The subtle
part everyone gets wrong:
- Why a DMD-distilled model is **action-invariant by construction** (added action inputs measure
  0.000 effect).
- The fix: small **gated action modules** (zero-init gate — start as a no-op, learn to un-gate)
  plus a **supervised next-frame flow-matching term** on real (latent, action) pairs.
- Why a **LoRA-on-attention variant was counterproductive** (degraded to "a grainy blob") and is
  disabled.
- Coarse temporal granularity (one action vector per ~21-frame segment).

- **scope:** substantial · **prereqs:** [building-a-real-time-world-model] · **lesson_file:** 05-action-conditioning.html

## Sources

- Design: research notes, non-public (Part 1 "Action steering").
- Backing: the per-platform findings (non-public)
  (`gpu/action_causal_model.py`, `training/model/action_dmd.py`).

## Acceptance criteria

- [ ] Lesson HTML generated; `mise run verify` passes
- [ ] Source-verification gate satisfied
- [ ] Exercise (misconception probe): "a colleague added an action input to a DMD model and it had
      zero effect — why, and what's the fix?"
- [ ] Glossary + SR cards produced
