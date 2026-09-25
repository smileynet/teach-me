---
id: "384"
title: "Teach: generative-media-pipelines / the-async-contract"
status: open
blocked_by: ["367", "381"]
tags: ["content"]
---

# Teach: generative-media-pipelines / the-async-contract

Generate the lesson for topic 4 (MAP id `01M2R98N1JF95PJKCYR4JCKFK7`, lesson file
`04-the-async-contract.html`, scope: substantial, prereqs: the-universal-serving-pipeline).
Produced via the `generate-topic` pipeline.

> **Refined 2026-09-17** from a per-topic research+review subagent. Findings:
> `.scratch/research/374-refine.md`.

## What to build

Teach why inference is too slow for request/response, so every platform is **submit/status/stream**,
and why **idempotency (claim→commit, "work-done-wins") is where correctness lives.** Core beats:

1. **The universal contract:** submit (validate + enqueue + return job id; inputs as **S3
   references, never inline bytes**; optional `Idempotency-Key`) → authoritative status GET →
   progress stream. All three repos converge (REDACTED WS poll-then-WS; REDACTED SSE;
   REDACTED ComfyUI `/ws`).
2. **At-least-once delivery vs exactly-once EFFECT.** Distributed queues deliver at-least-once **by
   design** (SQS included) — chasing broker-level exactly-once is the classic wasted-effort
   anti-pattern. Correctness = an **idempotent handler**: stable key + atomic check-and-record,
   short-circuit BEFORE inference. Teach "exactly-once *effect* on at-least-once *delivery*", never
   "exactly-once delivery."
3. **Why a redelivered generative job must short-circuit before inference:** seeded/sampled models
   are non-deterministic, so re-running produces a *different* artifact — idempotency keys on the
   job id, not output comparison.
4. **The double-run failure mode with its concrete trigger:** visibility timeout shorter than
   worst-case processing (REDACTED's cold-start p95 **342s > 300s default**, `[L1]`
   spike) → redelivery + double-run; mitigate with the per-message heartbeat that extends
   visibility, and the rule **one liveness authority — never a reaper AND visibility recovery
   together** (`orchestrator/worker.py`, ADR 0007). Present the general "visibility > worst-case
   processing (≈6× rule of thumb)" separately with its external cite so the lesson doesn't overfit
   to one number.
5. **SSE vs WebSocket vs webhook — decision callout with criteria:** SSE = one-way progress off an
   authoritative store (REDACTED `generate.py`); WebSocket = bidirectional/interactive (REDACTED `/ws`,
   REDACTED events); webhook = terminal callback (SageMaker SNS notify). **Resumability
   is server-side, not transport-side** — `Last-Event-ID` reconnects the transport but loses
   generation state; poll-then-WS sends the authoritative snapshot first, then streams
   (`app.py:job_events`).

**SageMaker Async = the managed instance (framed "same shape, managed", NOT "use this instead"):**
S3-pointer in, immediate identifier + S3 output location, optional **SNS** success/error notify
(a terminal webhook, ≠ a per-stage progress stream), scale-to-zero, limits **1 GB payload / 1 hour**
`[L4:verified` https://docs.aws.amazon.com/sagemaker/latest/dg/async-inference.html`]`. State what
you give up (the double-run reasoning) and keep (idempotent handler on at-least-once).

## G2 warnings (Con callouts, cited)

Visibility-timeout-shorter-than-processing = guaranteed double-run; SQS delivers >once by design;
two recovery mechanisms at once double-run; non-deterministic processor + at-least-once ≠
at-most-once; SSE has no backpressure and loses state on drop; don't force broker exactly-once;
**ALB 60s idle-timeout kills long WS/SSE streams** (REDACTED set 3600s — cross-ref topic 5).

## Source-verification gate (per #367)

Every claim → repo file path (`orchestrator/app.py`/`store.py`/`worker.py`/`queue.py`;
`backend/routers/generate.py`/`services/async_jobs.py`) or `[L#]`; SageMaker limits cite the async
doc. External idempotency/transport sources tagged in the findings file.

## Artifact set (authoritative gate: `tools/check-topic-completeness.py`)

Lesson HTML at **flat** `library/generative-media-pipelines/lessons/04-the-async-contract.html`
(NOT a nested `lessons/<domain>/` path — checker globs one level); reference; quiz (≥5/≥3); SR JSONL
(≥1); **inline `glossary-data` block, not a JSON file**; code-files dir only if `data-file` blocks
exist. Follows `visual-teaching.md` + `code-validation-teaching.md`.

## Acceptance criteria

- [ ] `library/generative-media-pipelines/lessons/04-the-async-contract.html` generated via `generate-topic` (flat path)
- [ ] Distinguishes at-least-once delivery from exactly-once EFFECT; states correctness lives in an idempotent handler (stable key + atomic check-and-record), not the broker — with external cite + the work-done-wins repo cite
- [ ] Teaches the double-run trigger (visibility < worst-case processing; 342s>300s `[L1]`), the heartbeat mitigation, AND the one-liveness-authority rule
- [ ] Covers why a redelivered generative job short-circuits BEFORE inference (non-determinism)
- [ ] SSE-vs-WebSocket-vs-webhook decision callout grounded in the three repos, each with a when-to-use criterion; poll-then-WS explained as server-side authoritative state
- [ ] SageMaker Async framed as the managed instance (S3-pointer in, identifier+output location, SNS terminal notify, scale-to-zero, 1GB/1hr), "same shape managed" not "use instead", cited to the async doc
- [ ] Reference + quiz (≥5/≥3) + SR JSONL + inline glossary produced; every claim cites a repo path or `[L#]`
- [ ] `mise run verify` passes AND `check-topic-completeness.py --workspace library/generative-media-pipelines --topic the-async-contract` (and `--concepts`) clean
