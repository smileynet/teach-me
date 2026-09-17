---
id: "375"
title: "Teach: generative-media-pipelines / comfyui-at-scale"
status: open
blocked_by: ["367", "373", "374"]
tags: ["content"]
---

# Teach: generative-media-pipelines / comfyui-at-scale

Generate the lesson for topic 5 (MAP id `01M2R98N1JSSGZ9GTRY1P5YZDT`, lesson file
`05-comfyui-at-scale.html`, scope: substantial, prereqs: model-onboarding-as-data +
the-async-contract). Produced via the `generate-topic` pipeline.

> **Refined 2026-09-17** from a per-topic research+review subagent. Findings:
> `.scratch/research/375-refine.md`.

## What to build

Teach ComfyUI as a single-process node-graph engine that ships a full HTTP+WebSocket API, and the
specific traps of hosting it as a service. The through-line: **decouple ingest from GPU work** —
stateless gateway validates+enqueues, version-pinned GPU workers drain the queue, outputs to object
storage. Beats:

1. **Headless API loop:** `POST /prompt` (API-format JSON) → `prompt_id`; `/ws` typed progress
   (completion = `executing` with null node); `GET /history/{id}` → outputs; `GET /view` → download.
   Treat **`/object_info` as the platform-defining route** (runtime node-schema discovery) — it's
   what makes ComfyUI programmable, not a footnote. Call out **API-format vs UI-format JSON** (the UI
   graph won't POST to `/prompt`) as an immediate gotcha.
2. **Two execution surfaces from one container image + model library:** headless-batch on EKS
   (the async API loop) vs the full ComfyUI **UI streamed via AppStream** (interactive artists, Okta
   SAML, one GPU/session); name the **router** that dispatches by tier.
3. **Workflow-as-immutable-container versioning:** git→build→scan→**approval gate**→immutable ECR
   tag; weights never in the image; SHA-pin ComfyUI + custom nodes. The version-mixing bug it
   prevents (`latest` on a multi-replica fleet silently changes sampler seeding → non-reproducible).

## G2 warnings (Con callouts with source — all three are load-bearing)

- **ALB 60s idle-timeout drops the `/ws` progress socket** on long generations — fix: raise idle
  timeout (REDACTED 3600s; AWS ECS sample 300s+) **and/or** WebSocket ping/pong ≤58s (note the
  exactly-at-timeout race). Cross-vendor confirmed.
- **No-auth = RCE surface.** Core ComfyUI has no built-in auth; custom nodes are arbitrary Python
  (supply-chain + RCE). Never internet-facing; auth-gate at the edge; **allowlist custom-node class
  names before enqueue**; cap workflow payload size. (Internal Critical finding.)
- **One-process-one-workflow.** ComfyUI serializes on one GPU; scale by adding whole pods, not
  concurrency → sticky sessions + `Recreate` deploy + one GPU/node. Round-robin without stickiness
  sends a status poll to the wrong worker.

Also: cold checkpoint load dominates first-request latency (REDACTED ~15 min fresh vs ~182s warm).

## Provenance paragraph (MANDATORY — keep REDACTED and aws-samples distinct)

The lesson **must** state: `REDACTED` did NOT surface in REDACTED (likely a
private REDACTED package), explored directly by symlink — its facts are `[L1]` first-party
observation of *that specific repo*. The three **`aws-samples`** reference architectures
(`comfyui-on-eks`, `cost-effective-aws-deployment-of-comfyui`, `sample-comfy-to-sagemaker-processing-job`)
are **PUBLIC, INDEPENDENT prior art** — NOT descriptions of, derived from, or claims about REDACTED.
Where they agree (ALB timeout, no-auth, S3→node weights, SHA pinning) that is **convergent evidence
for the pattern**, not shared lineage. Never let the prose blur "REDACTED did X" with "aws-samples does X".

## Honest scope (per topic-1 asymmetry discipline)

REDACTED's ONLY live generative pipeline is **image→3D mesh (GLB)** via TRELLIS.2; text→image
(z_image_turbo) and Hunyuan3D-2 are staged-not-wired; video/audio/speech absent. Don't present
staged/proposed capabilities as shipped. REDACTED's KEDA `minReplicaCount 1` is a **warm-pod floor, not
literal zero** (weekend "park" is the true-zero path); the aws-samples EKS/ECS shapes DO scale to
literal zero — keep the distinction explicit. Surface two open questions (custom-node supply-chain
vetting; approved model-artifact provenance path) rather than glossing.

## Source-verification gate (per #367)

Every claim → repo file path (`docs/VISION.md`, `k8s/ingress/comfy-alb.yaml`,
`k8s/keda/comfy-scaledobject.yaml`, `containers/*/Dockerfile`, `lambda/router/index.ts`,
`cdk/lib/*-stack.ts`) or `[L#]`; aws-samples cited as external `[L4]` with their repo URLs, kept
distinct from REDACTED.

## Artifact set (authoritative gate: `tools/check-topic-completeness.py`)

Lesson HTML at **flat** `library/generative-media-pipelines/lessons/05-comfyui-at-scale.html`;
reference; quiz (≥5/≥3); SR JSONL (≥1); **inline `glossary-data` block, not a JSON file**;
code-files dir only if `data-file` blocks exist. Follows `visual-teaching.md` +
`code-validation-teaching.md`.

## Acceptance criteria

- [ ] `library/generative-media-pipelines/lessons/05-comfyui-at-scale.html` generated via `generate-topic` (flat path)
- [ ] Four headless routes pinned with roles + `/object_info` treated as the platform-discovery route; API-format-vs-UI-format gotcha called out
- [ ] Two execution surfaces (headless EKS vs AppStream UI) as one image+library, with the router that dispatches by tier
- [ ] All three G2 warnings in Con callouts with source (ALB `/ws` idle-timeout + fix; no-auth RCE + node allowlist + never-internet-facing; one-process-one-workflow → sticky sessions/Recreate/one-GPU)
- [ ] Workflow-as-immutable-container versioning explained (git→build→scan→approve→immutable tag; SHA-pin; weights not in image) + the version-mixing bug
- [ ] **Explicit provenance paragraph**: REDACTED = private/first-party-observed; aws-samples = independent public prior art; convergence ≠ shared lineage
- [ ] Media-type reality honest (image→3D live; text→image staged; video/audio/speech absent); warm-pod-floor vs literal-zero distinction stated
- [ ] Reference + quiz (≥5/≥3) + SR JSONL + inline glossary produced; every claim cites a repo path or `[L#]`
- [ ] `mise run verify` passes AND `check-topic-completeness.py --workspace library/generative-media-pipelines --topic comfyui-at-scale` (and `--concepts`) clean
