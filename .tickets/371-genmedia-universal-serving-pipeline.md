---
id: "371"
title: "Teach: generative-media-pipelines / the-universal-serving-pipeline"
status: open
blocked_by: ["367"]
tags: ["content"]
---

# Teach: generative-media-pipelines / the-universal-serving-pipeline

Generate the lesson for topic 1 of the `generative-media-pipelines` domain (MAP id
`01M2R98N1JTYQXWXSDV3EBC7MW`, lesson file `01-the-universal-serving-pipeline.html`, scope:
substantial, prereqs: none).

## What to build

Teach the end-to-end shape shared by all three explored platforms as **one diagram** —
client → auth → submit → queue → scale-to-zero GPU worker → weight staging → infer → output
store → progress stream — with `REDACTED`, `REDACTED`, and `REDACTED`
each mapped onto it so the shared pattern and the divergences are both visible. This is the spine
every later topic decides *inside*, so it must land the whole loop before any single stage is
deepened.

Run the `generate-topic` pipeline: research → lesson → post-process (jargon, diagram, downloadable
artifacts if any code) → verify.

## Source-verification gate (per #367)

- Every load-bearing claim traces to a cited **repo file path** (the three explored repos are
  primary) or a **`[L#:confidence]` external source** per `source-authority` steering. No
  parametric memory.
- Design source: `.memory/research/world-models-and-genmedia/02-generative-media-pipelines.md`
  (briefing + study guide). Backing: `repo-findings/{REDACTED,REDACTED,REDACTED}.md`.
- `mise run verify` clean (links + lint + SVG theming + glossary coverage).

## Acceptance criteria

- [ ] `library/generative-media-pipelines/lessons/generative-media-pipelines/01-the-universal-serving-pipeline.html` generated via `generate-topic`
- [ ] The three platforms are each mapped onto the single shared loop diagram (shared shape + divergences visible)
- [ ] Reference doc + quiz + SR cards + glossary JSON produced (per lesson-authoring contract)
- [ ] Every load-bearing claim cites a repo file path or `[L#]` source (source-verification gate)
- [ ] `mise run verify` passes; `check-topic-completeness.py` reports no missing artifacts for this topic
