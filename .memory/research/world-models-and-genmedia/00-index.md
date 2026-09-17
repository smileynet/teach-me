# Briefing & Study Guides — World Models and Generative Media Pipelines

Two research-backed guides synthesized 2026-09-15 from five explored repos (symlinked into
`.references/`). Each guide has a **Briefing** half (what/why/landscape, read once cold) and a
**Study** half (concepts to master + explain-to-a-colleague self-tests + glossary + source map).

## The two guides

1. **[World Models](01-world-models.md)** — AI systems that *simulate steerable, interactive
   environments* (predict the next frame given an action), and how you tell a good one from a
   "vivid dream." Covers the generator side (real-time video-diffusion, Rolling Forcing, DMD
   distillation, action conditioning on AWS Trainium) and the evaluator side (the FDS benchmark:
   engine-as-oracle, behavioral IDM round-trip, drift horizon).

2. **[Generative Media Pipelines](02-generative-media-pipelines.md)** — the platform stack for
   *hosting models and workflows to generate images, video, speech, and 3D*, plus related tasks
   like LoRA. Covers scale-to-zero GPU serving, model-onboarding-as-data, the async
   submit/status/progress contract, ComfyUI as a substrate, hot-weights storage, and where LoRA/
   training actually lives (spoiler: hosted, not trained, in the serving platforms).

## The five repos and how they map

| Repo | Primary guide | What it is |
|------|---------------|------------|
| `world-models` | World Models | Research project defining **FDS**, a benchmark that separates "looks real" from "plays correctly" — the missing eval-metrics piece. |
| `delirium-world-models-poc` | World Models (+ serving in Media) | Browser-playable world model: a fork of TencentARC Rolling Forcing (Wan2.1 causal DiT), DMD-distilled to ~14 fps on Trainium2, with a grafted action pathway. |
| `studio-model-service` | Generative Media Pipelines | Scale-to-zero inference platform serving generative *art* models (PBR maps, 3D mesh) to DCC tools; a reference-architecture demo. |
| `ArtSmoker` | Generative Media Pipelines | Self-hosted artist web studio: prompt -> 2D/edit/video/STT/3D, over Bedrock + self-deployed SageMaker endpoints. The broadest media coverage. |
| `riot-comfy-ui-platform` | Generative Media Pipelines | Production platform to run *any* ComfyUI workflow on a shared GPU fleet, API-headless or streamed UI; live image->3D. |

## How the two topics connect

They are two ends of one pipeline. **World models** are a *kind of model you'd host*; **generative
media pipelines** are *how you host models*. `delirium` is the hinge — its model internals belong
to the World Models guide, but its GPU-serving, SSE-streaming, scale-from-zero deployment is a
generative-media-pipeline problem like the other three. A world/video model is, from a serving
platform's view, "just another `OutputKind` + runner" — which is exactly why
`studio-model-service`'s onboarding seam is built the way it is.

## Cross-cutting findings worth remembering

- **image->3D mesh is the common denominator** — TripoSR / TripoSG / TRELLIS.2 / Hunyuan3D-2 show
  up in every media platform. It's the most mature "generate a usable asset" capability.
- **Weights never live in the image** — S3->NVMe, FSxN+FlexClone, or HF-direct-pull. The image
  pull is the real cold-start tax.
- **Cold start is an SLO, not an afterthought** — measured (342s scale-from-zero vs 150s warm)
  and designed around.
- **Onboarding a model is a config action, not new code** — manifest / registry / workflow
  container.
- **LoRA is hosted, not trained** in the serving platforms; real training (DMD, action adapters)
  only appears in the world-model research repo, and even there LoRA-on-attention was a dead end.
- **Speech is thin** — one STT capability (ArtSmoker's Nova Sonic); **no text-to-speech anywhere**
  across the five repos. A genuine gap if speech generation is a goal (see gap research below —
  AWS Polly / Nova Sonic S2S + strong internal TTS prior art exist).

## Gap-filling research (2026-09-16)

Seven follow-up research passes (internal + web search) filled the gaps the repo synthesis
surfaced. Each guide now has a **Part 3 — Prior Art & Gap-Filling Research** section; the raw
findings (per-claim `[L#:confidence]` source tags) are in `.scratch/research/gaps/`:

| Gap | File | Headline finding |
|-----|------|------------------|
| World-model eval prior art | `gaps/world-model-eval-prior-art.md` | FDS's IDM-round-trip is an established family (VPT->Genie->RLIR), not novel; complements FVD/CD-FVD. No internal FDS predecessor. |
| Real-time WM serving | `gaps/realtime-worldmodel-serving.md` | **Decart** is the internal delirium analog (NKI mega-kernels, ~25 fps on Trainium3); Self-Forcing + WebRTC + step-distillation is the reference stack. |
| Speech generation | `gaps/tts-speech-generation.md` | AWS Polly + Nova Sonic S2S; self-host Chatterbox/Kokoro/XTTS; strong internal prior art (Connect UTTS, XBLocalizedVideo dubbing). |
| LoRA / fine-tuning tier | `gaps/lora-training-tier.md` | SageMaker Training Jobs = default for one LoRA; HyperPod = org-scale. Internal "Fine-tune SDXL with Kohya" IaC solution exists. |
| Scale-to-zero GPU serving | `gaps/scale-to-zero-gpu-serving.md` | Four AWS-native paths; the three repo orchestrators reinvent SageMaker Async / EKS+KEDA reference architectures. |
| ComfyUI at scale | `gaps/comfyui-at-scale.md` | Three AWS reference samples (`comfyui-on-eks` etc.); the ALB WebSocket idle-timeout trap; core ComfyUI has no auth. |
| image->3D generation | `gaps/image-to-3d-generation.md` | Two model families + a **Hunyuan3D non-commercial-license** gate; universal retopo/UV/PBR/LOD cleanup tax already codified in Amazon artist SOPs. |

## Provenance

- Per-repo raw findings (fully file-path-cited): `.scratch/research/*.md`
- Gap research (internal + web, `[L#:confidence]`-tagged): `.scratch/research/gaps/*.md`
- These are synthesized reference docs in `.scratch/` (ephemeral). Promote to `.memory/` or a
  committed location if they should persist.

## Caveats

- Guide claims sourced from repo code/docs were gathered by subagents citing file paths; guide
  claims in the Part 3 sections were gathered by subagents citing web/internal URLs. Load-bearing
  claims should be verified against the cited source before use in an external briefing.
- Two items to verify against source: (1) FDS's exact mathematical definition (the guide says
  `1 - action_F1`); (2) whether the `riot-comfy-ui-platform` internal package matches the AWS
  reference samples (it did not surface in InternalSearch — likely a private GitFarm package).
