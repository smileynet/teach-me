# ComfyUI at Scale — Hosting & Scaling as a Production Service

Research for the `riot-comfy-ui-platform` reference-pattern context. Every claim carries a source tag `[L#:confidence]` keyed to the Sources section. Levels per the source-authority hierarchy: L1 observed artifact, L4 authoritative reference, L5 informed commentary, L6 community.

## Summary

ComfyUI is a single-process, node-graph diffusion engine (Python backend + litegraph.js frontend) that ships with a full HTTP + WebSocket API on port 8188 — you drive it headlessly by POSTing a workflow to `/prompt`, watching `/ws` for progress, then pulling results from `/history/{prompt_id}` and `/view` [L4:verified]. Running it *as* that synchronous server in production is the single biggest cause of incidents: one long generation head-of-line-blocks every request, and a GPU OOM or crash drops all in-flight work because control and data planes are co-located [L5:established]. The dominant production pattern is therefore **decouple ingest from GPU work**: a stateless gateway validates + enqueues, a pool of version-pinned GPU workers drains the queue at GPU speed, and outputs land in object storage handed back as signed URLs [L5:established]. On AWS there are three well-trodden reference architectures — **EKS + Karpenter** (interactive, scale-to-zero, GPU autoscaling), **ECS + ASG** (cost-first, single-instance, Cognito-fronted), and **SageMaker AI Processing Jobs** (batch, pay-per-second, ephemeral) — all AWS-published samples [L4:verified]. Model storage is the recurring hard problem: the fast path is **S3 as the source of truth synced to node-local NVMe instance store**, with FSx/EFS shared filesystems as the alternative for shared model trees [L4:verified][L1:verified]. Workflow-as-container versioning centers on **pinning ComfyUI + custom nodes + Python deps + models to immutable commit SHAs** in one image, because a mixed-version fleet silently changes node behavior [L5:established][L4:verified]. Internal Amazon prior art is substantial: an APG pattern (config-driven batch V-RAG on SageMaker), the CoREL/NARA GPU cluster's ComfyUI demo preset (Slurm), AWS Deadline Cloud + ComfyUI integration, a MAPLE/"Art Director" design doc analyzing ComfyUI's node architecture, and a Riddler/Palisade security slat treating internet-exposed ComfyUI as a Critical finding [L1:verified][L4:verified].

## Headless ComfyUI API patterns

**The core loop (`/prompt` → `/ws` → `/history`).** ComfyUI runs an HTTP server (default port 8188) you can call programmatically to submit workflows, upload files, download outputs, and monitor progress with no browser [L4:verified]. The canonical flow:

1. **POST `/prompt`** with the workflow in *API format* JSON. The server validates the prompt and adds it to an execution queue, returning either `prompt_id` + `number` (queue position), or `error` + `node_errors` if validation fails [L4:verified]. The prompt queue and `PromptExecutor` live in `execution.py`; routes are defined by `@routes` decorators in `server.py` [L4:verified].
2. **Connect WebSocket `/ws`** for real-time bidirectional updates. It emits JSON messages typed `status`, `execution_start`, `execution_cached`, `executing`, `progress`, `executed` — you watch for the `executing` message with a null node (execution complete) for your `prompt_id` [L4:verified].
3. **GET `/history/{prompt_id}`** to retrieve the completed run's outputs (which nodes produced which files), then **GET `/view`** (with filename/subfolder/type params) to download each image [L4:verified].

**Full route surface** (from `server.py`) worth knowing for a platform [L4:verified]:
- `/prompt` (GET = queue status/exec info; POST = submit)
- `/ws` (WebSocket real-time channel)
- `/history` (GET all; GET `/history/{prompt_id}`; POST to clear/delete)
- `/queue` (GET state; POST clear pending/running), `/interrupt` (stop current), `/free` (unload models to free VRAM)
- `/upload/image`, `/upload/mask` (input assets), `/view` (fetch output), `/view_metadata` (model metadata)
- `/object_info` and `/object_info/{node_class}` — introspect every node type's input/output schema, min/max/default constraints, and category (this is how a platform discovers what nodes/params exist at runtime) [L4:verified]
- `/models`, `/models/{folder}`, `/embeddings`, `/extensions`, `/features`, `/system_stats` (python version, devices, VRAM), `/workflow_templates`
- `/userdata` + `/v2/userdata` (user file CRUD, move/rename), `/users` (multi-user mode)
- Custom routes are added via `@routes.post('/my_path')` on `PromptServer.instance.routes` (aiohttp) — the extension mechanism for a platform to add its own endpoints [L4:verified].

**Workflow "API format" vs "UI format".** The UI saves a graph JSON with layout; headless submission needs the *API format* (node-id-keyed dict of class_type + inputs). ComfyUI exports it via the UI's "Save (API Format)" / dev-mode option; this is the JSON you template with prompt/seed and POST to `/prompt` [L4:verified]. Reference client implementations: ComfyUI ships `script_examples/websockets_api_example.py`; community clients include `ComfyAPI` (Python, websocket-based queue+download) and the official docs' Python (stdlib + `websocket-client`) examples with TypeScript/curl equivalents [L6:reported][L4:verified].

**Auth.** Core ComfyUI has no built-in auth — you put auth in front (ALB+Cognito, CloudFront+WAF, Midway/SSO reverse proxy) or use a login extension like `ComfyUI-Login` [L5:established][L4:verified]. Amazon's own security posture treats an unauthenticated internet-exposed ComfyUI as a **Critical** finding (arbitrary code execution via the node system) — see Internal prior art [L4:verified].

## AWS hosting/scaling reference architectures

Three AWS-published patterns, each optimized for a different access shape:

### 1. EKS + Karpenter (interactive service, GPU autoscaling, scale-to-zero) — `aws-samples/comfyui-on-eks` [L4:verified]
- **IaC**: AWS CDK + Amazon EKS Blueprints manage the cluster (EKS 1.35, Karpenter 1.9 in the current README).
- **GPU autoscaling**: Karpenter provisions GPU nodes on demand (`g6.2xlarge`/`g5.2xlarge`) and **scales to zero when idle**; Amazon Spot cuts GPU cost.
- **Model storage**: S3 is the model source of truth; on GPU node boot, user-data formats local **instance-store NVMe** and syncs models from S3 to it; pods bind-mount the node's instance-store dir into `ComfyUI/models` for fast load/switch. Outputs map `ComfyUI/output` to S3 via the **Mountpoint for S3 CSI driver** (PVC).
- **Model sync**: S3 put/delete events trigger a **Lambda** that fans out `aws s3 sync` to all GPU nodes over **SSM** (checksum-verified). An **auto-model-downloader** custom node transparently fetches missing models on first workflow run (from S3, HuggingFace fallback).
- **Build path**: container images and multi-GB model downloads run in **CodeBuild** (200+ MiB/s HF→S3), no local Docker/GPU needed. Images pin ComfyUI + Florence2 to immutable commit SHAs.
- **Secure access**: internal-only ALB reached by **CloudFront via VPC Origins (PrivateLink)** — ALB never faces the internet; NetworkPolicy restricts pod ingress to ALB subnets (port 8848) and egress to DNS+HTTPS; IMDSv2 hop-limit 1.
- **Bedrock custom nodes**: bundled nodes call Bedrock (Nova Canvas text-to-image, Nova Reel text-to-video, Stability inpaint/upscale/control, Claude/Nova/Qwen prompt enhancement) via **EKS Pod Identity** — no keys in the pod.
- **API use**: workflows saved as API-format JSON are callable per `test/invoke_comfyui_api.py`.
- Cost example: ~$450/mo for 1×g5.2xlarge 8h/day×20d + EKS control plane + S3 + CloudFront.

### 2. ECS + ASG (cost-first, single-user interactive, SSO-gated) — `aws-samples/cost-effective-aws-deployment-of-comfyui` [L4:verified]
- **Shape**: CDK deploys an ECS cluster on an EC2 GPU ASG (capacity provider), ALB in front, **Amazon Cognito** (user pool or SAML — Entra ID/Google Workspace) for auth, optional **WAF** IP allowlist + rate limit on `/api/prompt`.
- **Scale-to-zero**: a CloudWatch alarm on ASG CPU <1% for 60 min sets desired capacity to 0; a visit to the ALB invokes an admin **Lambda** that scales back to 1 (cold start ~5-8 min: launch + image pull + task start). Optional cron-based scheduled scaling (work hours).
- **Model/data storage**: a persistent **EBS data volume** (rexray Docker volume plugin) holds models, outputs, custom nodes across scale-to-zero cycles. This is **AZ-bound** and single-instance.
- **Cost/Spot**: Spot GPU (`g6e.2xlarge`, L40S 48GB) 60-90% savings; NAT Instance over NAT Gateway. ~$80/mo (2h/day) to ~$542/mo (24/7) on Spot.
- **Known limits (explicitly sample-grade)**: ASG max=1 (no concurrent multi-user scaling), single-AZ, no EBS snapshot automation, Spot interruption loses in-progress work, and **ALB idle timeout defaults to 60s which breaks WebSocket progress on long SDXL/video workflows — raise to 300s+** [L4:verified].

### 3. SageMaker AI Processing Jobs (batch, ephemeral, pay-per-second) — `aws-samples/sample-comfy-to-sagemaker-processing-job` [L4:verified]
- **Shape**: a Lambda triggers a SageMaker Processing Job that provisions N GPU instances (`ml.g5.xlarge`), pulls a custom ComfyUI container from ECR, runs a workflow over a batch of prompts, streams outputs to S3 in real time (continuous S3 upload mode), then terminates the instance — you only pay per second of compute.
- **Headless mechanics**: the container imports a workflow module that connects to the local ComfyUI server on import, **queues one workflow per prompt via the ComfyUI REST API, then polls the queue every 15s until empty** before shutting down [L4:verified — matches the APG pattern below].
- **CDK stacks**: DataStack (S3 + KMS), SecurityStack (VPC private subnets, NAT, KMS, flow logs), ComfyUISmStack (Lambda trigger + processing job + ECR). Uses `uv` for deps; example ships Z-Image Turbo (6B diffusion transformer).
- **Why batch**: "generate hundreds of images in one batch" — A/B ad creative, locale packaging, storyboard frames. Queue-based, scales by instance count, no idle cost.

### Other AWS building blocks and comparisons
- **Queue-backed GPU worker pattern (vendor-neutral, the general "right" shape)** [L5:established]: stateless FastAPI gateway (auth/validate/enqueue) → **Redis Streams** queue (consumer groups give in-flight tracking, idle-timeout retry, dead-letter) → version-pinned GPU worker pods → S3-compatible object store → Prometheus/Grafana. Scale gateway on CPU/req-rate; scale **workers on queue depth via KEDA**; keep 1-2 pre-warmed spares to hide cold starts. Shed load with HTTP 429 before the queue hits its memory cap. On AWS, swap Redis→SQS for externally-hosted workers.
- **SageMaker managed-serving pattern (from the internal Semantic Code Search whitepaper, analogous GPU-serving shape)**: "use managed serving, but own the deployed artifact" — SageMaker owns endpoint lifecycle/health/autoscaling; you own the container (patched DLC image in ECR) + weights (`model.tar.gz` in S3). Isolate latency-sensitive (query) from batch (indexing) traffic on **separate endpoints**; the indexing fleet held 30 `ml.g5.xlarge` (A10G 24GB) min, autoscaling to 50 [L1:verified]. Directly transferable to "interactive ComfyUI endpoint vs batch generation endpoint."
- **AppStream 2.0 / Nimble Studio** cover the *interactive artist-workstation streaming* angle (GPU workstation over NICE DCV, elastic Deadline render farm behind it) rather than a headless API — relevant if the platform also serves the ComfyUI *canvas* to artists, not just the API [L4:reported][L5:established].
- **Capacity model (editorial, not benchmarked)** [L5:reported]: ~1 A10G worker/~10 req/min, ~3/~30 req/min, ~8-12/~100 req/min; the biggest cost driver is **GPU idle time**, not GPU-hours — hence scale-to-zero and queue-depth autoscaling matter more than picking a cheaper card.

## Workflow + model management

### Workflow-as-container versioning
- **Pin everything to one image, one tag.** Every worker bundles ComfyUI at an immutable commit SHA + pinned PyTorch/CUDA base + pinned custom nodes + pinned Python deps. `latest` on a multi-replica fleet is a documented source of silent workflow incompatibility — mixed ComfyUI versions can change node behavior including sampler seeding [L5:established]. `comfyui-on-eks` follows this (ComfyUI + Florence2 pinned to commit SHAs; npm exact versions; SHA256-verified tool downloads) [L4:verified].
- **Reproducible-bundle tooling** (the ecosystem's answer to "workflow as a versioned artifact") [L6:reported]:
  - `Comfy-Org/comfy-complete` — the reproducible runtime Comfy Cloud deploys: ComfyUI core + a curated set of custom node packs + exact pinned Python deps, one repo, one Docker image.
  - `bentoml/comfy-pack` — toolkit to **lock, pack, and deploy** a ComfyUI workflow's full environment (nodes, models, deps) reproducibly.
  - ComfyUI **snapshots** (Comfy Desktop / ComfyUI-Manager) capture the node+dep set at a point in time.
  - Comfy.org **Enterprise "managed builds"** pin ComfyUI release, Python, CUDA, custom nodes, models, and deps across a fleet (the vendor's governance story) [L4:reported].
  - `runpod-workers/worker-comfyui` — serverless worker packaging pattern (custom nodes/models baked at build).
- **Bake the model into the image or a warm volume.** Cold checkpoint loads (multi-GB) dominate first-request latency far more than inference; baking the checkpoint or pre-warming a PVC removes the download from the cold path [L5:established].

### Custom-node management
- **ComfyUI Manager** is the community standard: search/install/update/disable/uninstall nodes, and on loading a shared workflow it **detects missing custom nodes and installs them automatically** [L4:verified][L1:verified — internal MAPLE doc].
- **Node interface contract**: custom nodes are Python classes declaring a schema (`define_schema` with `node_id`, `display_name`, `category`, typed inputs with min/max/default, typed outputs) and an `execute` classmethod; all node metadata is introspectable at runtime via `/object_info` [L1:verified — internal MAPLE doc quotes the exact `IO.ComfyNode` pattern]. The **V3 schema** is a versioned public node API adding stateless execution, async support, and backward-compat guarantees [L6:reported].
- **Dependency isolation**: `comfy-env` runs nodes needing conflicting CUDA/Python deps in their own persistent subprocess environments, transparent to ComfyUI — the answer to custom-node dependency hell in a shared image [L6:reported].
- **Security gate for a platform**: validate incoming workflow JSON against an **allowlist of known custom-node class names** before enqueue to prevent arbitrary code execution, and cap workflow payload size (oversized/malformed workflows are a common OOM cause) [L5:established].

### Model storage (the recurring hard problem)
- **S3-as-source + node-local NVMe instance store** is the fast path (comfyui-on-eks): S3 holds the canonical `ComfyUI/models` tree; nodes sync to instance store on boot for fast load/switch; S3 events → Lambda → SSM re-sync on change [L4:verified].
- **Shared filesystem (FSx / EFS / home dir mount)** is the alternative for a shared model tree across many nodes — the CoREL cluster mounts models from home/team data mounts and warns "never put weights in `/tmp`; it's wiped when the job ends; first load of a large model from shared storage takes minutes (normal)" [L1:verified]. The ECS sample uses a single persistent **EBS** data volume (AZ-bound) [L4:verified].
- **On-demand / lazy model download**: the comfyui-on-eks auto-model-downloader node intercepts a queued prompt, scans for referenced model files, downloads missing ones (+ co-downloads dependent text encoders/VAEs) from S3/HF, then runs — so the full ~90-model catalog is available without pre-loading everything [L4:verified].
- **GPUDirect Storage (emerging)**: ComfyUI GDS streams weights NVMe→VRAM, running heavy models on GPUs with as little as 6GB VRAM [L6:reported].

## Internal prior art (cite URLs)

- **APG pattern — "Deploy config-driven batch video, image, and audio generation pipelines on AWS SageMaker"** (V-RAG). ComfyUI used *headlessly* in all generation; the pattern imports a ComfyScript workflow module (connects to the local ComfyUI server on import), **queues one workflow per input prompt via the ComfyUI REST API, polls the queue until all complete**, copies outputs to the SageMaker output dir, logs results to DynamoDB. Troubleshooting notes name the exact failure classes: missing custom nodes, incompatible model format, GPU OOM (check `$COMFY_HOME/comfyui.log`). Requires SageMaker Processing job instance quota bumps for high-instance-count pipelines. https://apg-library.amazonaws.com/content/5d2698b3-50bb-477a-95c8-24dc32e12f14 [L4:verified]
- **CoREL / Amazon Video Content Partner Lifecycle GPU cluster** (Slurm-based, GPU pool donated by NARA, AutoDubs, etc.). Ships a **ComfyUI demo preset**: `sbatch demo-serve.sbatch my-workflow --preset comfyui --src <checkout> --models <tree> --workflows <dir>` serves a workflow at an SSO-protected URL; `--src` persists a ComfyUI checkout so **custom nodes install once and persist across demos**; `--models` points at a shared model tree (checkpoints/loras/vae/embeddings/controlnet/upscale_models resolve). Storage guidance: model weights on shared storage, never `/tmp`. Demos are 4h max, share ≤6 cluster GPUs, and programmatic (curl/python) clients can't pass the SSO wall — use the printed SSH tunnel. Also documents a **Burst Autoscaler** (reserved GPU blocks) and three-tier Slurm preemption. https://w.amazon.com/bin/view/Amazon_Video/Content_Partner_Lifecycle/CoREL/Compute/Cluster_User_Guide/Model_Demos/ and .../Cluster_User_Guide/ [L1:verified — live job listings show `comfyui_` jobs on p4d nodes]
- **AWS Deadline Cloud + ComfyUI integration** — Broadcast final presentation ("ComfyUI Integration with Deadline Cloud") https://broadcast.amazon.com/videos/1258051 ; NAB 2026 booth demo "Orchestrating content generation with ComfyUI on AWS" describes a **containerized ComfyUI that scales on demand with AWS as collaboration/orchestration hub**, plus a Kiro-built Adobe Premiere plugin embedding ComfyUI workflows. Deadline Cloud uses **Open Job Description (OJD)** as the job/environment spec and supports service-managed vs customer-managed (Spot-in-your-account) fleets. https://w.amazon.com/bin/view/AWS_3P_Events_Team/AWSatNAB2026/ and https://w.amazon.com/bin/view/AWS/Teams/Technical_Feedback_Communities/Media/Resources/AWS-Services/AWS-Deadline-Cloud/ [L4:verified / L5:established]
- **Riddler / Palisade security slat "OpenComfyUI"** (`palisade.riddler.open_comfyui`). Treats an owned ComfyUI instance exposed to the internet **without authentication as a Critical finding** — arbitrary code execution via the node system, access to model files/generated content, potential crypto-mining. Remediation: restrict security group to no public access + add auth, or terminate. Direct evidence that any internal ComfyUI hosting MUST be auth-gated and not internet-facing. https://w.amazon.com/bin/view/Palisade/Slats/Riddler/OpenComfyUI/ [L4:verified]
- **MAPLE / "Art Director" design doc (Yashal/Elm, "Appendix 3: Workflow Tools State Of Art and Mapping to MAPLE")** — an internal engineering analysis of ComfyUI's architecture as prior art for a DAG execution engine: input-signature-based caching (invalidate only when inputs change), the `IO.ComfyNode` custom-node schema pattern, `/object_info` runtime introspection, and the workflow-sharing ecosystem (embedded-PNG-metadata workflows, ComfyUI Manager auto-install, official templates). https://w.amazon.com/bin/view/Yashal/Docs/Elm/v1/ExecutionWorkingBackwardsFromRealAdsToBuildArtDirector/Design/Appendix3WorkflowToolsStateOfArtAndMappingToMaple/ [L1:verified — internal design doc]
- **AI Studios / Nara** — production ComfyUI usage by artists; knowledge-hub notes a known limit that there is **no shared studio API key for calling models from ComfyUI in production** (billing must go through studio leadership), and RDP/Wacom/access gotchas. Signals an internal org running ComfyUI at production scale for creative work. https://w.amazon.com/bin/view/Aistudios/KnowledgeHubSetup/ [L1:verified / L5:reported]
- **Broadcast: "ComfyUI Image Generation and Editing Workflows — Stability AI + Bedrock"** — internal enablement session citing the two aws-samples repos (cost-effective ECS, comfyui-on-eks) plus a "ComfyUI Personalized Generative AI Avatars App" sample. https://broadcast.amazon.com/videos/1520493 [L4:reported]

## Sources (URLs + [L#:confidence])

Internal:
- [L4:verified] APG — Config-driven batch V-RAG on SageMaker (ComfyUI headless): https://apg-library.amazonaws.com/content/5d2698b3-50bb-477a-95c8-24dc32e12f14
- [L1:verified] CoREL Cluster User Guide — Model Demos (ComfyUI preset): https://w.amazon.com/bin/view/Amazon_Video/Content_Partner_Lifecycle/CoREL/Compute/Cluster_User_Guide/Model_Demos/
- [L1:verified] CoREL Cluster User Guide (GPU classes, Burst Autoscaler, preemption): https://w.amazon.com/bin/view/Amazon_Video/Content_Partner_Lifecycle/CoREL/Drafts/cb-guide/Compute/Cluster_User_Guide/
- [L4:verified] Riddler/Palisade slat — OpenComfyUI (Critical: unauth internet exposure): https://w.amazon.com/bin/view/Palisade/Slats/Riddler/OpenComfyUI/
- [L1:verified] MAPLE "Art Director" Appendix 3 — ComfyUI architecture analysis: https://w.amazon.com/bin/view/Yashal/Docs/Elm/v1/ExecutionWorkingBackwardsFromRealAdsToBuildArtDirector/Design/Appendix3WorkflowToolsStateOfArtAndMappingToMaple/
- [L4:reported] Broadcast — ComfyUI Integration with Deadline Cloud: https://broadcast.amazon.com/videos/1258051
- [L4:reported] Broadcast — ComfyUI Workflows: Stability AI + Bedrock (cites aws-samples repos + avatars app): https://broadcast.amazon.com/videos/1520493
- [L4:verified] NAB 2026 wiki — "Orchestrating content generation with ComfyUI on AWS" demo: https://w.amazon.com/bin/view/AWS_3P_Events_Team/AWSatNAB2026/
- [L4:reported] M&E TFC — AWS Deadline Cloud (Open Job Description, fleets): https://w.amazon.com/bin/view/AWS/Teams/Technical_Feedback_Communities/Media/Resources/AWS-Services/AWS-Deadline-Cloud/
- [L1:reported] AI Studios KnowledgeHub — ComfyUI production usage / no shared API key: https://w.amazon.com/bin/view/Aistudios/KnowledgeHubSetup/
- [L1:verified] BuilderHub — Semantic Code Search whitepaper (SageMaker managed-serving-own-artifact pattern, workload isolation): https://ai.hub.amazon.dev/white-paper-semantic-code-search

External:
- [L4:verified] ComfyUI docs — Server Routes (HTTP + WebSocket API): https://docs.comfy.org/development/comfyui-server/comms_routes
- [L4:verified] ComfyUI docs — Server Overview: https://docs.comfy.org/development/comfyui-server/comms_overview
- [L4:verified] ComfyUI docs — API Examples (Python/websocket-client): https://docs.comfy.org/development/comfyui-server/api-examples
- [L4:verified] ComfyUI docs — Custom Nodes / Manager: https://docs.comfy.org/basic-concepts/custom-nodes
- [L4:reported] Comfy.org — Enterprise managed builds (fleet governance/pinning): https://comfy.org/enterprise/managed-builds/
- [L4:verified] aws-samples/comfyui-on-eks (EKS + Karpenter + S3/instance-store + Bedrock nodes): https://github.com/aws-samples/comfyui-on-eks
- [L4:verified] aws-samples/cost-effective-aws-deployment-of-comfyui (ECS + ASG + Cognito, scale-to-zero): https://github.com/aws-samples/cost-effective-aws-deployment-of-comfyui
- [L4:verified] AWS ML Blog — Running ComfyUI workflows on SageMaker AI Processing Jobs: https://aws.amazon.com/blogs/machine-learning/running-comfyui-workflows-on-amazon-sagemaker-ai-processing-jobs/
- [L4:verified] aws-samples/sample-comfy-to-sagemaker-processing-job: https://github.com/aws-samples/sample-comfy-to-sagemaker-processing-job
- [L4:reported] AWS Architecture Blog — Deploy Stable Diffusion ComfyUI on AWS elastically (instance-store optimization): https://aws.amazon.com/blogs/architecture/deploy-stable-diffusion-comfyui-on-aws-elastically-and-efficiently/
- [L5:established/reported] markaicode — ComfyUI Production Architecture: Queue-Backed GPU Workers (FastAPI+Redis Streams+KEDA): https://markaicode.com/architecture/comfyui-production-system-design-architecture/
- [L5:reported] markaicode — ComfyUI + Kubernetes production at scale: https://markaicode.com/integrate/comfyui-with-kubernetes/
- [L6:reported] Comfy-Org/comfy-complete (reproducible pinned bundle): https://github.com/Comfy-Org/comfy-complete
- [L6:reported] bentoml/comfy-pack (lock/pack/deploy environments): https://github.com/bentoml/comfy-pack
- [L6:reported] PozzettiAndrea/comfy-env (custom-node dependency isolation): https://github.com/PozzettiAndrea/comfyui-envmanager
- [L6:reported] runpod-workers/worker-comfyui (serverless worker packaging): https://github.com/runpod-workers/worker-comfyui
- [L6:reported] SamratBarai/ComfyAPI (Python websocket client): https://github.com/SamratBarai/ComfyAPI
- [L6:reported] sygnal.com — Exposing ComfyUI as an external API: https://www.sygnal.com/kb/exposing-comfyui-as-an-external-api
- [L6:reported] apatero.com — ComfyUI V3 custom-node schema: https://www.apatero.com/blog/comfyui-v3-custom-node-schema-development-2026
- [L4:reported] AWS PGS — SageMaker HyperPod (EKS orchestration, node health for GPU fleets): https://docs.aws.amazon.com/prescriptive-guidance/latest/gen-ai-inference-architecture-and-best-practices-on-aws/amazon-sage-maker-hyper-pod.html

## Open questions

1. **What exactly is `riot-comfy-ui-platform`?** Internal search surfaced no repo/wiki by that name (searched ALL, code-adjacent terms). It is likely a team-internal GitFarm package or private repo not indexed by InternalSearch. Confirm via `code.amazon.com` package search or the repo's own README — the explored repo is the primary source for which of the three AWS patterns (EKS/ECS/SageMaker) it actually implements.
2. **Concurrency model per worker.** ComfyUI is single-process and largely serializes a queue on one GPU. Does the platform run one ComfyUI per GPU pod (the common choice) or attempt multi-GPU via `ComfyUI-Distributed` (multi-GPU local/remote/cloud)? Not yet confirmed for any internal deployment.
3. **Session affinity for `/ws`.** The gateway/queue pattern hands back a job ID and polls `/history`, but interactive canvas use needs sticky WebSocket routing to the worker that owns the prompt. How does each internal deployment handle ALB/CloudFront WebSocket affinity + the 60s idle-timeout trap at scale? (The ECS sample flags the timeout but is single-instance.)
4. **Custom-node supply-chain governance internally.** Amazon's Riddler slat gates *exposure*, but is there an internal allowlist/vetting process for custom nodes (arbitrary-code-execution surface) analogous to comfy-complete's curated pack? Not found.
5. **Model artifact provenance.** aws-samples pulls weights from HuggingFace at build/deploy. Internal deployments likely must route models through HoverMart/approved artifact stores (per ML Coda model-hosting FAQ) rather than direct HF — the exact internal-approved model-distribution path for ComfyUI weights is unconfirmed.
6. **Bedrock-as-backend vs local-GPU tradeoff.** comfyui-on-eks ships Bedrock custom nodes (Nova/Stability/Claude) so ComfyUI can offload generation to managed models with zero GPU. When does a platform host open-weight models on its own GPUs vs call Bedrock? Decision criteria not established.
