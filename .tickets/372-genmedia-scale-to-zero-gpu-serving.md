---
id: "372"
title: "Teach: generative-media-pipelines / scale-to-zero-gpu-serving"
status: open
blocked_by: ["367", "371"]
tags: ["content"]
---

# Teach: generative-media-pipelines / scale-to-zero-gpu-serving

Generate the lesson for topic 2 (MAP id `01M2R98N1J0D5K8T3HW95QFKB9`, lesson file
`02-scale-to-zero-gpu-serving.html`, scope: **deep**, prereqs: the-universal-serving-pipeline).

## What to build

Teach why GPUs scale to zero (the economic heart) and cold start as the tax. Cover the four
AWS-native paths — SageMaker Async, Inference-Component `minCopies=0`, Serverless (CPU-only), EKS
Karpenter+KEDA — plus Bedrock; the measured cold-start SLO (~342s scale-from-zero vs ~150s
warm-pool); and why the hand-rolled orchestrators re-implement SageMaker Async / the EKS reference
architecture. **SageMaker Asynchronous Inference is the worked reference example** threaded through
the track — introduce it here as the managed mirror of REDACTED's hand-rolled
SQS+worker orchestrator (queues requests, scales instances to zero, pay only while processing).

Run `generate-topic`: research → lesson → post-process → verify.

## Source-verification gate (per #367)

- Claims → repo file path or `[L#]` source. Cold-start numbers cite
  `REDACTED/.memory/spikes/02-cold-start-comparison.md`.
- SageMaker Async: cite https://docs.aws.amazon.com/sagemaker/latest/dg/async-inference.html
- Design source: `.memory/research/world-models-and-genmedia/02-generative-media-pipelines.md`
  + relevant `gap-research/*.md` (AWS scale-to-zero decision guide).
- `mise run verify` clean.

## Acceptance criteria

- [ ] `library/generative-media-pipelines/lessons/generative-media-pipelines/02-scale-to-zero-gpu-serving.html` generated
- [ ] Four AWS-native scale-to-zero paths + Bedrock covered with when-to-use decision criteria
- [ ] SageMaker Async introduced as the worked managed reference; cold-start SLO cited with source
- [ ] Reference doc + quiz + SR cards + glossary JSON produced
- [ ] Every load-bearing claim cites a repo file path or `[L#]` source
- [ ] `mise run verify` passes; `check-topic-completeness.py` clean for this topic
