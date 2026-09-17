# ArtSmoker — Research Findings

Repo explored: `/local/home/sabiggin/code/teach-me/.references/ArtSmoker` (symlink → `/local/home/sabiggin/code/ArtSmoker`). Read-only; no files modified.
Sources: `README.md`, `SPEC.md`, `backend/` (config, services, routers, sagemaker_handlers), `backend/model_registry.json`, `api-samples/skill.md`, `pyproject.toml`, plus the repo's own prior exploration notes in `.scratch/explore/` (which carry verified `file:line` refs I cross-checked against the code).

## Purpose

ArtSmoker is a self-hosted, artist-first web studio that wraps the newest generative-media models behind one clean UI so game/media creative teams can go from a plain-language prompt to production-ready 2D art, edited variants, cinematic video, and fully-textured game-engine-ready 3D models — with no prompt engineering, GPU management, or pipeline wrangling of their own (`README.md:11-33`, `SPEC.md:1`). It connects only to the user's own AWS account: heavy compute runs on Amazon Bedrock (managed) or on Amazon SageMaker GPU endpoints ArtSmoker deploys and scales to zero, so artwork/prompts/IP stay in the user's environment (`README.md:33`, `SPEC.md:112-170`). It is inference/hosting orchestration only — there is no model training or LoRA fine-tuning of the user's own art (verified below).

## Architecture & Components

**Stack** (`SPEC.md:9-21`, `pyproject.toml`): Python 3.11+ FastAPI backend (Pydantic v2, `async def` routes, synchronous blocking Bedrock service calls), vanilla-JS + Tailwind-CDN frontend (no build step, IIFE components on `window`, wired by `app.js`). Run-in-place app driven by `requirements.txt` — `pyproject.toml` intentionally has no `[project]`/`[build-system]` table (only linter/scanner config).

**Backend structure** (`SPEC.md:60-140`, `backend/` listing):
- `main.py` — FastAPI app, CORS, lifespan, static mount; `config.py` — `Settings` (Pydantic-settings, `ARTSMOKER_` env prefix, `.env`); `APP_VERSION="1.9-20260907_05"` (`backend/config.py`).
- `routers/` — one per surface: `generate.py` (2D options×variations + image editing, 139KB), `generate_3d.py` (image-to-3D, 107KB), `video.py`, `chat.py`, `typestudio.py`, `styles.py`, `gallery.py`, `browse.py`, `transcribe.py`, `refine.py`, `custom_deploy.py` (1-click SageMaker deploy, 71KB), `admin.py` (registry + Bedrock discovery, 154KB).
- `services/` — the engine: `bedrock_client.py` (generic `invoke_llm`/`invoke_image_model`), `image_generator.py` (retry/backoff + moderation classifier), `prompt_engineer.py` (decompose/recompose/enhance/concepts + negative-prompt synthesis), `style_analyzer.py` (two-phase vision style profiling), `video_generator.py` (async Bedrock video), `sagemaker_deployer.py` (endpoint lifecycle, 139KB), `sagemaker_invoker.py`, `async_jobs.py` (S3-persisted async job tracker, 75KB), `custom_models.py` (catalog), `model_detector.py` (HF auto-detect), `mesh_export.py` (GLB→FBX/USDZ via headless Blender), `post_processor.py` (bg-remove/upscale/SVG), `cost_tracker.py`, `prompt_translator.py`, `prompt_templates.py`, `model_registry.py`, `auto_update.py`, `mantle_client.py` (OpenAI-compatible Bedrock Mantle for GPT-5.x-class models).
- `sagemaker_handlers/inference.py` (272KB) — ONE universal, data-driven handler packaged into every endpoint's `model.tar.gz`; dispatches on `INFERENCE_LIBRARY`/`PREDICTOR_TYPE` env set from the catalog (`backend/sagemaker_handlers/inference.py:1-30`). `bundled_packages/` vendors the 3D CUDA stacks: `triposg`, `hy3dpaint`, `mvadapter`, `stablex`.
- `models/` — Pydantic request/result models (`generation_request.py`, `generation_result.py`, `style_profile.py`); `storage/local_store.py` — local FS with S3-compatible interface.
- Two persisted JSON config files: `model_registry.json` (392KB — all models/regions/pricing/format-families) and `prompt_templates.json` (64KB — 28 editable LLM directive prompts).

**Frontend structure** (`SPEC.md:140-170`): single-page `index.html`; `js/app.js` router + `js/components/` studios (`ImageStudio`, `VideoStudio`, `ChatStudio`, `TypeStudio`, `StyleLibrary`, `Gallery`, `PromptDesigner`, `PromptEditor`, `VoiceInput`); `js/i18n/` with 9 languages (en/ja/zh/ko/fr/es/hi/ru/de, 817+ keys).

**Data/storage** (`SPEC.md:165-175`, `config.py`): `data/styles/` (profiles + refs), `data/generated/` (PNG/SVG + GLB + engine exports + per-version metadata), `data/video/` (MP4 + thumbnails + job meta), `data/chat/`; plus an S3 bucket (required for async Bedrock video invoke and SageMaker async I/O).

## Generative Media Pipeline Aspects

### Media types generated
2D images (PNG + true-vector SVG), edited image versions (inpaint/outpaint/erase/search-replace/recolor), video (MP4), text overlays (Type Studio), and textured 3D meshes (GLB with embedded PBR, exportable to FBX/USDZ per engine) (`README.md` features, `SPEC.md:112-170`).

### Model backends — two worlds behind one registry
1. **Amazon Bedrock (managed, synchronous)** (`SPEC.md:150-165`): image — Stable Diffusion 3.5 Large, Stable Image Ultra, Stable Image Core, Amazon Nova Canvas, Stability editing services (inpaint/outpaint/erase/search-replace/recolor/upscale/bg-remove); video — Nova Reel v1.0/v1.1 (single/multi-shot, image-to-video), Luma AI Ray v2.0; LLM — Claude Sonnet (fast: refine/hints/cohesion/chat) + Opus (complex: style analysis Phase 2, concept generation) + 80+/99 chat LLMs across 16 providers for Chat Studio; Nova Sonic — bidirectional-streaming speech-to-text (`backend/services/transcriber.py`, needs the experimental `aws_sdk_bedrock_runtime` Smithy SDK).
2. **Self-hosted on Amazon SageMaker (async, scale-to-zero)** (`model_registry.json` `custom_model_catalog`, key entries at lines ~9456+): FLUX.1 [schnell] (Apache-2.0), FLUX.1 [dev] (non-commercial), FLUX.2 [dev] (32B, NF4, Mistral-3 text encoder), HunyuanImage 3.0 (BF16 80B MoE / NF4), Qwen-Image + Qwen-Image-Edit (Apache-2.0, instruction editing), and image-to-3D: TripoSG (geometry, MIT) and TRELLIS.2 (geometry + PBR in one model, MIT model but non-commercial nvdiffrast bake). Post-processing bundles: Real-ESRGAN (upscale), RMBG-2/BiRefNet (bg-remove), CodeFormer (face restore), Depth-Anything-v2, SAM2.

### 2D generation pipeline — "two-level" options × variations
For each prompt the LLM produces N distinct **Options** (genuinely different concepts, e.g. "warrior" → Viking / samurai / cyber-soldier) and the image model produces M **Variations** (seed variants) per option; both clamp 1..5 → up to 25 images/batch (`README.md:1.3`, `SPEC.md:4.2`, `backend/models/generation_request.py`). Pipeline stages (`.scratch/explore/backend-pipeline.md`, verified against `backend/routers/generate.py`): language detect/translate → asset-type classify → Prompt Designer decompose (subject/scene/composition/lighting/style, each field `{value, source=user|inferred}` with lock/vary) → recompose → per-model LLM enhance (+ negative-prompt synthesis by stripping negation phrases) → **canary** single-image moderation probe → parallel `ThreadPoolExecutor` batch → post-process (bg/upscale/SVG) → store with 3-level prompt lineage (`original → recomposed → enhanced`). Streamed over SSE with event types `started/stage/prompts_ready/canary/image_done/model_status/async_submitted/moderation_blocked/prompt_refused/complete`.

### Image editing & reference-guided
Mask-based Bedrock editors (Stability) plus mask-free instruction editors (Qwen-Image-Edit) support all five modes — including true canvas extension via a pre-pad-noise → complete-only-new-band → feather-blend-original recipe (`backend/services/instruction_outpaint.py`, validated recipe in its docstring). Reference images: "Match" (pixel-faithful edit) vs "Inspired by" (vision-LLM writes the prompt).

### 3D pipeline (image → textured GLB)
`/api/generate/3d` (async, SageMaker) (`SPEC.md:134`, `backend/routers/generate_3d.py`). Two deployable pipelines: **TripoSG** (rectified-flow SDF transformer geometry, loaded fp32, marching-cubes at `dense_octree_depth` 7/8/9 ← frontend `mesh_resolution` 128/256/512) + a chosen texture backend (`trellis2` default / `hunyuan` non-commercial / legacy `mvadapter`); and **TRELLIS.2 Full** (geometry + PBR SLAT in one model, DINOv3 encoder → mandatory "Built with DINOv3" attribution baked into asset metadata). Backend-specific CUDA ops (`custom_rasterizer`, `nvdiffrast`, `o_voxel`/`cumesh`/`flex_gemm`) build at load time and are S3-cached, arch-namespaced by GPU compute capability. Includes a vision "smart source completion" step: crops are detected and offered outpainting before 3D so a legless character doesn't become a legless mesh (`README.md` feature, `generate_3d.py`). **Engine export** via headless Blender (`backend/services/mesh_export.py`, `blender/convert.py`): targets generic/Unreal(Z-up)/Unity/Godot/Maya/3ds Max with correct axes; prep ops = per-engine texture packing (Unreal ORM, Unity metallic+smoothness-in-alpha, HDRP mask map), LOD chains, convex/CoACD collision hulls (`UCX_*`), UV2 (`SPEC.md:1571-1572`).

### Video pipeline
`backend/services/video_generator.py` uses Bedrock `StartAsyncInvoke` for Nova Reel and Luma Ray, downloads output from the S3 bucket, and generates thumbnails via ffmpeg subprocess; all invocation params come from the registry (no hardcoded structures).

### 1-click self-hosting / deploy lifecycle (the standout capability)
`custom_deploy.py` → `sagemaker_deployer.py` (`.scratch/explore/3d-and-deploy.md`, verified): packages the universal `inference.py` + generated `requirements.txt` + `invoke_config.json` + bundled CUDA packages into a tiny `model.tar.gz`; **weights are pulled directly from HuggingFace at container start** (`ARTSMOKER_HF_REPO`, deliberately not `HF_MODEL_ID`), so GB of weights never touch the app host. Handles: quantization/offload (NF4, `ENABLE_MODEL_CPU_OFFLOAD`, a generic `BlockOffloadManager` sliding-window GPU↔CPU offload with CUDA-stream prefetch — `inference.py:139`), DLC image resolution from ECR, SageMaker execution-role auto-create, **scale-to-zero autoscaling registered only after the model confirms loaded** (so scale-in can't kill a 5–60-min load) with a deploy grace window, CloudWatch alarms, auto-teardown on failed deploy, HF gated-access pre-check across the full dependency closure (incl. transitive gated deps like DINOv3), encrypted HF token in Secrets Manager, dev keep-warm + S3 hot-reload overlay, and unified cost accounting. Self-hosted endpoints register into the SAME `model_registry.json` studio sections as Bedrock models (`model_source="custom_hosted"`, `format_family="sagemaker_<type>"`), so they appear in the same dropdowns/cost/moderation/gallery and route transparently.

### LoRA / training — NOT present in ArtSmoker's own code
ArtSmoker does no training or LoRA fine-tuning. Every `lora`/`training` grep hit is inside **vendored upstream ML packages** under `backend/sagemaker_handlers/bundled_packages/` (TripoSG, hy3dpaint, mvadapter model definitions) — snapshots ArtSmoker neither authors nor lints (`pyproject.toml` bandit `exclude_dirs`). "Custom models" means *hosting* fine-tuned/imported/deployed Bedrock/HF models, not producing them. Style consistency is achieved by **LLM-reasoned vision style profiling → text directive** (a prompt prepended to every generation), explicitly a different mechanism than A1111-style embedding/LoRA style transfer (`.scratch/explore/prompts-moderation-registry.md`, `backend/services/style_analyzer.py`).

### API shape (`api-samples/skill.md`, `SPEC.md:5`)
REST/JSON, base `http://localhost:8000`, auto-generated Swagger at `/docs`; snake_case fields. Core flow: `GET /api/admin/models/image-options` → `POST /api/refine-prompt/classify-asset-type` → `POST /api/refine-prompt/decompose` → `POST /api/generate/stream` (SSE) → `GET /api/generate/async-jobs` (poll SageMaker jobs) → `GET /api/gallery/{asset_id}/png`. Bedrock images return inline; SageMaker returns an `async_submitted` sentinel + `job_id` (jobs persisted to S3 at submit, survive restarts). Sample clients shipped in Python, Node, Go, Rust (`api-samples/imageGen_*.{py,js,go,rs}`).

## World Model Relevance

No world-model / physics-simulation / scene-graph capability — ArtSmoker generates **assets**, not simulated environments (searches for "world model"/"simulation"/"physics"/"scene graph" return only game-engine *import* language, not simulation). Adjacent-but-not-equal relevance for a world-model context:
- **Image-to-3D as a spatial-lifting primitive**: single 2D image → textured 3D mesh via multi-view synthesis (TripoSG/TRELLIS.2) is the same family of "infer 3D structure from a 2D observation" used in some world-model asset pipelines (`SPEC.md:162-163`, `generate_3d.py`).
- **Game-engine-tailored output** (Unity/Unreal/Godot with correct up-axis, LODs, collision proxies, engine texture packing) means generated assets can drop straight into an engine that *hosts* a simulation/world model (`SPEC.md:1571-1572`) — ArtSmoker is an asset feeder, not the simulator.
- **Multi-view synthesis + texture baking** (mvadapter/hy3dpaint bundled packages) is the closest thing to view-consistent scene reasoning, but it is per-object mesh generation, not a persistent world state.

## Key Terms & Jargon

- **Two-level generation (Options × Variations)** — Options = distinct LLM-authored *concepts*; Variations = *seed* variants of one concept (`SPEC.md:4.2`).
- **Prompt Designer** — UI that decomposes a prompt into editable fields (subject/scene/composition/lighting/style) with per-field lock/vary toggles (`README.md`, `backend/services/prompt_engineer.py`).
- **Format family** — a registry JSON template (`body_template` + typed param paths) that lets one generic invoker call any model with zero new code; 17 families (`model_registry.py:_DEFAULT_FORMAT_FAMILIES`).
- **Canary (moderation)** — one probe generation before the full batch; a moderation block aborts the batch, wasting 1 call not N×M (`backend/routers/generate.py:655`).
- **Scale-to-zero endpoint** — a SageMaker async endpoint with MinCapacity=0; $0 idle, cold-starts from zero on demand (`sagemaker_deployer.py:_setup_auto_scaling`).
- **Async job sentinel** — `{"async_submitted": true, "job_id": ...}` returned instead of image bytes for SageMaker models; a background poller finalizes to the gallery (`backend/services/async_jobs.py`).
- **BlockOffloadManager** — generic sliding-window GPU↔CPU block offload with CUDA-stream prefetch, fits large models on smaller GPUs (`sagemaker_handlers/inference.py:139`).
- **NF4 / BF16** — 4-bit NormalFloat quantization (cost/VRAM) vs bf16 (best quality); per-model in the catalog (`model_registry.json` flux2_dev/hunyuan entries).
- **SLAT** — Structured LATent texturing used by TRELLIS.2 for voxel-conditioned PBR (`model_registry.json` trellis2 entry).
- **PBR / GLB / ORM** — physically-based-rendering textures; GLB = binary glTF (WebP-encoded atlas via `EXT_texture_webp`); ORM = AO/Roughness/Metallic packed texture for Unreal (`SPEC.md:1540,1572`).
- **HF-direct-pull packaging** — ship KB of handler code; container downloads weights from HuggingFace at startup via `ARTSMOKER_HF_REPO` (`sagemaker_deployer.py:upload_handler_to_s3`).
- **Mantle** — Bedrock's OpenAI-compatible + Anthropic-Messages endpoint (bearer-token auth) used only for models Converse can't reach, e.g. GPT-5.x (`backend/config.py`, `mantle_client.py`).
- **Style profile / cohesion check** — two-phase vision analysis (Sonnet cohesion → Opus 9-attribute profile) distilled to a ≤200-word text directive prepended to generations (`backend/services/style_analyzer.py`).

## Notable Files

- `SPEC.md` — 298KB complete rebuild blueprint: architecture (§2), project structure (§3), component design (§4, incl. 4.2 two-level pipeline), full API reference (§5), self-hosted §5.10 / async jobs §5.11, pricing §14.
- `backend/model_registry.json` — single source of truth; `custom_model_catalog` at line ~9456 (FLUX/Hunyuan/Qwen/TripoSG/TRELLIS.2 entries + bundles + `dedicated_models`).
- `backend/sagemaker_handlers/inference.py` — universal data-driven inference handler for ALL endpoints (`BlockOffloadManager` @139, TRELLIS.2 loader @1704, TripoSG loader @1773, marching-cubes predict @3591, `predict_fn` dispatch @5378).
- `backend/routers/generate.py` — 2D options×variations pipeline, canary, cooperative-cancel, SSE, moderation cascade.
- `backend/routers/generate_3d.py` — image→GLB async orchestration, sub-versioning, DINOv3 attribution, licence resurface.
- `backend/routers/custom_deploy.py` — 1-click deploy/teardown/status; HF gated-access pre-check; registers endpoints into the shared registry.
- `backend/services/sagemaker_deployer.py` — 139KB endpoint lifecycle: packaging, DLC resolution, scale-to-zero ordering, Secrets-Manager HF token, teardown/orphan sweep.
- `backend/services/async_jobs.py` — S3-persisted async job tracker: dedup finalization, durability-before-delete, stale resubmit, host-save backoff.
- `backend/services/instruction_outpaint.py` — mask-free canvas-extension recipe (pre-pad → complete-band → feather-blend).
- `backend/services/prompt_engineer.py` / `prompt_templates.py` / `prompt_templates.json` — LLM orchestration + 28 editable directive templates with variable validation.
- `backend/services/style_analyzer.py` — two-phase cohesion-aware vision style profiling with smart sampling.
- `backend/services/mesh_export.py` + `services/blender/convert.py` — headless-Blender GLB→FBX/USDZ engine export.
- `api-samples/skill.md` + `imageGen_{python,node,go,rust}.*` — external API contract + working client samples.
- `backend/config.py` — `Settings`, AWS regions, Blender provisioning, scale-to-zero grace, `APP_VERSION`.
- `.scratch/explore/{backend-pipeline,3d-and-deploy,prompts-moderation-registry,frontend-studios}.md` — the repo's own prior deep-dive notes with verified `file:line` refs (highly reliable secondary source; cross-checked against the code).
