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
Produced via the `generate-topic` pipeline (research → generate → post-process → verify).

> **Refined 2026-09-17** from a per-topic research+review subagent. Findings:
> `.scratch/research/372-refine.md` (cold-start numbers verified against the cited spike).

## What to build

Teach scale-to-zero as the **economic heart** of the design and cold start as the tax. Three arcs:

1. **The four AWS-native scale-to-zero paths** + Bedrock, each with *when-to-use* criteria, and map
   each repo onto its path: SageMaker **Inference Components `minCopies=0`**; **SageMaker Async**
   (managed queue + scale-to-zero — the worked reference, = REDACTED's whole hand-rolled
   SQS+worker); **Serverless** (CPU-only — a trap for GPU work); **EKS Karpenter+KEDA** (= REDACTED);
   plus Bedrock.
2. **Cold start as a MEASURED SLO** — p95 **342s scale-from-zero vs 150s warm-pool**, with the
   per-phase breakdown showing **docker image pull dominates (p95 137s, ~40%)**, while model load
   (~30s) and inference (~5s) are cheap-and-fixed. This inverts the naive intuition (which fears
   weight-loading). Cite `REDACTED/.memory/spikes/02-cold-start-comparison.md`; state
   the percentile.
3. **Mitigation levers, separated by which phase they attack** — image-pull levers (SOCI *with its
   ML caveat*, slim images, Container Caching, Dragonfly) vs weight-load levers (Fast Model Loader
   S3→accelerator, weights-out-of-image) — each with its honest limit.

Also: **weights never baked into the image** (S3→NVMe / FSxN+FlexClone / HF-direct-pull, tied to
*why* — keeps the pull tax bounded); capacity as a first-class problem (diversified EC2 Fleet vs
single-type droughts; ODCR solves retention not acquisition; 2026 managed Capacity-Aware Inference).

**Honest asymmetry (per topic-1 discipline):** the three repos are NOT all "true zero" — REDACTED runs
a warm pod (KEDA `minReplicaCount 1`), REDACTED offers both as a config dial, only
SageMaker Async / Bedrock are literal-zero-idle. Teach the dial, not "everyone scales to zero."
Pin in the glossary that `minReplicaCount`/`minCopies`/`MinCapacity` are three provider names for
the same "floor" dial.

## G2 warnings (must appear as gotcha/Con callouts, each with the concrete failure + fix)

- SageMaker Async needs the **`HasBacklogWithoutCapacity`** step policy or a lone sub-target request
  queues forever; async cold-start-from-zero can hit ~20 min for a large image.
- **SOCI is weak specifically for ML** (inference reads most of the image); it defers cost to first
  request and shifts failure semantics.
- **Keep 1–2 warm for interactive, true-zero for batch** (why REDACTED chose `minReplicaCount 1`);
  guard scale-in against in-flight work ("scaled to zero mid-decode").
- **Serverless is CPU-only** — a dead end for diffusion/LLM GPUs.
- **SQS-visibility double-run**: cold-start p95 (342s) > 300s default visibility → redelivery;
  extend via heartbeat, and never run BOTH a reaper AND visibility recovery.

## Scope boundary

The universal loop is topic 1 (reference, don't re-teach). Weight-staging *mechanics* are shared
with topic 3 — cross-reference. This topic owns the scale-to-zero economics + cold-start SLO +
mitigation.

## Source-verification gate (per #367)

Every load-bearing claim → repo file path or `[L#:confidence]` external source (per
`source-authority`). Design source `.memory/research/world-models-and-genmedia/02-generative-media-pipelines.md`
+ `gap-research/scale-to-zero-gpu-serving.md`; external best-practice/anti-pattern set in
`.scratch/research/372-refine.md` (four-paths docs, SOCI/Fast Model Loader, the G2 reposts). No
parametric memory.

## Artifact set (authoritative gate: `tools/check-topic-completeness.py`)

Lesson HTML at **flat** `library/generative-media-pipelines/lessons/02-scale-to-zero-gpu-serving.html`
(checker globs `lessons/*.html` at one level — a nested `lessons/<domain>/` path is silently
missed); reference doc; quiz (≥5 cards, ≥3 types); SR JSONL (≥1 card); **inline
`<script id="glossary-data">` block, NOT a separate JSON file**; code-files dir only if `data-file`
blocks exist. Follows `visual-teaching.md` + `code-validation-teaching.md` (narrative framing,
decision "when to use which" callouts, WCAG SVG, `var(--svg-*)`, prose-check pass).

## Acceptance criteria

- [ ] `library/generative-media-pipelines/lessons/02-scale-to-zero-gpu-serving.html` generated via `generate-topic` (flat path)
- [ ] Four AWS-native paths (IC `minCopies=0`, Async, Serverless-CPU-only, EKS Karpenter+KEDA) + Bedrock, each with when-to-use criteria, and each repo mapped onto its path
- [ ] Cold start taught as a measured SLO with the per-phase breakdown (docker pull dominates, p95 137s/~40%; load ~30s, infer ~5s cheap-and-fixed), cited to the spike file
- [ ] Every G2 warning has a gotcha callout with concrete failure + fix (HasBacklogWithoutCapacity; SOCI-weak-for-ML; keep-warm-for-interactive; scaled-to-zero-mid-decode; Serverless CPU-only; SQS double-run)
- [ ] Mitigation levers distinguished by phase (image-pull vs weight-load), each with its honest limit; "weights never in image" stated with all three staging strategies
- [ ] Honest asymmetry preserved (warm-pod floor vs true zero); the three floor-dial names pinned in the glossary
- [ ] Reference + quiz (≥5/≥3) + SR JSONL + inline glossary produced; every claim cites a repo path or `[L#]`
- [ ] `mise run verify` passes AND `check-topic-completeness.py --workspace library/generative-media-pipelines --topic scale-to-zero-gpu-serving` (and `--concepts`) clean
