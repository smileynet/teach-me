# riot-comfy-ui-platform — Research Findings

Repo explored via symlink → `/local/home/sabiggin/code/riot-comfy-ui-platform` (real path).
Focus: generative media pipelines (ComfyUI hosting, workflows, media types, model hosting,
LoRA/training, GPU infra). Every claim cites a file path.

## Purpose

A production, GPU-backed platform that lets any Riot Games creative or engineering team run
ComfyUI generative-AI workflows without provisioning GPUs, downloading model weights, or
building a job queue — teams submit a job via REST/WebSocket API or open a full ComfyUI UI
streamed to a browser (`README.md`; `docs/VISION.md`; `docs/comfy-platform-overview.md`). The
architecture is deliberately workflow-agnostic: any ComfyUI workflow packaged as a versioned
container runs on the shared GPU fleet with the same access control, model store, and cost
model (`docs/VISION.md` "The platform is generic by design"). The reference workflow is
**Trellis2** — image → 3D mesh (GLB) via Microsoft TRELLIS.2 — chosen because it exercises
every platform capability at once: ~10 GB weights, GPU-only execution, multi-node CUDA
extensions, non-trivial output format (`docs/comfy-platform-overview.md` "Why Trellis2 as the
reference workflow?"). All five milestones are marked complete, 30/30 slices (`README.md`
Status/Milestones table).

## Architecture & Components

Three conceptual layers — **Workflow Registry**, **Model Library**, **Execution Surface**
(`docs/VISION.md` "The Three Layers"). Implementation:

### CDK (IaC — all AWS infra, TypeScript)
Entry `cdk/bin/app.ts`; region hardcoded `us-west-2`; `prototyping: true` context. Stacks
(`cdk/bin/app.ts`, `cdk/lib/*`):
- **NetworkStack** (`cdk/lib/network-stack.ts`) — VPC, 3 AZs, 3 subnet tiers, 1 NAT (prototyping);
  VPC endpoints (S3, ECR, SageMaker, Secrets Manager); SGs for EKS/AppStream/FSxN (NFS 2049).
- **RegistryStack** (`cdk/lib/registry-stack.ts`) — ECR repos `comfy-workflows/trellis2-3d` and
  `comfy-workflows/comfyui-base` (immutable tags, scan-on-push); platform KMS CMK; **SageMaker
  Model Package Groups** `trellis-image-large`, `dinov3-vitl16`, **`loras`** (model lineage/approval).
- **StorageStack** (`cdk/lib/storage-stack.ts`) — **FSx for NetApp ONTAP** (SINGLE_AZ_2, 1200 GiB
  SSD, 1536 MiB/s; SVMs `models-svm` + `scratch-svm`; FlexClone parent volume `models_master`
  200 GiB); **EFS** (outputs); **S3** models+outputs buckets (SSE-KMS); DynamoDB
  `comfy-clone-registry`, `comfy-job-queue`, `comfy-platform-state`; Secrets (HuggingFace token,
  ONTAP creds). Optional `fsxnMultiAz=true` flag (`docs/platform-brief.md` "Optional: multi-AZ FSxN").
- **CloneManagerStack** (`cdk/lib/clone-manager-stack.ts`) — Lambda managing FlexClone lifecycle.
- **VendingStack** (`cdk/lib/vending-stack.ts`) — model-access gate Lambda + `VendingRole` + S3
  deny-on-tag-mismatch bucket policy.
- **EksStack** (`cdk/lib/eks-stack.ts`) — EKS `comfy-eks`, K8s 1.32, **private endpoint only**,
  **Auto Mode** (built-in Karpenter/EBS-CSI/ALB controller/VPC CNI); EFS-CSI + CloudWatch
  observability addons. Manifests applied post-deploy, not by CDK `addManifest()` (`README.md`
  "IaC"; times out on Auto Mode).
- **EksValidationCodeBuildStack** (`cdk/lib/eks-validation-codebuild-stack.ts`) — in-VPC CodeBuild
  runner `comfy-eks-validation` that runs `k8s/verify-live-env.sh` against the private endpoint
  (no bastion) (`docs/runbooks/eks-validation-access.md`).
- **SpaStack** (`cdk/lib/spa-stack.ts`) — S3 + CloudFront (OAC) hosting the React SPA.
- **AppStreamStack** (`cdk/lib/appstream-stack.ts`) — Cognito User Pool + **Okta SAML IdP**;
  **AppStream 2.0 fleet** (`stream.graphics.g6.xlarge`, ON_DEMAND) for interactive artist sessions.
- **RouterStack** (`cdk/lib/router-stack.ts`) — API Gateway + `comfy-router` Lambda + Cognito
  authorizer; routes interactive→AppStream, batch/async→EKS ALB.
- **CiRoleStack / Ec2BuilderStack / BuildReaperStack / ObservabilityStack** — GitLab-CI IAM role
  (`cdk/lib/ci-role-stack.ts`), ephemeral EC2 image-builder profile (`ec2-builder-stack.ts`),
  hourly reaper of orphaned builders (`build-reaper-stack.ts`), clone-orphan alarm/dashboard
  (`observability-stack.ts`).

### containers/ (ComfyUI Docker images — the "unit of deployment")
- **comfyui-base** (`containers/comfyui-base/Dockerfile`) — base `nvcr.io/nvidia/cuda:12.8.0-...`,
  Python 3.12 venv, PyTorch 2.7.0+cu128, ComfyUI pinned at a commit SHA
  (`containers/comfyui-base/.comfyui-version`). Model weights never in the image — mounted at
  runtime. CMD `python main.py --listen 0.0.0.0 --port 8188`.
- **trellis2-3d** (`containers/trellis2-3d/Dockerfile`) — production multi-stage build; Stage 1
  compiles CUDA extension wheels (flash-attn, nvdiffrast, diff-gaussian-rasterization, o_voxel,
  Hunyuan custom_rasterizer, pytorch3d), Stage 2 layers them onto comfyui-base + Trellis2 node
  source + optional DINOv3 bake. Ships `workflow.json`/`workflow_api.json`, `extra_model_paths.yaml`,
  `SMOKE_TEST_IMAGE.png`. CUDA extension strict install order documented in `docs/platform-brief.md`
  ("Container dependency chain"): `cumesh → nvdiffrast → nvdiffrec_render → flex_gemm → o_voxel`.
- **manifest/** (`containers/manifest/tools.json`) — platform tool catalog; currently one tool
  `comfyui/trellis2-3d`, tiers `["appstream","eks"]`, required mounts (models RO, output RW),
  DINOv3 gated-license note.

### k8s/ (manifests + live-cluster scripts)
- GPU **NodePool** (`k8s/nodepools/gpu-serving.yaml`) — g6.xlarge / NVIDIA L4, on-demand only,
  AZ-pinned to FSxN AZ, taint `nvidia.com/gpu=true:NoSchedule`.
- **Deployments** (`k8s/deployments/comfy-api-baseline.yaml`, `comfy-api-canary.yaml`) — ComfyUI
  pods, `strategy: Recreate` (one GPU per node), probes on `/system_stats:8188`, mounts
  `fsxn-models-pvc` (RO) + `efs-outputs-pvc` (RW).
- **KEDA** (`k8s/keda/comfy-scaledobject.yaml`) — DynamoDB `comfy-job-queue` depth scaler.
- **Ingress** (`k8s/ingress/comfy-alb.yaml`) — single internal-only ALB `comfy-alb`
  (`README.md` D050; second ALB deleted per D051), `target-type: ip`, `lb_cookie` sticky sessions
  3600s (ComfyUI in-process job state), idle timeout 3600s (WebSocket).
- **PV/PVC** (`k8s/pv/*`) — FSxN models (RO), FSxN shared-models (RW), FSxN projects, EFS outputs,
  per-team FlexClone PVs.
- Storage staging + model tooling (`k8s/models/manifest.json`, `k8s/stage-z-image-models.sh`,
  `k8s/stage-trellis-models.sh`, `k8s/models/generate_extra_model_paths.py`).
- Apply order authoritative in `k8s/post-deploy-apply.sh` (`k8s/README.md`).

### image-build/appstream/ (interactive-session bake)
Bakes the AppStream image running ComfyUI under podman: `provision-comfyui.sh`, `bake-gate.sh`,
`comfyui.service`, FSxN/projects/shared-models mount units (`image-build/appstream/*`). Runs
ComfyUI in a container reached by Firefox at `127.0.0.1:8188` (ComfyUI is a web app —
`docs/milestones/blender-tier-proposal.md` "ComfyUI is a web application").

### lambda/ (control plane)
- **clone-manager** (`lambda/clone-manager/index.ts`, `ontap.ts`) — ONTAP REST FlexClone
  create/delete; triggered by EventBridge on CodePipeline `pr-*` events (per-PR model env).
- **vending** (`lambda/vending/index.ts`) — checks SageMaker model-package approval + team S3-tag
  policy, returns NFS path `<nfsIp>:/models/<model>/<version>`.
- **router** (`lambda/router/index.ts`) — Cognito-authenticated tier router (interactive→AppStream
  `CreateStreamingURL`, async/batch→EKS ALB).
- **orphan-checker** (`lambda/orphan-checker/index.ts`) — hourly FlexClone-leak detector → CloudWatch.

### frontend/ (React SPA)
Vite + React (`frontend/src/App.tsx`, `frontend/package.json`); config-driven
(`frontend/public/config.json`, `frontend/src/configLoader.ts`); hosted on CloudFront (SpaStack).
Thin entry point that authenticates via Cognito and calls the Router API.

## Generative Media Pipeline Aspects

**ComfyUI hosting.** ComfyUI is the core workflow engine, run two ways from the *same* container
image + model library (`docs/comfy-platform-overview.md` "Execution Modes"):
- **API Batch** — headless ComfyUI on EKS GPU pods; `POST /prompt` (workflow JSON) → `prompt_id`,
  WebSocket `/ws` progress, `/history/{id}` → outputs, `/view?filename=` download (`docs/VISION.md`
  Layer 3). Port 8188 (`containers/comfyui-base/Dockerfile`).
- **Interactive Streaming** — full ComfyUI UI streamed via AppStream to a browser, Okta SSO
  (`docs/comfy-platform-overview.md`; `image-build/appstream/`).

**Workflow orchestration.** The workflow container (ComfyUI + custom nodes + workflow JSON) is the
unit of deployment/versioning; model weights never in the image (`docs/platform-brief.md`
"unit of deployment"). Promotion pipeline: git push → build → vulnerability scan → manual approval
gate → immutable ECR tag; fleet pulls only `approved=true` (`docs/VISION.md` Layer 1;
`docs/comfy-platform-overview.md` "Workflow Versioning and Promotion"). ComfyUI's in-process job
queue is why ALB sticky sessions + `Recreate` strategy are required (`docs/platform-brief.md`
"ALB sticky sessions"; `k8s/deployments/comfy-api-baseline.yaml`).

**Media types.**
- **Image → 3D mesh (GLB)** — the only *implemented, live-proven* generative pipeline. Trellis2
  workflow (`containers/trellis2-3d/workflow_api.json`) is a linear graph: `Trellis2LoadModel`
  (`microsoft/TRELLIS.2-4B`, `sparse_backend: flash_attn`, `conv_backend: flex_gemm`) →
  LoadImageWithTransparency → PreProcessImage → ImageCondGenerator → SparseGenerator →
  ShapeGenerator → ShapeCascadeGenerator (to_resolution 1024) → DecodeLatents → FillHoles →
  ReconstructMeshWithQuad → SimplifyMesh (500k faces) → MeshToTrimesh (90° reorient) → ExportMesh
  (GLB) → Preview3D. Round-trip target < 180s warm (`docs/platform-brief.md`). Proven live:
  `docs/milestones/m005-s02-trellis2-3d-proven-live.md`.
- **Text → image (RGBA/alpha)** — **proposed, not built**
  (`docs/milestones/text-to-image-alpha-proposal.md`): generate a full-body humanoid on true
  transparency to feed the TRELLIS input (today only one hand-made `SMOKE_TEST_IMAGE.png` exists).
  Native-alpha (LayerDiffuse) vs generate-then-matte (RMBG/BiRefNet/SAM) is an open slice-1 choice.
  A **z_image_turbo** text-to-image model set (diffusion_models + qwen_3_4b text encoder + VAE) is
  already staged on the curated tier (`k8s/models/manifest.json` model_sets `z_image_turbo`), and a
  **Hunyuan3D-2** image-to-3D checkpoint is staged (`k8s/models/manifest.json` `hunyuan3d_2`).
- **Video / audio / speech** — **not present.** Named only as future scope/open questions
  (FLUX/SDXL, CogVideoX/Wan, stable audio) in `docs/VISION.md` and `docs/comfy-platform-overview.md`
  "Open Questions". No video/audio/speech nodes, models, or workflows exist in the repo (grep of
  `docs/**` returns only the finetune proposal, overview, VISION, and storage runbook — no
  implementation).
- **DCC tool tiers** — **proposed**: containerized **Blender** (`docs/milestones/blender-tier-proposal.md`,
  gated on proving GPU-accelerated native GL in a container on AppStream) and **Unreal Editor**
  (`docs/milestones/unreal-tier-proposal.md`, gated on an Epic EULA legal review) as post-TRELLIS
  mesh-refinement stages.

**Model management.** Two-tier: **S3** authoritative KMS-encrypted weights → **FSxN** hot NFS
mounted by every pod/session (`nconnect=16`, up to ~10 GbE) → **FlexClone** per team/PR
(zero-storage copy-on-write, <10s) → `/workspace/models` (`docs/comfy-platform-overview.md`
"Model Storage Architecture"; `docs/platform-brief.md`). FSxN chosen over EFS (no `nconnect`) and
Mountpoint-S3 (no mmap, ≤1MB cache) (`docs/platform-brief.md` comparison table). Model resolution
via `containers/trellis2-3d/extra_model_paths.yaml`: a **writable shared root** (`is_default: true`,
`/workspace/shared_models` — where UI-downloaded models land and survive `podman run --replace`)
plus a **read-only curated library** (`/workspace/models`). Categories (`k8s/models/manifest.json`
`categories`) include checkpoints, clip, controlnet, embeddings, **loras**, vae, diffusion_models,
trellis, text_encoders. Governance: **vending Lambda** gates on SageMaker model-package approval +
IAM/S3 team-access tag before returning an NFS path (`lambda/vending/index.ts`;
`cdk/lib/vending-stack.ts`). Cold-start: first fresh-session generation ~15 min (weights fault in
over NFS) vs ~182s warm — the subject of the (proposed) model-availability milestone
(`docs/milestones/model-availability-proposal.md`).

**LoRA / training.** LoRA is a **first-class hosting concern but there is no training pipeline in
this platform.** Evidence: `loras` is a model category (`k8s/models/manifest.json`,
`extra_model_paths.yaml`) and a SageMaker Model Package Group (`cdk/lib/registry-stack.ts`);
adding a LoRA adapter is described as a container update, and per-team LoRA-on-shared-base isolation
is a FlexClone use case (`docs/VISION.md` Layers 1–2). Training/fine-tuning is explicitly
**scoped out**: "A HyperPod training tier was scoped out early; fine-tuning is not in this platform"
(`README.md`). A **HyperPod fine-tune milestone is proposed** but unbuilt and gated on a
Legal/IP data clearance and a "fine-tuned artifact vs. HyperPod demo?" objective decision
(`docs/milestones/hyperpod-finetune-proposal.md`); it notes a single-node SageMaker training job
would be cheaper for a LoRA/DreamBooth SDXL fine-tune.

**GPU scaling.** EKS **Auto Mode** built-in Karpenter provisions g6.xlarge (L4) GPU nodes in ~60s
(`docs/platform-brief.md`; `cdk/lib/eks-stack.ts`). **KEDA** scales ComfyUI pods on DynamoDB
`comfy-job-queue` `status=pending` depth: `targetValue 3` (`ceil(pending/3)`), `pollingInterval 15s`,
`cooldownPeriod 300s`, **`minReplicaCount 1`** (warm pod; GPU cold start 3–4 min),
**`maxReplicaCount 2`** — the *binding* ceiling, not the NodePool `limits` (cpu 12 ≈ 3 nodes)
(`README.md` "Autoscaling"; `k8s/keda/comfy-scaledobject.yaml`; `docs/milestones/multi-node-eks-render-proposal.md`).
Interactive GPUs are per-session AppStream `stream.graphics.g6.2xlarge` (32 GiB to keep the Trellis2
working set in page cache — D052) (`docs/comfy-platform-overview.md`; `docs/decisions/D052-appstream-fleet-instance-size-g6-2xlarge.md`).
Scale-to-zero + weekend park via `k8s/keda/park-gpu-weekend.sh` (annotate
`autoscaling.keda.sh/paused-replicas=0`, not `kubectl scale`) (`README.md`;
`docs/runbooks/keda-scale-to-zero.md`). Suspend/resume destroys GPU compute (~2 min) and reprovisions
(~15 min) while FSxN is always retained (~$35/mo) (`docs/platform-brief.md` "Suspend/resume";
`scripts/platform-suspend.sh`, `scripts/platform-resume.sh`). Multi-node fan-out beyond 2 GPUs is a
proposed milestone (`docs/milestones/multi-node-eks-render-proposal.md`).

## World Model Relevance

Low-to-moderate, and indirect. This platform is **generative media infrastructure**, not a
world-model/agentic-simulation system. The relevant intersections:
- **Image → 3D geometry** (Trellis2/TRELLIS.2, Hunyuan3D) turns a single image into 3D structure —
  a spatial-reconstruction/3D-generative capability adjacent to world-model asset generation, but
  here it targets game-art asset pipelines, not learned environment dynamics
  (`containers/trellis2-3d/workflow_api.json`; `docs/milestones/blender-tier-proposal.md`).
- **DINOv3 vision backbone** (`facebook/dinov3-vitl16-pretrain-lvd1689m`) is used as the image
  conditioning/feature extractor for 3D reconstruction (`k8s/assets/reconviagen_pipeline.json`
  `image_cond_model`; `.scratch/subagent-raw/vision-jtbd.md`) — a general visual representation
  model of the kind world-model work also draws on, used here purely for conditioning.
- A **reconviagen** pipeline variant exists (`k8s/assets/reconviagen_pipeline.json`;
  `Trellis2LoadModel.use_reconviagen` flag in `containers/trellis2-3d/workflow_api.json`) with a
  texture/appearance branch (tex_slat decoders/samplers) — richer 3D reconstruction, still asset
  generation not world modeling.
- No RL, no learned dynamics/simulation, no agent policy, no video-prediction world model anywhere
  in the repo. The one "agent" mention is a deferred stretch goal: WorkSpaces AI Agent Desktop +
  Strands MCP driving the ComfyUI UI by computer vision (`docs/comfy-platform-overview.md` Open
  Question 7) — UI automation, not a world model.

## Key Terms & Jargon

- **ComfyUI** — open-source node-graph engine for generative-AI workflows; runs headless (API) or
  interactive (UI); workflows serialize to JSON (`.scratch/subagent-raw/vision-jtbd.md`).
- **Workflow container** — ComfyUI + custom nodes + workflow JSON packaged as a versioned ECR image;
  the platform's unit of deployment; never contains model weights (`docs/platform-brief.md`).
- **Trellis2 / TRELLIS.2** — Microsoft image-to-3D-mesh model (`microsoft/TRELLIS.2-4B`), the
  reference workflow; produces a GLB mesh (`containers/trellis2-3d/workflow_api.json`).
- **DINOv3** — Meta visual backbone used as the image-conditioning feature extractor for Trellis2
  (`k8s/assets/reconviagen_pipeline.json`).
- **reconviagen** — an alternate Trellis reconstruction pipeline mode with a texture/appearance
  branch (`k8s/assets/reconviagen_pipeline.json`; `use_reconviagen` node input).
- **GLB** — binary glTF 3D asset, the Trellis2 output format (`containers/manifest/tools.json`
  output type).
- **FSxN (FSx for NetApp ONTAP)** — high-throughput NFS store for hot model weights; supports
  `nconnect`, mmap, and FlexClone (`docs/platform-brief.md`).
- **FlexClone** — ONTAP copy-on-write volume clone: instant (<10s), zero storage overhead;
  per-team/per-PR model isolation (`docs/VISION.md` Layer 2; `lambda/clone-manager/ontap.ts`).
- **nconnect=16** — NFS mount option opening 16 TCP connections for parallel throughput (~10 GbE)
  (`docs/platform-brief.md`).
- **Model vending** — Lambda that authorizes a team for a model (SageMaker approval + IAM/S3 tag)
  and returns its NFS mount path (`lambda/vending/index.ts`).
- **SageMaker Model Package Group** — model registry/approval unit gating what the fleet may pull;
  groups here include `trellis-image-large`, `dinov3-vitl16`, `loras` (`cdk/lib/registry-stack.ts`).
- **KEDA** — Kubernetes event-driven autoscaler; scales pods on DynamoDB queue depth
  (`k8s/keda/comfy-scaledobject.yaml`).
- **Karpenter / EKS Auto Mode** — built-in node autoprovisioner; brings up GPU nodes in ~60s
  (`cdk/lib/eks-stack.ts`).
- **AppStream 2.0** — AWS managed application streaming; delivers the interactive ComfyUI UI on a
  per-session GPU with Okta SSO (`cdk/lib/appstream-stack.ts`).
- **LoRA** — low-rank adapter stacked on base weights; a hosted model category here, not trained
  (`k8s/models/manifest.json`; `README.md`).
- **HyperPod** — SageMaker resilient multi-node training clusters; proposed-but-unbuilt fine-tune
  tier (`docs/milestones/hyperpod-finetune-proposal.md`).
- **z_image_turbo / Hunyuan3D-2** — additional staged model sets (text-to-image; image-to-3D)
  (`k8s/models/manifest.json`).
- **Suspend/resume** — cost model destroying GPU compute at idle while retaining FSxN
  (`scripts/platform-suspend.sh`, `platform-resume.sh`).

## Notable Files

- `docs/VISION.md` — the three-layer vision, JTBD, roadmap, open questions.
- `docs/comfy-platform-overview.md` / `docs/platform-brief.md` — architecture + decision rationale
  (GPU choice, FSxN vs EFS/Mountpoint, CUDA extension chain, cost model).
- `cdk/bin/app.ts` — full stack graph + dependency ordering + SpringClean exemption notes.
- `containers/trellis2-3d/workflow_api.json` / `workflow.json` — the live Trellis2 image→3D graph.
- `containers/trellis2-3d/Dockerfile` — multi-stage CUDA-extension build (the hard part).
- `containers/trellis2-3d/extra_model_paths.yaml` — writable-shared vs read-only-curated model roots.
- `k8s/models/manifest.json` — S04 layout contract; staged model sets (Trellis, z_image_turbo, Hunyuan3D-2).
- `k8s/assets/reconviagen_pipeline.json` — full TRELLIS model set incl. texture/appearance branch + DINOv3/BiRefNet.
- `k8s/keda/comfy-scaledobject.yaml` + `k8s/nodepools/gpu-serving.yaml` — GPU autoscaling config.
- `k8s/ingress/comfy-alb.yaml` — single internal-only ALB (sticky sessions for ComfyUI job state).
- `lambda/vending/index.ts` + `cdk/lib/vending-stack.ts` — model governance (approval + team-tag gate).
- `lambda/clone-manager/index.ts` + `ontap.ts` — FlexClone lifecycle.
- `docs/milestones/text-to-image-alpha-proposal.md` — proposed text→image (alpha) feeder for TRELLIS.
- `docs/milestones/hyperpod-finetune-proposal.md` — proposed (unbuilt) LoRA/fine-tune tier.
- `docs/milestones/multi-node-eks-render-proposal.md` — proposed GPU multi-node fan-out scaling.
- `docs/milestones/blender-tier-proposal.md` / `unreal-tier-proposal.md` — proposed DCC mesh-refinement tiers.
- `docs/milestones/m005-s02-trellis2-3d-proven-live.md` — the live image→3D acceptance record.
- `docs/decisions/D0xx-*.md` — 40+ ADRs (D025 patches overlay, D050/D051 ALB collapse, D052 AppStream
  instance size, D053 A/B topology, D055 ScaledObject ordering).
- `patches/ComfyUI-Trellis2/` — version-controlled patch overlaid on the gitignored vendored node tree.

### Scope note
Implemented & live: **image → 3D (GLB)** only. Staged-but-not-wired: text-to-image (z_image_turbo),
Hunyuan3D-2. Proposed/unbuilt: text→image-with-alpha, LoRA/HyperPod fine-tuning, multi-node scaling,
Blender & Unreal tiers. Absent entirely: video, audio, speech generation.
