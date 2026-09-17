---
domain: generative-media-pipelines
description: "Host models and workflows to generate images, video, speech, and 3D on AWS: the universal scale-to-zero serving pipeline, model-onboarding-as-data, async submit/stream contracts, ComfyUI at scale, image→3D, and where LoRA training actually lives"
generated: 2026-09-17
depth: 0
parent: null
leads_to: []
---

# Generative Media Pipelines — Hosting Models to Generate Images, Video, Speech & 3D

## Orientation

A generative media pipeline is the platform that turns "a research model on a GPU" into "a stable
API a creative team calls." Three real platforms — a custom scale-to-zero orchestrator
(studio-model-service), an artist studio over Bedrock + SageMaker (ArtSmoker), and a ComfyUI
platform on EKS (riot-comfy-ui-platform) — all implement the *same* core loop: authenticate,
submit a job, queue it, wake a GPU worker that was scaled to zero, stage the model weights, infer,
store the output, and stream progress back. This track teaches that shared architecture and the
decisions inside it: which AWS scale-to-zero path to pick, why you onboard models as data instead
of endpoints, why weights never live in the container image, how to host ComfyUI headlessly, what
the image→3D landscape and its licensing look like, and why LoRA is a *hosted* category whose
*training* lives in a separate tier. It's deliberately architecture-first — the specific models are
examples; the serving patterns transfer. Sources are the three explored repos (primary) plus
internal + external prior-art research; the image→3D *output* feeds the gltf-format and
godot-asset-pipeline domains, which this references rather than duplicates.

## Topics

### the-universal-serving-pipeline
- **id:** 01M2R98N1JTYQXWXSDV3EBC7MW
- **title:** The Universal Serving Pipeline
- **why:** Every later topic is a decision *inside* this loop — you can't reason about scale-to-zero, onboarding, or the async contract without the end-to-end shape first. Taught as one diagram (client → auth → submit → queue → scale-to-zero GPU worker → weight staging → infer → output store → progress stream) with each of the three platforms mapped onto it, so the shared pattern and the divergences are both visible.
- **scope:** substantial
- **prereqs:** []
- **lesson_file:** 01-the-universal-serving-pipeline.html

### scale-to-zero-gpu-serving
- **id:** 01M2R98N1J0D5K8T3HW95QFKB9
- **title:** Scale-to-Zero GPU Serving
- **why:** GPUs are expensive and idle most of the time, so scaling to zero is the economic heart of the whole design — and cold start is the tax you pay for it. Covers the four AWS-native paths (SageMaker Async, Inference-Component minCopies=0, Serverless-CPU-only, EKS Karpenter+KEDA) + Bedrock, the measured cold-start SLO (~342s scale-from-zero vs ~150s warm-pool), and why the hand-rolled orchestrators re-implement SageMaker Async / the EKS reference architecture.
- **scope:** deep
- **prereqs:** [the-universal-serving-pipeline]
- **lesson_file:** 02-scale-to-zero-gpu-serving.html

### model-onboarding-as-data
- **id:** 01M2R98N1JH2ACGN90N90CR7A3
- **title:** Model Onboarding as Data
- **why:** Adding a model must not mean adding an endpoint or bespoke serving code — this is what lets one platform serve many models. Covers the manifest/registry (studio-model-service), the universal data-driven inference handler + format families (ArtSmoker), and the versioned workflow-container (riot); the rule-of-two seam; runner strategies (native/comfyui/mock); and why weights are never baked into the image (S3→NVMe vs FSxN+FlexClone vs HF-direct-pull, NF4/offload).
- **scope:** deep
- **prereqs:** [the-universal-serving-pipeline]
- **lesson_file:** 03-model-onboarding-as-data.html

### the-async-contract
- **id:** 01M2R98N1JF95PJKCYR4JCKFK7
- **why:** Inference is too slow for request/response, so every platform is submit/status/stream — and getting the idempotency right is where correctness lives. Covers submit/status/progress, SSE vs WebSocket, poll-then-WS resume, and the claim→commit "work-done-wins" contract (and why a reaper + visibility recovery would double-run jobs).
- **title:** The Async Submit/Status/Progress Contract
- **scope:** substantial
- **prereqs:** [the-universal-serving-pipeline]
- **lesson_file:** 04-the-async-contract.html

### comfyui-at-scale
- **id:** 01M2R98N1JSSGZ9GTRY1P5YZDT
- **title:** Hosting ComfyUI at Scale
- **why:** ComfyUI is the de-facto node-graph substrate for generative workflows, and hosting it as a service has specific traps. Covers the headless API (/prompt → prompt_id, /ws progress, /history, /object_info introspection), headless-batch vs streamed-UI (AppStream), the three AWS reference samples, the ALB WebSocket idle-timeout trap, workflow-as-immutable-container versioning, and the no-auth security surface.
- **scope:** substantial
- **prereqs:** [model-onboarding-as-data, the-async-contract]
- **lesson_file:** 05-comfyui-at-scale.html

### media-types-and-image-to-3d
- **id:** 01M2R98N1JBZ8E3378G56N2Y8S
- **title:** Media Types & Image-to-3D
- **why:** What these platforms actually generate, with image→3D as the common denominator and its own licensing/cleanup gotchas. Covers the two-level 2D pipeline (Options × Variations, canary moderation), video-async, image→3D model families (TRELLIS.2 / Hunyuan3D / TripoSG / TripoSR) + the Hunyuan3D non-commercial-license gate + the universal retopo/UV/PBR/LOD "cleanup tax" (which references gltf-format / godot-asset-pipeline rather than duplicating them).
- **scope:** substantial
- **prereqs:** [the-universal-serving-pipeline]
- **lesson_file:** 06-media-types-and-image-to-3d.html

### lora-and-the-training-tier
- **id:** 01M2R98N1JAP32MK8W74HYM6M8
- **title:** LoRA & the Training Tier
- **why:** The sharpest cross-platform finding — none of the serving platforms *train* LoRAs; they *host* them, and training lives in a separate tier. Corrects the common assumption. Covers LoRA-as-hosted-category, SageMaker Training Jobs (the default for one SDXL/FLUX LoRA) vs HyperPod (org-scale), the data-flywheel pattern, and style-via-prompt as the non-LoRA alternative.
- **scope:** substantial
- **prereqs:** [model-onboarding-as-data]
- **lesson_file:** 07-lora-and-the-training-tier.html
