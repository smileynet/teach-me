# studio-model-service — Exploration Findings

Repo (symlink target): `/local/home/sabiggin/code/studio-model-service`
Explored: README.md, AGENTS.md, `.memory/` (PLAN, CONTEXT, ADRs, spikes), full `src/studio_model_service/`, `tools/`, `tests/`, `mise.toml`, `requirements*.txt`.

## Purpose

Studio Model Service is a **scale-to-zero AI model inference platform** that hosts generative art models on GPUs and serves them to DCC (Digital Content Creation) tools — Blender first — through one versioned API, so a working artist gets the capability *inside their tool* without cloning repos, managing CUDA, or downloading weights (`README.md` lines 1-45; `AGENTS.md` "What this project is"). It turns "a research model on a GPU" into "a versioned API endpoint a Blender plugin calls," while the GPUs behind it drop to ~$0 cost when idle (`.memory/PLAN.md` "Vision"). It is explicitly framed as a **reference-architecture demo for Ubisoft** — compare the tradeoffs of scale-to-zero model hosting, not ship a single-SLA product (`.memory/PLAN.md` framing note; `.memory/adr/0004-reference-architecture-demo.md`).

## Architecture & Components

The system splits into an **orchestrator** (FastAPI control/submit plane) and a separate **GPU worker** process that consumes a queue, per the topology diagram in `README.md` (lines ~97-115): `Blender/DCC client → API GW (Cognito JWT) → Orchestrator (Fargate/FastAPI) → SQS FIFO → GPU workers (ECS/EC2 Spot) → model runner; weights S3→NVMe; WS relay for job events`.

Key modules in `src/studio_model_service/`:

- **`contract.py`** — the typed job/output contract + model manifest, as stdlib dataclasses with explicit `validate()` (kept dependency-free per demo-mode discipline; documented Pydantic-mappable for the real FastAPI service). Defines closed vocabularies: `RunnerType` (comfyui/native/mock), `InputType` (image/prompt/mesh), `OutputKind` (pbr_map_set/mesh/texture), `JobState`, `JobStage`. Core types: `ModelManifest` (the registry entry: model_id, integer version, runner, inputs, output, `WeightsDecl`, `LicenseDecl`), `WeightsDecl`/`WeightAsset` (a full weight dependency LIST — checkpoint + vendored base configs, so a hosted model never depends on a live community mirror; `contract.py` docstring cites the spike-03 RedbeardNZ 404), and `JobResult.conforms_to(manifest)` which enforces produced artifacts match declared roles/content-types (`src/studio_model_service/contract.py`).
- **`registry.py`** — the `ModelRegistry`, "the onboarding seam" (ADR 0003). Two sub-registries (sbin idioms): a runner instance registry keyed by runner_type, and a manifest store keyed by (model_id, version) with integer versioning + pinned default + aliases. Enforces the **license gate at registration** (`register_model` → `manifest.validate()` → `license.validate()`), resolves runners honoring pause-state + a circuit breaker, and exposes pause/enable for the operator console (`src/studio_model_service/registry.py`).
- **`bootstrap.py`** — registry bootstrap; onboards CHORD and TripoSR through the *identical* `register_model()` path (proving the rule-of-two seam: a pbr_map_set model and a mesh model need no core changes). `build_demo_registry()` swaps both models' runner to `mock` so the full submit→result loop closes with no GPU/creds (`src/studio_model_service/bootstrap.py`).
- **`roles.py`** — the single source of truth for the 5 canonical PBR map role names (`base_color, normal, roughness, metallic, height`); pinned because the running Blender client is the authority (L1 observable > L2 spec) and spike-05 caught the contract drifting (`src/studio_model_service/roles.py`).
- **`resilience.py`**, **`errors.py`** — circuit breaker + structured platform errors (inherited from the sbin prior art).
- **`orchestrator/app.py`** — the FastAPI orchestrator (app factory + injected `Dependencies`, no AWS client at import time). ONE generic submit surface, never per-model endpoints. `Dependencies.demo()` wires in-memory backends + `LocalProcessor`; `Dependencies.aws()` wires the live adapters (DynamoDB/SQS/Cognito/API-GW-WS) and has NO processor because the GPU worker is a separate process (`src/studio_model_service/orchestrator/app.py`).
- **`orchestrator/worker.py`** + **`worker_main.py`** — the scale-to-zero GPU worker: SQS long-poll loop, per-message heartbeat thread that extends visibility (cold-start p95 342s > 300s visibility timeout — the landmine), outcome-driven message lifecycle, Spot-interruption/SIGTERM drain, and dead-worker recovery via SQS visibility + conditional stale-reclaim (NOT a reaper — mixing both double-runs jobs). `worker_main.py` is the container entrypoint (`python -m studio_model_service.orchestrator.worker_main`) with a fail-fast env preflight (`src/studio_model_service/orchestrator/worker.py`, `worker_main.py`).
- **`orchestrator/executor.py`** — `JobExecutor`, the transport-agnostic `claim→stage→load→infer→commit→emit` core shared by both the in-process `LocalProcessor` and the real `Worker`. Returns an `Outcome` and stays out of the message-delete decision (`src/studio_model_service/orchestrator/executor.py`).
- **`orchestrator/queue.py`** — `JobQueue` abstraction + versioned wire `Envelope` (carries model+version, inputs as S3 references never bytes) + `InMemoryQueue` FIFO backend; distinguishes malformed (delete) vs unknown-version (leave for redelivery) envelopes (`src/studio_model_service/orchestrator/queue.py`).
- **`orchestrator/store.py`** — `JobStore` conditional-write state machine (PENDING→QUEUED→RUNNING→terminal; work-done-wins; `reclaim_if_stale`/`touch` liveness). In-memory backend; DynamoDB adapter mirrors it (`src/studio_model_service/orchestrator/store.py`).
- **`orchestrator/autoscaler.py`** — queue-depth autoscaler as a PURE decision function (`desired_worker_count`) + a `LaunchController` seam. Two mechanisms: 0↔1 scale-to-zero and 1↔N backlog, with asymmetric cooldowns (scale out fast, in slow) and an in-flight guard that never scales in below running workers with claimed jobs. `ScalingStrategy` (SCALE_FROM_ZERO vs WARM_POOL) is a config dial, not a baked pick (`src/studio_model_service/orchestrator/autoscaler.py`).
- **`orchestrator/metrics.py`** — per-model `MetricsEmitter` (CloudWatch with structured-log fallback), dimensioned by Model+Version(+InstanceType); records inference latency, VRAM peak, outcome counts; stubbed pass-2 extension points for cold-start-phase and cost-per-job (`src/studio_model_service/orchestrator/metrics.py`).
- **`orchestrator/auth.py`** — `TokenVerifier` (fail-closed; DemoVerifier + Cognito adapter), `Principal` with `org_id` tenancy claim, and the normalized `JobEvent` + `EventRelay` WS abstraction (`src/studio_model_service/orchestrator/auth.py`).
- **`orchestrator/adapters/`** — the live-AWS adapters behind the same interfaces: `dynamodb_store.py`, `sqs_queue.py`, `apigw_ws.py`, `cognito_auth.py`, and `fleet_launcher.py` (the live `LaunchController` that acquires GPUs via a diversified EC2 Fleet). Imported LAZILY so the worker image carries no web/auth deps (`src/studio_model_service/orchestrator/adapters/`).
- **`runners/`** — the runner abstraction (ADR 0003/0005): `base.py` (`Runner` ABC + `StageResult`/`InferResult` envelope), `native.py` (the REAL CHORD PyTorch runner), `ComfyUIRunner`/`MockRunner` in `__init__.py`, `native_height.py` (normal→height derivation) (`src/studio_model_service/runners/`).

## Generative Media Pipeline Aspects

**What is served:** heterogeneous generative *art* models behind one uniform contract. The two seed models (`bootstrap.py`) span the output-shape spectrum:
- **CHORD** — image → **PBR material map set** (5 svBRDF maps: base_color, normal, roughness, metallic, height). Ubisoft La Forge's SIGGRAPH-Asia-2025 material-estimation model; runner=native, research-only license (`bootstrap.py:chord_manifest`; `.scratch/chord-research.md`).
- **TripoSR** — image → **3D mesh** (model/obj + optional texture/material); MIT license, chosen for maximum output-shape contrast to prove the runner seam is not CHORD-shaped (`bootstrap.py:triposr_manifest`; `.memory/PLAN.md` open-questions #5).

**How models are hosted/served (the serving path):**
1. **Onboarding, not endpoints** — an ML engineer publishes a model once as a `ModelManifest` (weights location, runner, typed I/O contract, license gate); `register_model()` is the only path, adding a model never adds an endpoint (`registry.py`; ADR 0003).
2. **Submit API** — `POST /v1/models/{model_id}/{version}/jobs` validates model+version against the registry, enforces the **license gate before enqueue**, validates inputs against the declared contract, requires image/mesh inputs to be **S3 references not inline bytes**, supports an `Idempotency-Key`, creates a PENDING row, enqueues, marks QUEUED (`orchestrator/app.py:submit`).
3. **Status** — `GET /v1/jobs/{job_id}` is authoritative status (ownership-as-404 across orgs); `DELETE` cancels; there are control-plane routes `/v1/control/models/{id}/pause` and `/v1/control/jobs/{id}/rerun` for the operator console (`orchestrator/app.py`).
4. **Progress stream** — `WS /v1/jobs/{job_id}/events` (auth via query-string ACCESS token) sends the current snapshot then streams normalized `JobEvent`s until a terminal state ("poll-then-WS": WS resumes from authoritative state) (`orchestrator/app.py:job_events`; `AGENTS.md` WS authorizer gotcha).
5. **Execution** — a GPU worker claims a message (conditional QUEUED→RUNNING), runs the runner lifecycle `stage() → load() → infer()`: S3/HF→NVMe weight staging, load-once model construction, per-job inference, then S3 upload of outputs and a conditional RUNNING→COMPLETE commit with the typed artifact list as references (`orchestrator/executor.py`; `runners/native.py`).

**Image-generation / material-estimation specifics (CHORD `NativeRunner`, `runners/native.py`):**
- `stage()` downloads the gated CHORD checkpoint (`Ubisoft/ubisoft-laforge-chord`, `chord_v1.safetensors`, ~2.76 GB) to NVMe, plus SD-2.1-base **config + tokenizer ONLY** (never base weights — asserts no `.safetensors/.bin/.ckpt/.pt` leaked into the staged base dir).
- `load()` fails fast if `torch.cuda.is_available()` is false (never a silent CPU fallback), builds `ChordModel` from the OmegaConf config, and overrides `model.stable_diffusion.hf_key` to the staged local base-config dir so CHORD loads offline (`local_files_only`) instead of the dead RedbeardNZ mirror.
- `infer()` reads the S3-referenced input image, runs the model at a configurable resolution (default 1024) under `torch.autocast`, saves the 4 native CHORD maps under **canonical role names** via `_CHORD_TO_CANONICAL` (basecolor→base_color, metalness→metallic, etc.), derives the 5th map (height) from the normal map (`native_height.normal_to_height`), uploads 5 PNGs to S3, and returns metrics including `vram_peak_gib`.
- Heavy deps (torch, chord, PIL, huggingface_hub) are imported INSIDE the lifecycle methods so the module unit-tests on a host with no GPU.

**Two runner strategies (ADR 0005 "compare, don't pick"):**
- **native** (in-process PyTorch) — the shipped real runner; spike-03 chose it for lower latency.
- **comfyui** — out-of-process ComfyUI HTTP runner; stub in `src/` but a working prototype exists in `tools/spike03/comfy_runner.py` (uploads image, POSTs the CHORD node-graph workflow in API format, polls `/history`, downloads the 5 maps). This is the near-term substrate because CHORD ships a ComfyUI node and artist-pipeline already runs ComfyUI-on-Spot.
- **mock** — demo-mode runner, fully functional with no GPU, returns reference artifacts for every declared role.

**Worker container (`tools/worker/Dockerfile`):** `nvidia/cuda:12.8.1-runtime-ubuntu24.04`, torch+torchvision from the same cu128 index, CHORD runtime deps pinned (diffusers 0.35.2 to avoid the 0.36 import break), CHORD code cloned to `/opt/chord`, our `src/` baked, weights NOT baked (staged at runtime). CMD is the worker daemon. Built/pushed via `tools/worker/build-push.sh`.

**LoRA / training:** No LoRA training or fine-tuning is implemented in `src/`. Training is a deliberately-deferred secondary "data flywheel" deliverable — an opt-in loop where artist accept/correct feedback becomes labeled training data, reduced for the demo to "a shown hook" (`.memory/CONTEXT.md` "Data flywheel"; ADR 0006; `.memory/PLAN.md` JM-4). The README notes artist-pipeline (prior art) has LoRA training to lift from later, and the architecture diagram shows "fine-tune on the same GPU capacity" as a future path — but none is present here.

**Cold start as a first-class SLO (`.memory/spikes/02-cold-start-comparison.md`, measured n=10 each):** scale-from-zero p95 **342s** ($0 idle) vs warm-pool STOPPED p95 **150s** (~$10-15/mo/worker EBS). docker pull of the 6.3 GB image dominates true cold-start (~137s, ~40% of it) — hence the SOCI parallel-pull ticket. Hibernate is unsupported on all G-family GPUs; CRIU is feasible but not turnkey. GPU capacity droughts are common → acquisition is a **diversified EC2 Fleet** across instance families/AZs (OD→Spot), not single-type run-instances.

## World Model Relevance

Low-to-none directly. This is a **serving/hosting platform for generative *art* models** (2D PBR material maps, image→3D mesh), not a world model / video-generation / interactive-simulation system. There is no world-model, video-generation, action-conditioned prediction, or agent-simulation code anywhere in the repo. The relevance is indirect and structural: the platform is model-agnostic by design (uniform manifest + runner seam + typed I/O contract + scale-to-zero GPU serving), so its patterns — versioned model registry, S3→NVMe weight staging, cold-start-optimized scale-to-zero GPU workers, queued inference with WS progress, per-model observability — are exactly the infrastructure pieces one would reuse to *serve* a large world/video model. The contract's `OutputKind` vocabulary (pbr_map_set/mesh/texture) is closed and art-shaped; a world/video output would be a new `OutputKind` + runner, which the rule-of-two onboarding path is explicitly built to accommodate (`contract.py`, `bootstrap.py`). No mention of world models in README, AGENTS, PLAN, CONTEXT, ADRs, or spikes.

## Key Terms & Jargon

- **Scale-to-zero** — GPU worker count drops to 0 when the queue is empty (idle cost ≈ $0); queue depth drives launch (`.memory/CONTEXT.md`; `autoscaler.py`).
- **Cold start** — elapsed time from "job queued, no warm worker" to "first inference result" (a measured SLO, not container-start; `.memory/spikes/02`).
- **S3→NVMe staging** — model weights kept in S3/HF and copied to the worker's local NVMe at container start, never baked into images (`.memory/CONTEXT.md`; `runners/native.py:stage`).
- **Runner** — a model's execution strategy on a worker: `native` (in-process PyTorch), `comfyui` (out-of-process HTTP), or `mock` (demo). Analogous to a pluggable backend (`runners/base.py`; ADR 0003/0005).
- **Model registry / manifest** — the catalog mapping model_id+version → runner, typed contract, weights dependency list, and license gate; onboarding a model is a manifest, never a new endpoint (`registry.py`, `contract.py`).
- **PBR material / svBRDF maps** — the *set* of texture maps describing how a surface reacts to light (base_color, normal, roughness, metallic, height); CHORD's output (`roles.py`; `.memory/CONTEXT.md`).
- **CHORD** — Ubisoft La Forge's diffusion-based PBR material-*estimation* model (single texture image → 5-map set); the motivating hosted model; research-only license (`.scratch/chord-research.md`).
- **TripoSR** — MIT-licensed image→3D-mesh model; the second seed model, chosen for output-shape contrast (`bootstrap.py`).
- **License gate** — a registry check enforced at registration that a model's license is accepted before it can be served (`registry.py`; `contract.py:LicenseDecl.validate`).
- **DCC tool** — Digital Content Creation tool (the artist's app; Blender is the first target client) (`.memory/CONTEXT.md`).
- **Plugin facade / client seam** — the DCC-shaped client contract: `enqueue(inputs)→job_id` + a `listen()` typed event stream, mapping 1:1 to API-GW-submit + SQS-FIFO + WS-relay (`.memory/CONTEXT.md`).
- **Envelope** — the versioned SQS wire message carrying model+version and input S3 references (`queue.py`).
- **Outcome / two-phase claim→commit** — the idempotency contract: only the conditional QUEUED→RUNNING winner runs inference; commit is work-done-wins (`executor.py`, `store.py`).
- **Data flywheel** — deferred opt-in loop turning artist accept/correct feedback into labeled training data (`.memory/CONTEXT.md`; ADR 0006).
- **MLP** — Minimum Lovable/Viable Product; the demo scope (ADR 0006).
- **Warm pool vs scale-from-zero** — the two acquisition mechanisms compared (STOPPED-EBS ~150s p95 at idle EBS cost vs true-zero ~342s p95 at $0 idle) (`autoscaler.py`; `.memory/spikes/02`).

## Notable Files

- `README.md` — purpose, why, three deliverables, topology diagram, prior-art anchors.
- `AGENTS.md` — operator guidance, current build stage, prior-art table, hard-won GPU/AWS/worker-import gotchas, ADR index.
- `.memory/PLAN.md` — authoritative work status, JTBD (creative + AI/ML team), deliverable roadmap, spike ordering.
- `.memory/CONTEXT.md` — project glossary + inherited-term crosswalk (sbin/artist-pipeline → this project).
- `.memory/adr/0003-model-registry-runner-abstraction.md`, `0004-reference-architecture-demo.md`, `0005-swappable-acquisition-and-runner-strategies.md`, `0007-worker-cold-start-and-message-liveness.md`, `0008-job-result-contract-for-dcc.md` — the load-bearing decisions.
- `.memory/spikes/02-cold-start-comparison.md` — measured cold-start numbers (the economic heart of the demo).
- `.scratch/chord-research.md` — CHORD deep dive (what/inputs/outputs/pipeline stage/maturity).
- `src/studio_model_service/contract.py` — the typed manifest + job-result contract (`conforms_to`).
- `src/studio_model_service/registry.py` — the model registry + license gate + runner resolution.
- `src/studio_model_service/bootstrap.py` — CHORD + TripoSR onboarding through one path; demo-vs-real registries.
- `src/studio_model_service/runners/native.py` — the real CHORD serving runner (stage/load/infer + S3 upload + role mapping).
- `src/studio_model_service/orchestrator/app.py` — the FastAPI submit/status/WS surface.
- `src/studio_model_service/orchestrator/worker.py` + `worker_main.py` — the scale-to-zero GPU worker + entrypoint.
- `src/studio_model_service/orchestrator/executor.py` — the shared claim→stage→load→infer→commit core.
- `src/studio_model_service/orchestrator/autoscaler.py` — the pure scaling decision + warm-vs-cold dial.
- `src/studio_model_service/orchestrator/metrics.py` — per-model observability emitter.
- `tools/worker/Dockerfile` — the baked GPU worker image (CUDA 12.8, torch cu128, CHORD, our src).
- `tools/spike03/comfy_runner.py` — the ComfyUI-runner prototype driving CHORD's node graph over HTTP.
- `tools/provision/provision.py` + `launch-worker.sh` — scripted `studio-service-*` AWS provisioning + the diversified-Fleet GPU launcher.
- `requirements.txt` — orchestrator deps (fastapi, uvicorn, boto3, pyjwt); worker model deps live in the image, not here.
