---
id: "394"
title: "world-models topic 6: serving-and-accelerators"
status: open
blocked_by: ["366", "392"]
priority: medium
validation_criteria:
  - "Lesson library/world-models/lessons/06-serving-and-accelerators.html generated via generate-topic; passes mise run verify"
  - "AWS-doc anchors (NxD Inference + NKI + SageMaker streaming) cited; the no-video-gen-doc gap stated honestly; every claim cited"
tags: ["content"]
---

# world-models topic 6: serving-and-accelerators

Author lesson 6 (final) of the **world-models** domain (setup: #366; prereq: #392). This is the
domain's **AWS-doc-anchored** topic (the SageMaker-Async analog for #367).

## What to build

Lesson `library/world-models/lessons/06-serving-and-accelerators.html` via `generate-topic`. Getting
a real-time world model to a player:
- The **accelerator reality**: Trainium/Neuron with **NKI** kernels, TP/CP parallel topology, the
  **bandwidth/launch-bound roofline** (RF ~4-6% MFU; fps wins came from launch-count reduction, not
  FLOPs).
- **Frame delivery** via streaming (SSE/WebSocket; SageMaker `InvokeEndpointWithResponseStream`).
- The **Decart** analog (Oasis/Mirage) and the Self-Forcing +
  step-distillation + WebRTC reference stack.

- **scope:** substantial · **prereqs:** [building-a-real-time-world-model] · **leads_to:** [generative-media-pipelines] · **lesson_file:** 06-serving-and-accelerators.html

## AWS-doc anchors (thread through — the gap research (non-public))

- **NxD Inference** (NeuronX Distributed): https://awsdocs-neuron.readthedocs-hosted.com/en/latest/libraries/nxd-inference/index.html — accelerator-native serving; TP/SP/CP config.
- **NKI programming guide**: https://awsdocs-neuron.readthedocs-hosted.com/en/latest/general/nki/ — the kernel lever (the real-time PoC's NKI kernels; Decart's mega-kernels).
- **SageMaker real-time + response streaming**: https://docs.aws.amazon.com/sagemaker/latest/dg/realtime-endpoints.html + `InvokeEndpointWithResponseStream`.
- **Pin Neuron doc URLs to a specific version at authoring** (`/en/latest/` churns per release).

## HONEST GAP — state it in the lesson

There is **no first-party AWS doc for real-time *video generation* on accelerators** — only
image-DiT blogs (PixArt-Σ/SDXL) and video *understanding* (not generation). Frame "real-time video
generation on Trainium" as **extrapolation** from DiT image serving + streaming delivery, not a
documented AWS workflow.

## Sources

- Design: research notes, non-public (Part 3 real-time serving).
- Backing: the gap research (non-public),
  the per-platform findings (non-public) (`docs/ROOFLINE_RF_1_3B.md`, `kernels/`).

## Acceptance criteria

- [ ] Lesson HTML generated; `mise run verify` passes
- [ ] AWS-doc anchors cited; version-pinned; the no-video-gen-doc gap stated honestly
- [ ] Exercise: "why did launch-count reduction move fps but a precision change didn't" (roofline reasoning)
- [ ] Glossary + SR cards produced; cross-link to the generative-media-pipelines domain (leads_to)
