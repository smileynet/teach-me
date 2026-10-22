---
id: "387"
title: "Teach: generative-media-pipelines / lora-and-the-training-tier"
status: open
blocked_by: ["367", "383"]
tags: ["content"]
---

# Teach: generative-media-pipelines / lora-and-the-training-tier

Generate the lesson for topic 7 (MAP id `01M2R98N1JAP32MK8W74HYM6M8`, lesson file
`07-lora-and-the-training-tier.html`, scope: substantial, prereqs: model-onboarding-as-data).
Produced via the `generate-topic` pipeline.

> **Refined 2026-09-17** from a per-topic research+review subagent. Findings:
> `.scratch/research/377-refine.md`.

## What to build

Frame the lesson around the **tier boundary**, NOT "how to train a LoRA" (a generic tutorial would
miss the point and duplicate the open web). The load-bearing, repo-grounded thesis:

1. **Hosted-not-trained, with per-platform file-path evidence.** None of the three serving platforms
   *trains* a LoRA — they *host* one. Lead with the "only hosts" citations: the ComfyUI platform (`loras` as a
   model-store category + SageMaker Model Package Group; `README.md` "fine-tuning is not in this
   platform"); the DCC service (training is a deferred "data flywheel" hook, ADR 0006 /
   `GLOSSARY.md`); the artist studio (`style_analyzer.py` style-via-prompt instead of training; every
   `lora`/`training` hit is vendored upstream). Keep **the real-time PoC as a one-line contrast only** (it
   trains, but that's world-model research, not media LoRA).
2. **The two training tiers the platforms defer to:** **SageMaker Training Jobs** (ephemeral,
   pay-per-use — the correct default for a single SDXL/FLUX LoRA) vs **HyperPod** (persistent,
   org-scale/continuous/foundation-model). Criterion: single adapter → job; persistent/multi-node/
   reserved-GPU → HyperPod. **HyperPod-for-one-LoRA is overkill** (the platform's own proposal admits
   a single-node job is cheaper). HyperPod Recipes = one config, both backends.
3. **When LoRA vs prompt — a decision callout with criteria (three rungs, cheapest first):** prompt
   engineering + style-via-prompt directive (the artist studio's ≤200-word vision-profiled directive) →
   reference-image conditioning (IP-Adapter, session-scoped, doesn't persist) → **train a LoRA**
   (distinctive, reusable, versioned asset). Rule: *escalate only when the cheaper rung plateaus.* A
   LoRA is an **asset** (persisted/versioned/hosted); a prompt/reference is a **session knob** — which
   is exactly why the platforms have a `loras` category but no trainer.

Also: technique mechanism (low-rank adapters on cross-attention; UNet for SD1.5/SDXL, DiT for
FLUX/SD3; 3–200 MB `.safetensors`); **instance sizing** (SDXL LoRA → `ml.g5` 24 GB; FLUX LoRA
rank-16 can exceed 40 GB → `ml.p4d/p5`); the **data-flywheel** pattern (serve→feedback→curate→
retrain→hot-swap) AND the honest gap that **no turnkey AWS *image* data-flywheel exists** (assembled
from parts; curation/scoring unresolved). style-via-prompt as the non-LoRA production alternative.

## G2 warnings (Con callouts, cited)

Overfitting/"overcooking" is the dominant failure (only works at one strength; fix: lower LR, more
diverse data, halve alpha); **dataset quality dominates, not resolution**; captioning errors silently
break trigger binding; FLUX LoRA is memory-heavy (rank-16 >40 GB — `ml.g5` OOMs); HyperPod-for-one-LoRA
cost mismatch; no turnkey AWS image data-flywheel; base-model license gate before training/hosting
(FLUX.1 [dev] gated + non-commercial; SDXL/schnell permissive).

## Honest gaps to state (don't paper over)

No turnkey AWS image data-flywheel; video-diffusion LoRA on AWS has no canonical tooling ("bring your
own diffusers/PEFT to a p5/HyperPod job").

## Source-verification gate (per #367)

Every "only hosts" claim → repo file path (the ComfyUI platform `README.md` + `cdk/lib/registry-stack.ts`;
the DCC service ADR 0006 / `GLOSSARY.md`; the artist studio `style_analyzer.py` + vendored-packages
note). Training-tier + technique facts → `[L#]` (AWS re:Post decision guide, HF diffusers, Kohya;
AIM205). No parametric memory.

## Artifact set (authoritative gate: `tools/check-topic-completeness.py`)

Lesson HTML at **flat** `library/generative-media-pipelines/lessons/07-lora-and-the-training-tier.html`;
reference; quiz (≥5/≥3); SR JSONL (≥1); **inline `glossary-data` block, not a JSON file**;
code-files dir only if `data-file` blocks exist. Follows `visual-teaching.md` +
`code-validation-teaching.md`.

## Acceptance criteria

- [ ] `library/generative-media-pipelines/lessons/07-lora-and-the-training-tier.html` generated via `generate-topic` (flat path)
- [ ] Hosted-not-trained thesis stated with a per-platform file-path citation table (the ComfyUI platform / the DCC service / the artist studio each shown to only host); the real-time PoC kept a one-line contrast
- [ ] Two-tier training decision (Training Jobs default for one LoRA vs HyperPod org-scale) with criteria + the HyperPod-for-one-LoRA-is-overkill warning + HyperPod Recipes bridge
- [ ] When-LoRA-vs-prompt decision callout: three-rung escalation (prompt/style-directive → reference-image → LoRA) with a default recommendation and asset-vs-session-knob framing
- [ ] Instance-sizing fact (SDXL→ml.g5 24GB; FLUX rank-16 >40GB→ml.p4d/p5) stated
- [ ] Data-flywheel pattern described AND the "no turnkey AWS image blueprint" gap stated honestly
- [ ] Warnings section: overfitting/overcooking + dataset-quality-over-resolution, each tied to a fix; style-via-prompt shown as the non-LoRA alternative (the artist studio)
- [ ] Reference + quiz (≥5/≥3) + SR JSONL + inline glossary produced; every claim cites a repo path or `[L#]`
- [ ] `mise run verify` passes AND `check-topic-completeness.py --workspace library/generative-media-pipelines --topic lora-and-the-training-tier` (and `--concepts`) clean
