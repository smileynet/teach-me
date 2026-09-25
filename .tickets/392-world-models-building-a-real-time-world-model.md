---
id: "392"
title: "world-models topic 4: building-a-real-time-world-model"
status: open
blocked_by: ["366", "389"]
priority: medium
validation_criteria:
  - "Lesson library/world-models/lessons/04-building-a-real-time-world-model.html generated via generate-topic; passes mise run verify"
  - "Model lineage + fps stated exactly as verified (RF=Wan2.1-1.3B; ~14fps = RF offline on Trn2); every claim cited"
tags: ["content"]
---

# world-models topic 4: building-a-real-time-world-model

Author lesson 4 of the **world-models** domain (setup: #366; prereq: #389).

## What to build

Lesson `library/world-models/lessons/04-building-a-real-time-world-model.html` via `generate-topic`.
Teaches how the generator works, from the REDACTED PoC:
- Causal video **DiT** (Wan2.1-T2V-1.3B) + **rectified flow / flow matching**.
- **Rolling Forcing**: denoise a rolling window + an **attention-sink anchor block** + a streaming
  KV cache — the real-time, low-drift trick.
- **DMD distillation** to a few denoising steps (data-free; tracked by the gradient norm, not the
  loss value).

- **scope:** deep · **prereqs:** [what-is-a-world-model] · **lesson_file:** 04-building-a-real-time-world-model.html

## VERIFIED FACTS — hold these exactly (gap-research/366-source-verification.md)

- **RF = Wan2.1-T2V-1.3B** (~4 fps interactive); **Matrix-Game-3.0 = Wan2.2-5B** (~17 fps, 4×H100).
  Keep them distinct.
- The **"~14 fps" figure = RF offline on Trainium2** (TP4×CP4=16 cores, 480×640, 5 denoise steps,
  `VERIFIED_14FPS_BASELINE.md`) — NOT the interactive demo, NOT MG3.
- **Do not claim Trn2-vs-GPU parity** — the source doesn't state it. RF "runs on Trainium OR NVIDIA
  GPU" but no comparative fps is given.
- A DMD student only predicts accurate x0 at the noise levels it was distilled on (the T=5→T=4
  re-distill caveat) — don't imply you can just shorten the step list.

## Sources

- Design: `01-world-models.md` (Part 1 "The generator side").
- Backing: `repo-findings/REDACTED.md`, `gap-research/{realtime-worldmodel-serving,366-source-verification}.md`.

## Acceptance criteria

- [ ] Lesson HTML generated; `mise run verify` passes
- [ ] Lineage + fps stated exactly as verified (reviewer confirms RF/MG3 not conflated, no parity claim)
- [ ] Exercise: near-transfer on why Rolling Forcing suppresses drift vs. naive frame-by-frame
- [ ] Glossary + SR cards produced
