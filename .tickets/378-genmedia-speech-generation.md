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
the-async-contract).

## What to build

Teach speech as a first-class generative modality the explored platforms barely touch (only STT).
Cover the task taxonomy (TTS vs STT vs speech-to-speech vs voice cloning vs dubbing-as-a-pipeline
vs music/SFX) and which tool serves each; the AWS-native decision (Amazon Polly generative engine +
streaming; Nova 2 Sonic S2S on Bedrock) vs self-hosting open models (Kokoro/Chatterbox/CosyVoice2
are commercial-safe; XTTS-v2/F5-TTS are non-commercial — **license gates before quality**); and the
serving-pattern fit: dubbing/voiceover are large-payload, long-job, bursty = the **SageMaker Async
sweet spot** (S3-pointer in, scale-to-zero, SNS notify), while conversational voice needs a warm
streaming endpoint. Internal prior art: REDACTED audiobook voice-clone on SageMaker Async, Connect
REDACTED real-time streaming.

Run `generate-topic`: research → lesson → post-process → verify.

## Source-verification gate (per #367)

- Claims → repo file path or `[L#]` source. Deep research promoted to
  `.memory/research/world-models-and-genmedia/gap-research/tts-speech-generation-deep.md` — cite it.
- Open-model commercial-vs-non-commercial license status cited to each model's license.
- `mise run verify` clean.

## Acceptance criteria

- [ ] `library/generative-media-pipelines/lessons/generative-media-pipelines/08-speech-generation.html` generated
- [ ] Task taxonomy + AWS-native (Polly / Nova 2 Sonic) vs self-host decision covered; license gates flagged before quality
- [ ] Async-vs-streaming serving fit explained (dubbing = SageMaker Async; conversational = warm endpoint)
- [ ] Reference doc + quiz + SR cards + glossary JSON produced
- [ ] Every load-bearing claim cites a repo file path or `[L#]` source
- [ ] `mise run verify` passes; `check-topic-completeness.py` clean for this topic
