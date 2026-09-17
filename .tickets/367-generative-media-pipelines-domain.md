---
id: "367"
title: "Set up generative-media-pipelines domain (MAP + study-guide-backed topics + source-verification gate)"
status: open
blocked_by: []
priority: medium
validation_criteria:
  - "generative-media-pipelines.MAP.md exists with the topic spine + prereq edges (passes check-maps-forest)"
  - "Source-verification gate defined (every lesson claim traces to a cited repo file or [L#]-tagged external source)"
  - "Provenance recorded; standalone depth-0; no lessons generated until sign-off"
tags: ["content"]
---

# Set up generative-media-pipelines domain (MAP + study-guide-backed topics + source-verification gate)

Stand up the standalone **`generative-media-pipelines`** teaching domain — the platform stack for
*hosting models and workflows to generate images, video, speech, and 3D* on AWS, plus related tasks
like LoRA. Conceptual/architecture track built from three real platforms + prior-art research.

**Setup/scaffold + proposal only — NO lessons generated.** Design source (already written +
promoted): `.memory/research/world-models-and-genmedia/02-generative-media-pipelines.md` (briefing +
study guide + gap research). Backing findings: `repo-findings/{studio-model-service,artsmoker,riot-comfy-ui-platform}.md`
and all seven `gap-research/*.md`.

## Why this domain

Three explored platforms solve the same core differently — `studio-model-service` (custom
scale-to-zero orchestrator), `ArtSmoker` (artist web studio over Bedrock + SageMaker), and
`riot-comfy-ui-platform` (ComfyUI on EKS/AppStream). The study guide already extracts the shared
pattern (submit→queue→scale-to-zero worker→stage weights→infer→stream) and the cross-cutting
lessons (onboarding-as-data, cold-start-as-SLO, LoRA-is-hosted-not-trained, image→3D as the common
denominator), and the gap research adds the AWS reference architectures each repo reinvents.

## Domain shape (proposed)

```yaml
domain: generative-media-pipelines
description: "Host models and workflows to generate images, video, speech, and 3D on AWS: scale-to-zero GPU serving, model-onboarding-as-data, async submit/stream contracts, ComfyUI at scale, image→3D, and where LoRA training actually lives."
depth: 0
parent: null
leads_to: null
```

Standalone depth-0. Receives a `leads_to` edge from #366 (serving a world model is an instance of
this). Adjacent to the existing `gltf-format` / `godot-asset-pipeline` domains (image→3D output
feeds them) — reference, don't duplicate.

## Proposed topic spine (from the study guide's concept list — refine at scaffold time)

| # | slug | core idea | prereqs |
|---|------|-----------|---------|
| 1 | `the-universal-serving-pipeline` | client→auth→submit→queue→scale-to-zero GPU worker→weight staging→infer→output store→progress stream; the shared shape across all three platforms | [] |
| 2 | `scale-to-zero-gpu-serving` | why GPUs scale to zero; four AWS-native paths (SageMaker Async / Inference-Component minCopies=0 / Serverless-CPU / EKS Karpenter+KEDA); cold-start as an SLO (342s vs 150s) + mitigations | [1] |
| 3 | `model-onboarding-as-data` | manifest/registry/workflow-container vs per-model endpoints; the rule-of-two seam; runner strategies (native/comfyui/mock) | [1] |
| 4 | `weights-storage-and-cold-start` | never bake weights; S3→NVMe vs FSxN+FlexClone vs HF-direct-pull; NF4/offload; SOCI / Fast Model Loader | [2] |
| 5 | `the-async-contract` | submit/status/progress; SSE vs WebSocket; poll-then-WS resume; claim→commit idempotency | [1] |
| 6 | `comfyui-at-scale` | node-graph workflows; headless API (/prompt, /ws, /history, /object_info); headless vs streamed UI; ALB WebSocket trap; no-auth risk; three AWS reference samples | [3,5] |
| 7 | `media-types-and-image-to-3d` | what each platform generates; the two-level 2D pipeline; video-async; image→3D model families + Hunyuan3D license gate + the universal retopo/UV/PBR/LOD cleanup tax | [1] |
| 8 | `lora-and-the-training-tier` | LoRA is hosted, not trained; SageMaker Training Jobs (default for one LoRA) vs HyperPod (org-scale); the data-flywheel pattern; style-via-prompt as the non-LoRA alternative | [3] |
| 9 | `speech-generation` (optional) | the gap: AWS Polly + Nova Sonic S2S; self-host Chatterbox/Kokoro/XTTS; internal dubbing prior art; how it fits the same pipeline | [1] |

Prereq edges: `1→{2,3,5}`, `2→4`, `{3,5}→6`, `1→7`, `3→8`, `1→9`. All within-map. (9 is the
biggest — likely trim to ~6-7 core topics; 9 is optional given the thin speech coverage.)

## Validation gate (source-verification, not a code harness)

Conceptual domain — no runtime artifact. Same gate as #366:

- Every load-bearing claim traces to a cited **repo file path** or a **`[L#:confidence]` external
  source** (per `source-authority` steering). Cite AWS reference-sample repos and internal wiki
  guides from the gap research, not parametric memory.
- Standard `mise run verify` (links + lint + SVG theming + glossary coverage).
- Numbers cited or framed general — e.g. cold-start "342s vs 150s p95" cites
  `studio-model-service/.memory/spikes/02-cold-start-comparison.md`.

## Source note to carry into topic 6

The `riot-comfy-ui-platform` package did not surface in InternalSearch (likely a private GitFarm
package). Topic 6's AWS reference-sample content (`aws-samples/comfyui-on-eks` etc.) is prior art,
verified independently — not a claim about that specific repo. Keep the two distinct in lessons.

## Acceptance criteria

- [ ] `generative-media-pipelines.MAP.md` at `library/generative-media-pipelines/maps/` with the topic spine + prereq edges; ULIDs via `tools/migrate_map_ids.py --apply`; passes `tools/check-maps-forest.py`
- [ ] Source-verification gate recorded (claim→cited-source contract)
- [ ] Standalone depth-0 confirmed; incoming `leads_to` from #366 recorded; differentiated from gltf-format / godot-asset-pipeline (no duplication — reference for image→3D output)
- [ ] Provenance recorded (design source = the promoted guide; backing = repo-findings + all gap-research)
- [ ] Topic spine reviewed/trimmed (9 → final count; decide whether speech is in-scope) with the user before topic tickets
- [ ] NO lessons generated — topic tickets created after this is signed off

## Notes

- Design source + backing research already written and committed under
  `.memory/research/world-models-and-genmedia/`.
- Pairs with #366 (world-models). Gap research surfaced strong internal prior art for every
  sub-area (fine-tune-SDXL-with-Kohya IaC, ComfyUI reference samples, TTS dubbing pipelines,
  the "Deploying Open Models on AWS" decision guide) — cite these in the relevant topics.
