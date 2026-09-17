---
id: "374"
title: "Teach: generative-media-pipelines / the-async-contract"
status: open
blocked_by: ["367", "371"]
tags: ["content"]
---

# Teach: generative-media-pipelines / the-async-contract

Generate the lesson for topic 4 (MAP id `01M2R98N1JF95PJKCYR4JCKFK7`, lesson file
`04-the-async-contract.html`, scope: substantial, prereqs: the-universal-serving-pipeline).

## What to build

Teach why inference is too slow for request/response, so every platform is submit/status/stream —
and why getting idempotency right is where correctness lives. Cover submit/status/progress, SSE vs
WebSocket, poll-then-WS resume, and the claim→commit "work-done-wins" contract (and why a naive
reaper + visibility recovery would double-run jobs). Ground the hand-rolled contracts against
**SageMaker Async as the managed instance of the same shape**: S3-pointer input (never inline
bytes), an immediate identifier + S3 output location, optional SNS success/error notification, up
to 1 GB payloads and 1-hour jobs.

Run `generate-topic`: research → lesson → post-process → verify.

## Source-verification gate (per #367)

- Claims → repo file path or `[L#]` source. SageMaker Async payload/duration limits cite
  https://docs.aws.amazon.com/sagemaker/latest/dg/async-inference.html
- Design source: `.memory/research/world-models-and-genmedia/02-generative-media-pipelines.md`.
- `mise run verify` clean.

## Acceptance criteria

- [ ] `library/generative-media-pipelines/lessons/generative-media-pipelines/04-the-async-contract.html` generated
- [ ] Submit/status/progress + SSE-vs-WebSocket + poll-then-WS-resume covered; claim→commit idempotency explained with the double-run failure mode
- [ ] SageMaker Async framed as the managed instance (S3-pointer in, identifier + output location, SNS notify, limits)
- [ ] Reference doc + quiz + SR cards + glossary JSON produced
- [ ] Every load-bearing claim cites a repo file path or `[L#]` source
- [ ] `mise run verify` passes; `check-topic-completeness.py` clean for this topic
