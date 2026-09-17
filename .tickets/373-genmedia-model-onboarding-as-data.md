---
id: "373"
title: "Teach: generative-media-pipelines / model-onboarding-as-data"
status: open
blocked_by: ["367", "371"]
tags: ["content"]
---

# Teach: generative-media-pipelines / model-onboarding-as-data

Generate the lesson for topic 3 (MAP id `01M2R98N1JH2ACGN90N90CR7A3`, lesson file
`03-model-onboarding-as-data.html`, scope: **deep**, prereqs: the-universal-serving-pipeline).

## What to build

Teach why adding a model must not mean adding an endpoint or bespoke serving code — the property
that lets one platform serve many models. Cover the manifest/registry (REDACTED), the
universal data-driven inference handler + format families (REDACTED), the versioned
workflow-container (REDACTED); the rule-of-two seam; runner strategies (native/comfyui/mock); and why
weights are never baked into the image — S3→NVMe vs FSxN+FlexClone vs HF-direct-pull, NF4/offload.
(Weights-storage mechanics were merged into this topic + topic 2 per #367 spine v2.)

Run `generate-topic`: research → lesson → post-process → verify.

## Source-verification gate (per #367)

- Claims → repo file path or `[L#]` source. No parametric memory.
- Design source: `.memory/research/world-models-and-genmedia/02-generative-media-pipelines.md`.
  Backing: `repo-findings/{REDACTED,REDACTED,REDACTED}.md`.
- `mise run verify` clean.

## Acceptance criteria

- [ ] `library/generative-media-pipelines/lessons/generative-media-pipelines/03-model-onboarding-as-data.html` generated
- [ ] Manifest/registry vs data-driven handler vs workflow-container contrasted across the three platforms; rule-of-two seam explained
- [ ] Weights-never-baked covered (S3→NVMe / FSxN+FlexClone / HF-direct-pull, NF4/offload)
- [ ] Reference doc + quiz + SR cards + glossary JSON produced
- [ ] Every load-bearing claim cites a repo file path or `[L#]` source
- [ ] `mise run verify` passes; `check-topic-completeness.py` clean for this topic
