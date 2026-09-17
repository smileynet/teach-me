---
domain: world-models
description: "Interactive, action-steered environment simulation: what world models are, the architecture landscape, how you evaluate them (behavioral vs visual / the FDS harness), and how a real-time video-diffusion world model is built (causal DiT, Rolling Forcing, DMD) and served on AWS Trainium"
generated: 2026-09-17
depth: 0
parent: null
leads_to: [generative-media-pipelines]
---

# World Models — Building and Evaluating Interactive Environment Simulators

## Orientation

A world model generates an explorable environment frame-by-frame in response to actions, instead
of rendering from a fixed engine. Two real efforts frame the whole track: a benchmark that scores
whether a model actually *plays* correctly (the FDS harness in the `world-models` repo) and a
browser-playable real-time video-diffusion generator on AWS Trainium (`delirium-world-models-poc`,
a fork of TencentARC Rolling Forcing). The field's central failure is the "vivid dream" — a model
that looks photoreal while ignoring the player — so the track gives *evaluation* equal weight with
*generation*. It teaches what world models are, the architecture landscape, how to evaluate them
(the behavioral axis that separates play from look), how a real-time one is built (causal DiT +
rectified flow, Rolling Forcing, DMD distillation), how action conditioning is grafted on, and how
it's served on accelerators. It's architecture-first and source-grounded: every claim cites the two
repos or `[L#:confidence]` prior art, and serving anchors to AWS Neuron/SageMaker docs. Serving a
world model is itself a generative-media-pipeline problem, so this domain `leads_to` that one.

## Topics

### what-is-a-world-model
- **id:** 01M2RB7H6QXKJCYZJPF73E56R0
- **title:** What Is a World Model?
- **why:** The whole track rests on one distinction: a world model is *action-conditioned, over-time steerable* simulation — not a video generator (fixed clip) and not a hand-coded engine. Establishes the vocabulary (state, action, rollout, drift) and names the "vivid dream" failure the rest of the track exists to detect and fix.
- **scope:** substantial
- **prereqs:** []
- **lesson_file:** 01-what-is-a-world-model.html

### the-landscape
- **id:** 01M2RB7H6Q8SRH0ZKZV5AT6SWW
- **title:** The World-Model Landscape
- **why:** Situates the field so the learner can place any new model. Covers the six-way architecture taxonomy (video-latent, 3D-native, hybrid engine+model, latent-dynamics RL, JEPA, action-foundation) and the AWS-deployability tiers (self-hostable / walled / API-only), with named examples (Genie, Cosmos, Oasis, Dreamer, V-JEPA).
- **scope:** substantial
- **prereqs:** [what-is-a-world-model]
- **lesson_file:** 02-the-landscape.html

### evaluation-and-fds
- **id:** 01M2RB7H6Q4WPV2ZN5C9NVJSDH
- **title:** Evaluation — Behavioral vs Visual (the FDS Harness)
- **why:** The intellectual core. Why visual metrics lie (the ranking reversal); engine-as-oracle (games give deterministic, bit-reproducible ground truth robotics can't); the FDS four axes — visual (PSNR/LPIPS, reported-not-trusted), behavioral (IDM round-trip; **behavioral FDS = `1 - action_F1`**, a project-coined score, NOT a Fréchet distance and NOT FVD), drift-over-horizon `h*`, and the action-sensitivity guard. Situated against prior art: FVD/CD-FVD and the IDM-round-trip lineage (VPT→Genie→RLIR), where FDS is the repo's instantiation of an established family, complementary to FVD.
- **scope:** deep
- **prereqs:** [what-is-a-world-model]
- **lesson_file:** 03-evaluation-and-fds.html

### building-a-real-time-world-model
- **id:** 01M2RB7H6QV3NSZ97PRYRX4FD6
- **title:** Building a Real-Time World Model
- **why:** How the generator actually works, from the delirium PoC. Causal video DiT (Wan2.1-T2V-1.3B) + rectified flow / flow matching; Rolling Forcing (denoise a rolling window + an attention-sink anchor block + a streaming KV cache) as the real-time, low-drift trick; DMD distillation to a few denoising steps (data-free, tracked by the gradient norm not the loss). Grounds the "~14 fps" figure precisely: RF-1.3B offline on Trainium2, not the interactive demo and not the 5B Matrix-Game-3.0.
- **scope:** deep
- **prereqs:** [what-is-a-world-model]
- **lesson_file:** 04-building-a-real-time-world-model.html

### action-conditioning
- **id:** 01M2RB7H6QG1488ZG78SXMVNJC
- **title:** Action Conditioning
- **why:** The subtle part everyone gets wrong. Why a DMD-distilled model is action-invariant by construction (added action inputs measure 0.000 effect); the fix — small gated action modules (zero-init gate: start as a no-op, learn to un-gate) plus a supervised next-frame flow-matching term on real (latent, action) pairs; why a LoRA-on-attention variant was counterproductive (degraded to "a grainy blob") and disabled; coarse temporal granularity (one action vector per ~21-frame segment).
- **scope:** substantial
- **prereqs:** [building-a-real-time-world-model]
- **lesson_file:** 05-action-conditioning.html

### serving-and-accelerators
- **id:** 01M2RB7H6QKCKES7E5RDVWVF9Z
- **title:** Serving & Accelerators
- **why:** Getting a real-time world model to a player. The accelerator reality — Trainium/Neuron with NKI kernels, TP/CP parallel topology, the bandwidth/launch-bound roofline (RF sits at ~4-6% MFU; fps wins came from launch-count reduction, not FLOPs) — anchored to the **NxD Inference** and **NKI** AWS docs. Frame delivery via streaming (SSE/WebSocket; SageMaker `InvokeEndpointWithResponseStream`). The internal Decart analog (NKI mega-kernels, ~25 fps on Trn3) and the Self-Forcing + step-distillation + WebRTC reference stack. Honest gap: no first-party AWS doc for real-time *video generation* exists — it's extrapolation from DiT image serving + streaming delivery.
- **scope:** substantial
- **prereqs:** [building-a-real-time-world-model]
- **leads_to:** [generative-media-pipelines]
