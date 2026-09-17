---
id: "378"
title: "Teach: generative-media-pipelines / speech-generation"
status: open
blocked_by: ["367", "372", "374"]
tags: ["content"]
---

# Teach: generative-media-pipelines / speech-generation

Generate the lesson for topic 8 (MAP id `01M2RAGF0SAB63SQZD244ZTAPY`, lesson file
`08-speech-generation.html`, scope: substantial, prereqs: scale-to-zero-gpu-serving +
the-async-contract). Produced via the `generate-topic` pipeline.

> **Refined 2026-09-17** from a per-topic research+review subagent (license statuses + Polly/Nova
> Sonic capabilities web-verified 2026-09-17). Findings: `.scratch/research/378-refine.md`. **Use
> the deep-research license verdicts, NOT pass-1** (XTTS-v2 = CPML non-commercial, F5-TTS = CC-BY-NC).

## What to build

Speech is a **family of distinct tasks, not one thing** — the AWS decision is two-axis: **task ×
serving pattern**. Spine:

1. **Task taxonomy** (table/diagram, `task → tool`): TTS / STT / S2S / voice-clone / dubbing /
   music-SFX. Explicitly call out the two conceptual traps: **STT is the inverse (understanding, not
   generation)** and **dubbing is a pipeline (ASR→translate→clone→time-align→mux), not a model.**
2. **AWS-native managed:** **Amazon Polly** (batch + streaming TTS; generative engine; sync
   `SynthesizeSpeech` ≤3k billable chars, async `StartSpeechSynthesisTask` ≤100k → S3 = Polly's own
   async mirror, bidirectional `StartSpeechSynthesisStream` generative-only). **Nova 2 Sonic** (GA
   2025-12-02, real-time conversational S2S on Bedrock; regions incl. Stockholm per current release
   notes — supersede the gap-research "rolled back" note). **No native Bedrock music/SFX** — fill via
   Bedrock Marketplace (MusicGen) or self-host (Stable Audio).
3. **Self-host open models — license gates the choice BEFORE quality** (a decision callout with the
   verified table, each row cited to its model card):
   - Commercial-safe: **Kokoro (Apache-2.0)**, **Chatterbox (MIT, watermarked)**, **CosyVoice2
     (Apache-2.0 — flag the README "academic purpose" ambiguity for legal review)**, Piper (MIT),
     Qwen3-TTS (Apache-2.0).
   - Commercial dead ends: **XTTS-v2 (CPML, and Coqui is defunct so no one to buy a license from)**,
     **F5-TTS (CC-BY-NC)**, **Fish Speech (CC-BY-NC-SA)** — the "don't pick on quality alone" trap.
4. **Async-vs-streaming fit (the crux) — a decision table:** dubbing/voiceover/audiobook batch =
   large-payload/long-job/bursty → **SageMaker Async sweet spot** (S3-pointer in/out, ≤1 GB, ≤1 hr,
   scale-to-zero, SNS); >1 hr → **Processing Jobs** (unbounded); conversational = **warm streaming**
   (Nova Sonic managed, or a warm self-hosted endpoint — real-time can't fully scale to zero without
   cold-start UX damage); CPU-tiny (Kokoro) → Serverless (CPU-only). Teach the parallel: **Polly
   `StartSpeechSynthesisTask` ↔ SageMaker Async**.

**Internal prior art anchors (one per pipeline shape):** **REDACTED** = async + SNS fan-in (the
textbook async example); **REDACTED** = Step Functions + Processing Jobs dubbing; **REDACTED** =
per-cell real-time streaming; REDACTED = managed→self-host fallback ladder.

## G2 warnings (Con callouts adjacent to what they apply to, cited)

Polly bidirectional stream **closes after 10 min** regardless of activity (reopen for longer);
XTTS-v2/F5-TTS/Fish Speech non-commercial; CosyVoice2 "academic purpose" README ambiguity;
Chatterbox watermark; Polly Brand Voice is engagement-based not self-service; real-time can't scale
to zero without cold-start UX damage; Serverless is CPU-only (6 GB, 60 s); STT-is-inverse and
dubbing-is-a-pipeline conceptual traps.

## Honest open gaps (carry, don't block)

Dia-1.6B / UVR-MDX-NET exact licenses unverified; Async cold-start for a CosyVoice2/Chatterbox
container on `ml.g6.xlarge` unmeasured (a spike would pin it); Nova 2 Sonic context window reported
~1M (label as reported, don't assert a precise number).

## Source-verification gate (per #367)

Design-source facts → `02-generative-media-pipelines.md` + both `gap-research/tts-speech-generation*.md`;
every **license verdict** → its model-card URL, dated 2026-09; Polly/Nova limits → AWS docs;
internal prior art → the named wiki runbooks. Tagged `[L#:confidence]`.

## Artifact set (authoritative gate: `tools/check-topic-completeness.py`)

Lesson HTML at **flat** `library/generative-media-pipelines/lessons/08-speech-generation.html`;
reference; quiz (≥5/≥3); SR JSONL (≥1); **inline `glossary-data` block, not a JSON file**;
code-files dir only if `data-file` blocks exist. Follows `visual-teaching.md` +
`code-validation-teaching.md`.

## Acceptance criteria

- [ ] `library/generative-media-pipelines/lessons/08-speech-generation.html` generated via `generate-topic` (flat path)
- [ ] Task-taxonomy table/diagram (TTS/STT/S2S/clone/dubbing/music-SFX) explicitly flagging STT-is-inverse and dubbing-is-a-pipeline
- [ ] Commercial-safe license Decision callout with the verified table (Kokoro/Chatterbox/CosyVoice2 shippable; XTTS-v2/F5-TTS/Fish Speech non-commercial), each row cited to its card; CosyVoice2 "academic" caveat + Chatterbox watermark flagged
- [ ] Managed-vs-self-host Decision callout with concrete criteria (the REDACTED 4-motivation rubric) + fallback ladder; AWS-native (Polly engines/limits, Nova 2 Sonic GA/regions) covered
- [ ] Async-vs-streaming serving-pattern decision table with the Polly-async ↔ SageMaker-Async parallel and why real-time can't scale to zero
- [ ] Warnings placed adjacent to the code/decision they apply to (Polly 10-min close; Serverless CPU-only; real-time-can't-scale-to-zero)
- [ ] Internal prior-art anchors named (REDACTED async+SNS; REDACTED Processing; REDACTED real-time); music/SFX gap noted (no first-party Bedrock model)
- [ ] Near-transfer misconception-probe exercise (classify task + pick serving pattern + commercial-safe model; explain why the best-sounding non-commercial cloner is blocked at launch)
- [ ] Reference + quiz (≥5/≥3) + SR JSONL + inline glossary produced; every claim cites a repo path or a card/doc URL
- [ ] `mise run verify` passes AND `check-topic-completeness.py --workspace library/generative-media-pipelines --topic speech-generation` (and `--concepts`) clean
