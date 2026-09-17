# Generative Media Pipelines — Briefing Guide & Study Guide

Synthesized 2026-09-15 from three platform repos — `studio-model-service`, `ArtSmoker`,
`riot-comfy-ui-platform` — plus the serving side of `delirium-world-models-poc`. "Generative
media pipeline" here means the whole stack for *hosting models and workflows to generate images,
video, speech, and 3D*, plus related tasks like LoRA. Every claim traces to the repos' own docs;
file paths are cited in the source findings under `.scratch/research/`.

---

## PART 1 — BRIEFING GUIDE

### The shape of the problem

Turning "a research model on a GPU" into "a capability a creative team actually uses" is a
platform problem, not a model problem. All three repos solve the *same core* — host arbitrary
generative models on GPUs, serve them through a stable interface, and don't pay for idle GPUs —
but make different bets on the serving substrate and the target user.

The recurring pattern across all of them:

```
Client -> Auth -> Submit API -> Queue -> GPU worker (scale-to-zero) -> weights S3->local -> infer -> output store -> progress stream
```

### The three platforms at a glance

| | **studio-model-service** | **ArtSmoker** | **riot-comfy-ui-platform** |
|---|---|---|---|
| One-liner | Scale-to-zero inference platform serving art models to DCC tools (Blender-first) | Self-hosted artist web studio: prompt -> 2D/edit/video/3D | GPU platform to run *any* ComfyUI workflow, API or streamed UI |
| Target user | A Blender plugin (machine client) | A working artist (human, browser) | Any Riot creative/eng team |
| Serving substrate | Custom FastAPI orchestrator + SQS + GPU worker | Bedrock (managed) **and** self-deployed SageMaker endpoints | ComfyUI on EKS (headless) + AppStream (interactive UI) |
| Model onboarding | Typed `ModelManifest` in a registry (no new endpoints) | `model_registry.json` + universal inference handler | Versioned ComfyUI workflow container in ECR |
| Media types | image->PBR maps, image->3D mesh | 2D image, SVG, image editing, video, speech-to-text, image->3D | image->3D (live); text->image staged; video/audio absent |
| Framing | Reference-architecture *demo* (Ubisoft) | Shipping, feature-rich product | Production platform, all milestones complete |

### Cross-cutting concept 1: scale-to-zero GPU serving

GPUs are expensive and idle most of the time, so all three drop to ~$0 when no work is queued.

- **studio-model-service** makes cold start a **measured SLO**: scale-from-zero p95 **342s**
  ($0 idle) vs a warm-pool STOPPED-EBS p95 **150s** (~$10-15/mo/worker). The 6.3 GB docker
  pull dominates true cold-start (~40% of it). GPU acquisition is a **diversified EC2 Fleet**
  across families/AZs because single-instance-type capacity droughts are common. Autoscaling is
  a *pure decision function* on queue depth with two mechanisms (0<->1 and 1<->N) and asymmetric
  cooldowns (scale out fast, in slow) (`studio-model-service/.memory/spikes/02-cold-start-comparison.md`,
  `orchestrator/autoscaler.py`).
- **riot-comfy-ui-platform** uses **KEDA** on DynamoDB job-queue depth with `minReplicaCount 1`
  (a warm pod, because GPU cold start is 3-4 min) and `maxReplicaCount 2` — KEDA is the *binding*
  ceiling, not the node limits. Weekend "park" scales to zero via a KEDA annotation. Suspend/
  resume destroys GPU compute (~2 min) but always retains the FSxN model store (~$35/mo)
  (`riot-comfy-ui-platform/k8s/keda/comfy-scaledobject.yaml`, `docs/platform-brief.md`).
- **ArtSmoker** registers SageMaker scale-to-zero autoscaling **only after the model confirms
  loaded**, so scale-in can't kill a 5-60-min model load (`ArtSmoker/backend/services/sagemaker_deployer.py`).

**The universal rule: weights are never baked into the image.** They live in S3/HF and are
staged to local NVMe (studio-model-service) or mounted over NFS (riot) or pulled from HuggingFace
at container start (ArtSmoker). Baking GB of weights into images makes cold start and iteration
untenable.

### Cross-cutting concept 2: model onboarding as data, not code

Adding a model should not mean adding an endpoint or writing bespoke serving code.

- **studio-model-service:** a model is a typed `ModelManifest` (model_id + integer version +
  runner + typed I/O contract + weights dependency *list* + license gate). `register_model()` is
  the only path; a `pbr_map_set` model (CHORD) and a `mesh` model (TripoSR) onboard through the
  *identical* path — the "rule of two" proving the seam is generic. There are three **runner**
  strategies: `native` (in-process PyTorch, shipped), `comfyui` (out-of-process HTTP), `mock`
  (demo). "Compare, don't pick" is an explicit ADR (`studio-model-service/registry.py`,
  `contract.py`, ADR 0003/0005).
- **ArtSmoker:** a 392 KB `model_registry.json` + a single **universal, data-driven inference
  handler** baked into every endpoint's `model.tar.gz`. It dispatches on env vars
  (`INFERENCE_LIBRARY`/`PREDICTOR_TYPE`) set from the catalog, so one handler serves FLUX,
  Hunyuan, Qwen, TripoSG, TRELLIS.2. "Format families" are JSON body templates that let one
  generic invoker call any model with zero new code (`ArtSmoker/backend/sagemaker_handlers/inference.py`,
  `backend/model_registry.py`).
- **riot-comfy-ui-platform:** the *workflow container* (ComfyUI + custom nodes + workflow JSON)
  is the unit of deployment and versioning. Promotion: git push -> build -> vuln scan -> manual
  approval -> immutable ECR tag; the fleet pulls only `approved=true`
  (`riot-comfy-ui-platform/docs/VISION.md`).

### Cross-cutting concept 3: the async submit/status/progress contract

None of these are request/response — inference is too slow. They all use:

- A **submit** call that validates + enqueues and returns a job id (studio-model-service enforces
  the **license gate before enqueue** and requires image/mesh inputs as **S3 references, not
  inline bytes**).
- A **status** GET (authoritative, poll-safe).
- A **progress stream**: WebSocket in studio-model-service and riot (ComfyUI `/ws`), SSE in
  ArtSmoker and delirium. studio-model-service's pattern is "poll-then-WS": the socket sends the
  current snapshot then streams normalized events, so a reconnect resumes from authoritative
  state.

studio-model-service adds a rigorous **claim->commit** idempotency contract: only the conditional
QUEUED->RUNNING winner runs inference; commit is "work-done-wins"; dead workers are recovered via
SQS visibility + conditional stale-reclaim (a reaper *and* visibility recovery would double-run
jobs) (`studio-model-service/orchestrator/executor.py`, `store.py`, `worker.py`).

### Media types: who generates what

- **2D image + editing (ArtSmoker):** its richest surface. A "two-level" **Options x Variations**
  pipeline — the LLM produces N distinct *concepts*, the image model produces M *seed variants*
  each (<=25/batch). Full stage chain: language detect -> asset-type classify -> prompt decompose
  (subject/scene/composition/lighting/style, each field user-or-inferred with lock/vary) ->
  recompose -> per-model LLM enhance (+ negative-prompt synthesis) -> **canary** single-image
  moderation probe -> parallel batch -> post-process (bg-remove/upscale/SVG) -> store with 3-level
  prompt lineage, streamed over SSE. Editing includes mask-free instruction outpaint via a
  pre-pad -> complete-new-band -> feather-blend recipe
  (`ArtSmoker/backend/routers/generate.py`, `services/instruction_outpaint.py`).
- **Video (ArtSmoker):** Bedrock `StartAsyncInvoke` for Nova Reel + Luma Ray; output pulled from
  S3, thumbnails via ffmpeg. All invocation params come from the registry.
- **Speech (ArtSmoker):** Nova Sonic bidirectional-streaming **speech-to-text** (needs the
  experimental Smithy Bedrock runtime SDK). *(Note: this is the only speech capability across all
  five repos, and it's STT, not TTS.)*
- **PBR material maps (studio-model-service):** CHORD, a diffusion-based material-*estimation*
  model — one texture image -> a 5-map svBRDF set (base_color, normal, roughness, metallic,
  height). The real `NativeRunner` fails fast if CUDA is absent (never a silent CPU fallback) and
  stages the SD base *config + tokenizer only*, never base weights (`studio-model-service/runners/native.py`).
- **image->3D mesh (all three, the common denominator):** TripoSR (studio-model-service),
  TripoSG + TRELLIS.2 (ArtSmoker), TRELLIS.2 (riot's live reference workflow). This is the one
  capability every platform ships or targets. ArtSmoker then does **engine export** via headless
  Blender: correct up-axis + LODs + collision hulls + engine-specific texture packing (Unreal
  ORM, Unity metallic-in-alpha) for Unreal/Unity/Godot/Maya (`ArtSmoker/backend/services/mesh_export.py`).

### LoRA and training: mostly a hosting concern, rarely a training one

This is the sharpest cross-repo finding. **None of the three platforms trains LoRAs or
fine-tunes.** LoRA appears only as a *hosting* category:

- **riot-comfy-ui-platform:** `loras` is a model category and a SageMaker Model Package Group;
  serving a LoRA adapter is a container/model update. Training is explicitly scoped out — "A
  HyperPod training tier was scoped out early; fine-tuning is not in this platform." A HyperPod
  fine-tune milestone is *proposed but unbuilt*, and even it notes a single-node SageMaker job
  would be cheaper for a LoRA/DreamBooth SDXL fine-tune (`riot-comfy-ui-platform/README.md`,
  `docs/milestones/hyperpod-finetune-proposal.md`).
- **studio-model-service:** training is a deliberately deferred "data flywheel" — artist
  accept/correct feedback *would* become labeled data, but it's reduced to "a shown hook" for the
  demo (ADR 0006).
- **ArtSmoker:** all `lora`/`training` hits are inside *vendored upstream* 3D packages, not
  ArtSmoker's own code. Style consistency is achieved by **LLM-reasoned vision style profiling ->
  text directive** (a prompt prepended to every generation), explicitly *not* LoRA/embedding style
  transfer.
- **delirium (the exception):** actually *does* training — DMD distillation and a supervised
  action-adapter objective on Trainium — but that's world-model research, not media-asset LoRA.
  And even there, a LoRA-on-attention experiment was counterproductive and disabled.

**Takeaway:** in production media pipelines today, "custom model" almost always means *host a
fine-tuned/imported model*, not *train one here*. Training is a separate, heavier tier
(HyperPod / single-node SageMaker jobs).

### The ComfyUI question (riot's central bet)

ComfyUI is an open-source **node-graph engine** for generative workflows; a workflow serializes
to JSON. riot's bet is that this is the right universal substrate: run the *same* container image
+ model library two ways — headless on EKS (`POST /prompt` -> `prompt_id`, WebSocket progress,
`/history` -> outputs) for batch, and the full ComfyUI UI streamed via AppStream for interactive
artists. studio-model-service treats ComfyUI as *one runner strategy among three* rather than the
foundation. The tradeoff: ComfyUI gives you a huge node/workflow ecosystem and an interactive UI
for free, but its in-process job queue forces ALB sticky sessions + a `Recreate` deploy strategy
(one GPU per node) (`riot-comfy-ui-platform/docs/comfy-platform-overview.md`, `docs/platform-brief.md`).

### Model storage: the hot-weights problem

Weights are big and every cold worker needs them fast. Three answers:

- **studio-model-service:** S3 -> local NVMe staging at container start; the 6.3 GB image pull is
  the real cold-start tax (hence a SOCI parallel-pull ticket).
- **riot-comfy-ui-platform:** S3 (authoritative) -> **FSx for NetApp ONTAP** hot NFS (`nconnect=16`
  for ~10 GbE) -> **FlexClone** per team/PR (copy-on-write, <10s, zero storage overhead). FSxN was
  chosen over EFS (no `nconnect`) and Mountpoint-S3 (no mmap). A writable shared root + a read-only
  curated library resolve models (`riot-comfy-ui-platform/docs/platform-brief.md`).
- **ArtSmoker:** weights pulled directly from HuggingFace at container start (`ARTSMOKER_HF_REPO`),
  so GB of weights never touch the app host; a `BlockOffloadManager` slides model blocks GPU<->CPU
  to fit large models on smaller GPUs, plus NF4 quantization (`ArtSmoker/backend/services/sagemaker_deployer.py`).

### Governance & safety threads

- **License gates:** studio-model-service enforces license acceptance at model registration;
  riot's **vending Lambda** gates on SageMaker model-package approval + a team S3-tag before
  returning an NFS path; ArtSmoker does an HF gated-access pre-check across the full dependency
  closure (incl. transitive gated deps like DINOv3) and surfaces mandatory attribution ("Built
  with DINOv3").
- **Content moderation:** ArtSmoker's **canary** probe runs one image through moderation before
  the full N x M batch, so a block wastes 1 call not many.
- **Tenancy:** studio-model-service carries an `org_id` claim and treats cross-org access as 404.

---

## PART 2 — STUDY GUIDE

### Core concepts to master

1. **The universal serving pipeline** — client -> auth -> submit -> queue -> scale-to-zero GPU
   worker -> weights staging -> infer -> output store -> progress stream. Be able to draw it.
2. **Scale-to-zero + cold start as an SLO** — the 342s-vs-150s tradeoff, why the docker/image
   pull dominates, warm-pool vs true-zero, diversified-Fleet capacity acquisition.
3. **Model onboarding as data** — manifest/registry/workflow-container instead of per-model
   endpoints; the "rule of two" test that a seam is generic.
4. **Runner strategies** — native vs comfyui vs mock; "compare, don't pick."
5. **Async contract** — submit/status/progress; WebSocket vs SSE; poll-then-WS resume; the
   claim->commit idempotency contract and why a reaper + visibility recovery double-runs jobs.
6. **Weights never in the image** — S3->NVMe vs FSxN+FlexClone vs HF-direct-pull; NF4/offload for
   fitting big models.
7. **Media-type coverage reality** — image->3D is the common denominator; 2D+editing is
   ArtSmoker's depth; video is Bedrock-async only; speech is a single STT capability; **no TTS,
   no in-platform LoRA training anywhere.**
8. **The two-level 2D pipeline** — Options (concepts) x Variations (seeds), decompose/enhance/
   canary/batch/post-process.
9. **ComfyUI as substrate** — node-graph workflows, headless vs streamed-UI, and the sticky-
   session/Recreate cost of its in-process queue.
10. **LoRA is hosted, not trained** — where training actually lives (deferred flywheel / proposed
    HyperPod / separate SageMaker jobs), and style-via-prompt as the non-LoRA alternative.
11. **Governance** — license gates, model vending/approval, canary moderation, gated-model
    attribution, org tenancy.

### Self-test (explain-to-a-colleague format)

- A teammate wants to add a new image model by "spinning up another endpoint." Explain the
  onboarding-as-data alternative and why it scales better. *(Manifest/registry/workflow-container;
  adding a model is a config entry, not new serving code; the rule-of-two seam.)*
- Why is cold start treated as a first-class SLO, and what dominates it? What are the two ways to
  trade money for latency? *(342s scale-from-zero vs 150s warm-pool; image/weights pull dominates;
  warm-pool STOPPED-EBS costs idle EBS, true-zero costs latency.)*
- A colleague says "let's bake the weights into the container so startup is fast." Why is that
  backwards? *(GB weights make the image pull the cold-start bottleneck and kill iteration; stage
  from S3/NFS/HF instead.)*
- Someone asks "where do we train the LoRA in this platform?" Given these three repos, what's the
  honest answer? *(You don't — LoRA is a hosted category; training is a separate deferred/proposed
  tier; a single-node SageMaker job or HyperPod, not the serving platform.)*
- Why does ComfyUI on EKS need ALB sticky sessions and a Recreate deploy strategy? *(ComfyUI holds
  job state in-process; a request must return to the same pod, and one GPU per node means you
  replace rather than surge.)*
- A batch of 25 images gets moderation-blocked. Why does ArtSmoker's design waste only 1
  generation call, not 25? *(The canary probe moderates one image before the parallel batch.)*
- Why does studio-model-service require image inputs as S3 references and run inference only for
  the conditional QUEUED->RUNNING winner? *(Queues carry references not bytes; claim->commit
  idempotency prevents duplicate/lost work; "work-done-wins" commit.)*

### Glossary

- **Scale-to-zero** — worker/endpoint count drops to 0 when the queue is empty (~$0 idle).
- **Cold start** — elapsed time from "queued, no warm worker" to "first result"; a measured SLO,
  not container boot time.
- **Warm pool vs scale-from-zero** — STOPPED-EBS workers (~150s p95, idle EBS cost) vs true-zero
  (~342s p95, $0 idle).
- **Diversified EC2 Fleet** — GPU acquisition across instance families/AZs (OD->Spot) to survive
  single-type capacity droughts.
- **Runner** — a model's execution strategy: native (in-process PyTorch), comfyui (out-of-process
  HTTP), mock (demo).
- **Model manifest / registry** — the catalog entry (id+version+runner+typed I/O+weights+license)
  that makes onboarding a model a config action.
- **Rule of two** — build the generic seam only once two concrete cases need it; here, a PBR model
  + a mesh model prove the runner seam is generic.
- **Format family** — a registry JSON body template that lets one generic invoker call any model
  with no new code (ArtSmoker).
- **Universal inference handler** — one data-driven handler baked into every endpoint, dispatching
  on env vars from the catalog (ArtSmoker).
- **Workflow container** — ComfyUI + custom nodes + workflow JSON packaged as a versioned ECR
  image; riot's unit of deployment.
- **ComfyUI** — open-source node-graph generative-workflow engine; runs headless (API) or
  interactive (streamed UI); workflows serialize to JSON.
- **claim->commit / work-done-wins** — the idempotency contract: only the conditional
  QUEUED->RUNNING winner runs; commit succeeds if work is done.
- **poll-then-WS** — a progress socket that sends the authoritative snapshot then streams events,
  so reconnects resume correctly.
- **SSE vs WebSocket** — server-sent events (ArtSmoker/delirium) vs bidirectional socket
  (studio-model-service/riot ComfyUI) for progress.
- **Options x Variations** — ArtSmoker's two-level 2D generation: LLM concepts x image seeds.
- **Canary (moderation)** — one probe generation moderated before the full batch.
- **PBR / svBRDF maps** — the texture set describing how a surface reacts to light (base_color,
  normal, roughness, metallic, height); CHORD's output.
- **CHORD** — Ubisoft La Forge diffusion model that *estimates* a PBR map set from one image.
- **TripoSR / TripoSG / TRELLIS.2 / Hunyuan3D-2** — image->3D-mesh models; the common capability
  across the platforms.
- **FSxN + FlexClone** — high-throughput NFS store for hot weights + instant copy-on-write clones
  per team/PR (riot).
- **nconnect=16** — NFS option opening 16 TCP connections for parallel throughput.
- **S3->NVMe staging** — copy weights from S3 to local NVMe at container start (studio-model-service).
- **HF-direct-pull** — ship KB of handler code; the container downloads weights from HuggingFace
  at startup (ArtSmoker).
- **BlockOffloadManager / NF4** — sliding-window GPU<->CPU block offload + 4-bit quantization to
  fit large models on smaller GPUs.
- **KEDA / Karpenter / EKS Auto Mode** — event-driven pod autoscaler (queue-depth) / node
  autoprovisioner / managed node lifecycle (riot).
- **AppStream 2.0** — AWS managed application streaming; delivers the interactive ComfyUI UI on a
  per-session GPU.
- **Model vending** — a Lambda that authorizes a team for a model (approval + tag) and returns its
  NFS path (riot).
- **License gate** — a registration/enqueue check that a model's license is accepted before it's
  served.
- **Data flywheel** — deferred loop turning artist accept/correct feedback into labeled training
  data (studio-model-service, not built).
- **HyperPod** — SageMaker resilient multi-node training clusters; the proposed-but-unbuilt
  fine-tune tier.
- **DCC tool** — Digital Content Creation tool (Blender/Unreal/Unity/Maya); the artist's app and
  the client for studio-model-service.

### Source map (where to read deeper)

**studio-model-service (custom scale-to-zero orchestrator):**
- `README.md` / `AGENTS.md` — purpose, topology diagram, gotchas. *Start here.*
- `src/studio_model_service/contract.py` / `registry.py` — the manifest + onboarding seam.
- `orchestrator/app.py` — submit/status/WS surface.
- `orchestrator/worker.py` / `executor.py` / `autoscaler.py` — the scale-to-zero worker,
  claim->commit core, pure scaling decision.
- `.memory/spikes/02-cold-start-comparison.md` — the measured cold-start numbers.
- `runners/native.py` — the real CHORD PBR runner.

**ArtSmoker (artist web studio):**
- `SPEC.md` — full blueprint (architecture, API, pipelines). *Start here.*
- `backend/model_registry.json` — the model/pricing/format-family catalog (`custom_model_catalog`).
- `backend/sagemaker_handlers/inference.py` — the universal data-driven handler.
- `backend/routers/generate.py` — the two-level 2D pipeline + canary + SSE.
- `backend/services/sagemaker_deployer.py` — 1-click deploy lifecycle (HF-pull, NF4, scale-to-zero).
- `backend/services/mesh_export.py` — headless-Blender engine export.

**riot-comfy-ui-platform (ComfyUI platform):**
- `docs/VISION.md` / `docs/comfy-platform-overview.md` / `docs/platform-brief.md` — the three-layer
  design + decision rationale. *Start here.*
- `containers/trellis2-3d/workflow_api.json` — the live image->3D ComfyUI graph.
- `k8s/keda/comfy-scaledobject.yaml` / `k8s/nodepools/gpu-serving.yaml` — GPU autoscaling.
- `lambda/vending/index.ts` + `cdk/lib/vending-stack.ts` — model governance.
- `docs/milestones/hyperpod-finetune-proposal.md` — the proposed (unbuilt) fine-tune tier.

**delirium-world-models-poc (serving side of a real-time model):**
- `gpu/serve_gpu.py` / `gpu/serve_mg3.py` — SSE-streaming FastAPI serving on GPU/H100.
- See the World Models guide for the model internals.

---

## PART 3 — PRIOR ART & GAP-FILLING RESEARCH (2026-09-16)

Added from internal + web research to fill the gaps the repo synthesis surfaced. Full findings
with per-claim `[L#:confidence]` source tags live in `.scratch/research/gaps/`:
`tts-speech-generation.md`, `lora-training-tier.md`, `scale-to-zero-gpu-serving.md`,
`comfyui-at-scale.md`, `image-to-3d-generation.md`.

### Gap 1 — Speech generation (the biggest hole: no TTS in any repo)

- **AWS-native:** **Amazon Polly** (Generative voice engine + a new Bidirectional Streaming API)
  for managed TTS; **Amazon Nova Sonic / Nova 2 Sonic** on Bedrock for real-time *speech-to-speech*
  (Nova 2 GA Dec 2025) — internally noted as the only S2S model on Bedrock. Amazon Transcribe
  covers STT (the one capability ArtSmoker already has).
- **Self-hosted open models (SageMaker GPU):** Chatterbox (MIT), Kokoro-82M (Apache 2.0,
  CPU-capable), XTTS-v2 (MPL, 6 s voice cloning), F5-TTS, Dia-1.6B, CosyVoice2, OpenVoice V2, plus
  Demucs/UVR for source separation.
- **Strong internal prior art:** **Connect UTTS / Lily** (production self-hosted 3P TTS on
  per-cell SageMaker endpoints with response streaming), **Project Svalbard** (managed->self-hosted
  fallback matrix incl. a SageMaker audio-model table), **XBLocalizedVideo** (GPU dubbing pipeline
  with **CosyVoice2** voice cloning via Step Functions + SageMaker Processing Jobs). These are the
  templates to copy if you add speech generation.
- **How it fits the pipeline:** latency-critical conversational voice -> managed Nova Sonic / Polly
  streaming / real-time endpoints (Inference Components scale-to-zero); bursty/batch (dubbing,
  voiceover) -> SageMaker **Async** (MinCapacity 0) or **Processing Jobs** ($0 idle) — the same
  Step Functions + S3 + per-stage-GPU shape as the image/video repos.
- **Remaining gap:** no AWS-native *music/SFX* generation model surfaced (Nova is speech-only);
  some open models carry non-commercial/MPL license caveats.

### Gap 2 — LoRA / fine-tuning: the training tier the platforms defer to

The repos host LoRAs but don't train them. The research gives the concrete answer to "where does
training live?":

- **SageMaker Training Jobs** (ephemeral, pay-per-use, minutes, 1-few instances, warm pools for
  iteration) = **the correct default for a single SDXL/FLUX LoRA**. This directly answers riot's
  own note that "a single-node SageMaker job would be cheaper than HyperPod for a LoRA."
- **SageMaker HyperPod** (persistent SLURM/EKS clusters, auto-recovery, Spot up to ~90% savings,
  reserved training plans, ~40% TCO reduction) = org-scale / continuous / foundation-model
  training. **HyperPod Recipes** bridge both backends from one config.
- **Technique:** LoRA = low-rank adapters on cross-attention (UNet for SDXL, DiT blocks for
  FLUX/SD3); DreamBooth = the 3-5-image subject method; "DreamBooth LoRA" combines them. Canonical
  stacks: HuggingFace **diffusers** (accelerate + PEFT) and **Kohya_ss**. FLUX LoRA is
  memory-heavy (rank-16 can exceed 40 GB VRAM -> A100/H100); SDXL fits on a g5 (24 GB).
- **Strong internal prior art:** broadcast **942863 "Fine-tune SDXL with Kohya"** is a complete
  IaC SageMaker LoRA solution (CloudFormation -> CodeBuild -> ECR -> SageMaker training job runs
  Kohya headless -> safetensors to S3), built precisely because Bedrock/JumpStart couldn't
  fine-tune SDXL. Plus HyperPod fine-tuning platform samples (broadcast 2008368) and the AIM205
  recipes talk.
- **Data flywheel** (studio-model-service's deferred "shown hook"): the self-reinforcing
  serve -> collect feedback -> curate labeled pairs -> retrain -> hot-swap loop; best-documented by
  NVIDIA (NeMo microservices / Data Flywheel Blueprint), but that canon is LLM-centric — **no
  turnkey AWS *image* data-flywheel blueprint exists** (a real gap, and the curation/quality-scoring
  step is unresolved).

### Gap 3 — Scale-to-zero GPU serving: the repos each reinvented a reference pattern

There are **four documented AWS-native scale-to-zero paths** — the custom orchestrators could
likely consolidate onto them:

1. **SageMaker real-time + Inference Components `minCopies=0`** (Nov 2024) — scale-to-zero for
   interactive endpoints.
2. **SageMaker Asynchronous Inference** — native queue + scale-to-zero built in (needs the
   `HasBacklogWithoutCapacity` policy to scale *up* from zero). This is the managed equivalent of
   studio-model-service's whole custom SQS+worker orchestrator.
3. **SageMaker Serverless** — scales to zero but **CPU-only** (fine for Kokoro TTS, not for
   diffusion/LLM GPUs).
4. **EKS Karpenter (nodes) + KEDA (pods to zero)** — exactly riot's pattern; it *is* AWS's own EKS
   reference architecture.
   Plus **Bedrock** (base + Custom Model Import both scale to zero).
- **Cold start is the tax**, dominated by image pull + weight load (>75% of startup). Mitigations
  the repos should know: **SOCI** lazy loading (size-independent pull — but weak for ML that reads
  most of the image), **SageMaker Fast Model Loader** (S3->accelerator, up to 15x faster weights),
  **Container Caching** (up to 56% latency cut).
- **Best internal references:** the wiki **"Deploying Open Models on AWS: A Decision Guide"**
  (`w.amazon.com/bin/view/Ai-inference/decision-matrix/`) is the canonical map of every serving
  option + its scale-to-zero story; the **PSV Production Architecture** page is a real
  HITL-reviewed cost/latency comparison of three scale-to-zero GPU hosting options.
- **Consolidation opportunity:** the three repo reinventions could plausibly collapse onto one
  shared pattern — SageMaker Async for batch + Inference-Component scale-to-zero for interactive.

### Gap 4 — Hosting ComfyUI at scale: three AWS reference samples exist

riot built this from scratch; AWS publishes three reference shapes:

1. **`aws-samples/comfyui-on-eks`** — EKS + Karpenter GPU autoscaling, scale-to-zero, Spot,
   S3-synced-to-node-NVMe models, Mountpoint-S3 for outputs. The closest match to riot's design.
2. **`cost-effective-aws-deployment-of-comfyui`** — ECS + ASG, Cognito/SAML auth, WAF,
   scale-to-zero via CPU alarm; explicitly flags the **ALB 60 s idle-timeout WebSocket trap**
   (riot hit the same and set 3600 s).
3. **`sample-comfy-to-sagemaker-processing-job`** — batch, pay-per-second ephemeral GPU jobs.
- **Headless API surface (official):** `POST /prompt` -> `prompt_id`, WebSocket `/ws`
  (status/progress/executed), `GET /history/{id}`, `GET /view`, plus `/object_info` (node-schema
  introspection — key for a platform) and `/free` (VRAM unload). Workflows must be exported in
  **"API format"** JSON. **Core ComfyUI has no auth** — an internet-exposed instance is a
  CRITICAL security finding (internal Palisade rule).
- **Workflow/model management:** pin ComfyUI + custom nodes + deps + models to **immutable commit
  SHAs** in one image (mixed versions silently change sampler/seed behavior); allowlist custom-node
  class names before enqueue (arbitrary-code-execution surface).
- **Strong internal prior art:** an **APG** config-driven batch pattern (ComfyUI headless +
  ComfyScript + queue-poll on SageMaker), the **CoREL/NARA** Slurm cluster's ComfyUI preset, and
  **AWS Deadline Cloud + ComfyUI** (NAB 2026 talk). Note: the `riot-comfy-ui-platform` repo itself
  did not surface in InternalSearch — likely a private GitFarm package, not that it's absent.

### Gap 5 — image->3D (the common denominator): landscape, licensing, and the cleanup tax

- **Two model families:** native-3D latent generation (Hunyuan3D-DiT, TripoSG, TRELLIS/SLAT) vs
  feed-forward LRM reconstruction (TripoSR ~0.5 s, SF3D 0.3-0.5 s). Frontier = **TRELLIS.2** (4B,
  O-Voxel, full PBR) and **Hunyuan3D-2.1/2.5** (production PBR).
- **Licensing is the headline decision:** TRELLIS / TripoSR / TripoSG are **MIT/permissive**;
  **Hunyuan3D is Tencent NON-COMMERCIAL** with an EU/UK/South Korea territorial carve-out — a real
  clearance gate before internal production use. (ArtSmoker already flags this; riot stages
  Hunyuan3D but hasn't wired it.)
- **Technical approach:** 3D VAE (3DShape2VecSet latents) -> rectified-flow/flow-matching DiT ->
  marching cubes/FlexiCubes; SLAT = sparse voxel grid + multi-view features decodable to
  Gaussians/meshes; DINOv2/**DINOv3** image conditioning; texture/PBR as a decoupled second stage.
- **The cleanup tax is universal:** raw AI meshes are "triangle-soup blobs" with no clean UVs and
  invalid PBR. Every pipeline needs a downstream **retopo -> poly-budget/LODs -> re-UV -> PBR
  correction -> scale/pivot -> collision -> GLB export** pass (GLB excludes lights/cameras) — which
  Amazon has already codified in artist SOPs (3D Digital Studio / KRYTEN / Woodshop GLB QA). This
  is exactly what ArtSmoker's headless-Blender engine export automates.
- **Strong internal prior art:** **IML-Australia "Generate 3D assets from product images"** (a
  CLAY-like two-stage ShapeVAE + flow-DiT model with DINO-v2, targeting Bedrock via AGI), plus a
  **GDC 2025** games demo (TRELLIS via SageMaker) and a GameCraft hackathon (TRELLIS on EC2).
