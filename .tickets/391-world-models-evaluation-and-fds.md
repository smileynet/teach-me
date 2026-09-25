---
id: "391"
title: "world-models topic 3: evaluation-and-fds"
status: open
blocked_by: ["366", "389"]
priority: medium
validation_criteria:
  - "Lesson library/world-models/lessons/03-evaluation-and-fds.html generated via generate-topic; passes mise run verify"
  - "FDS defined EXACTLY as verified (1 - action_F1, project-coined, NOT Frechet/FVD); every claim cited"
tags: ["content"]
---

# world-models topic 3: evaluation-and-fds

Author lesson 3 — the intellectual core of the **world-models** domain (setup: #366; prereq: #389).

## What to build

Lesson `library/world-models/lessons/03-evaluation-and-fds.html` via `generate-topic`. Teaches:
- Why visual metrics lie (the **ranking reversal**).
- **Engine-as-oracle**: games give deterministic, bit-reproducible ground truth robotics can't.
- The **FDS four axes**: visual (PSNR/LPIPS, reported-not-trusted), behavioral (IDM round-trip),
  drift-over-horizon `h*`, action-sensitivity guard.
- Situated against prior art: FVD/CD-FVD and the IDM-round-trip lineage (VPT→Genie→RLIR); FDS is
  the repo's instantiation of an established family, complementary to FVD.

- **scope:** deep · **prereqs:** [what-is-a-world-model] · **lesson_file:** 03-evaluation-and-fds.html

## VERIFIED FACTS — hold these exactly (source-verification pass, gap-research/366-source-verification.md)

- Behavioral FDS = **`1 - action_F1`** (`world-models/tools/fds_harness.py:202-203`) — macro-F1 over
  discrete action channels via IDM round-trip (`:94-133`). It is a **project-coined score, NOT a
  Fréchet distance, and NOT FVD**. Do not describe it with Fréchet/Gaussian/covariance machinery.
- `camera_l1` is reported but **NOT folded into the trusted FDS scalar** — don't imply it is.
- Interpretation context for the lesson: IDM needs ≥128 frames (32-frame clips give F1≈0 even on
  real data); recorded ceilings ~0.457 dense / ~0.196 sparse; the 0.2 retrain threshold lives in
  the proposal, not the harness.

## Sources

- Design: `01-world-models.md` (Part 1 "FDS four axes" + Part 3 prior-art).
- Backing: `repo-findings/world-models.md`, `gap-research/{world-model-eval-prior-art,366-source-verification}.md`.

## Acceptance criteria

- [ ] Lesson HTML generated; `mise run verify` passes
- [ ] FDS defined exactly as verified above (reviewer confirms no Fréchet/FVD conflation)
- [ ] Exercise: "a model wins LPIPS but the world ignores WASD — which axis catches it and why"
- [ ] Glossary + SR cards produced
