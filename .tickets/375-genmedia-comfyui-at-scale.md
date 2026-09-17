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
the-async-contract).

## What to build

Teach ComfyUI as the de-facto node-graph substrate for generative workflows and the specific traps
of hosting it as a service. Cover the headless API (`/prompt` → prompt_id, `/ws` progress,
`/history`, `/object_info` introspection), headless-batch vs streamed-UI (AppStream), the three
AWS reference samples, the ALB WebSocket idle-timeout trap, workflow-as-immutable-container
versioning, and the no-auth security surface.

**Source note (carry from #367):** `REDACTED` did not surface in REDACTED
(likely a private REDACTED package). The AWS reference-sample content (`aws-samples/comfyui-on-eks`
etc.) is independently-verified prior art — NOT a claim about that specific repo. Keep the two
distinct in the lesson.

Run `generate-topic`: research → lesson → post-process → verify.

## Source-verification gate (per #367)

- Claims → repo file path or `[L#]` source. AWS reference samples cited as external `[L#]`, kept
  distinct from the (unverifiable-in-search) REDACTED package.
- Security surface (no-auth ComfyUI) flagged with the source-authority security posture.
- `mise run verify` clean.

## Acceptance criteria

- [ ] `library/generative-media-pipelines/lessons/generative-media-pipelines/05-comfyui-at-scale.html` generated
- [ ] Headless API endpoints + headless-vs-streamed-UI covered; ALB WebSocket trap + workflow-as-container versioning + no-auth risk explained
- [ ] AWS reference samples cited as prior art, kept distinct from the REDACTED package (per source note)
- [ ] Reference doc + quiz + SR cards + glossary JSON produced
- [ ] Every load-bearing claim cites a repo file path or `[L#]` source
- [ ] `mise run verify` passes; `check-topic-completeness.py` clean for this topic
