---
id: "377"
title: "Teach: generative-media-pipelines / lora-and-the-training-tier"
status: open
blocked_by: ["367", "373"]
tags: ["content"]
---

# Teach: generative-media-pipelines / lora-and-the-training-tier

Generate the lesson for topic 7 (MAP id `01M2R98N1JAP32MK8W74HYM6M8`, lesson file
`07-lora-and-the-training-tier.html`, scope: substantial, prereqs: model-onboarding-as-data).

## What to build

Teach the sharpest cross-platform finding: none of the serving platforms *train* LoRAs — they
*host* them, and training lives in a separate tier. This corrects the common assumption that a
serving platform trains. Cover LoRA-as-hosted-category, SageMaker Training Jobs (the default for
one SDXL/FLUX LoRA) vs HyperPod (org-scale), the data-flywheel pattern, and style-via-prompt as the
non-LoRA alternative.

Run `generate-topic`: research → lesson → post-process → verify.

## Source-verification gate (per #367)

- Claims → repo file path or `[L#]` source. Internal prior art (fine-tune-SDXL-with-Kohya IaC)
  cited where used. No parametric memory.
- Design source: `.memory/research/world-models-and-genmedia/02-generative-media-pipelines.md`
  + relevant `gap-research/*.md`.
- `mise run verify` clean.

## Acceptance criteria

- [ ] `library/generative-media-pipelines/lessons/generative-media-pipelines/07-lora-and-the-training-tier.html` generated
- [ ] LoRA-is-hosted-not-trained thesis landed; SageMaker Training Jobs vs HyperPod decision criteria given; data-flywheel + style-via-prompt covered
- [ ] Reference doc + quiz + SR cards + glossary JSON produced
- [ ] Every load-bearing claim cites a repo file path or `[L#]` source
- [ ] `mise run verify` passes; `check-topic-completeness.py` clean for this topic
