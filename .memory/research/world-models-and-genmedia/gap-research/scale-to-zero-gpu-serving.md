# Scale-to-Zero GPU Inference Serving on AWS — Canonical Guides & Prior Art

Research date: 2026-09-16. Sources: InternalSearch (ALL/AWS_DOCS/BUILDER_HUB/WIKI) + web_search.
Source-authority tags per `[L#:confidence]` — L1 observed artifact, L4 authoritative reference, L6 community.

## Summary

Scale-to-zero GPU inference on AWS is a **solved problem with 4 canonical AWS-native paths** plus a
well-trodden self-managed queue-driven pattern. The explored repos that "reinvented" this (custom SQS
orchestrator, KEDA on EKS, SageMaker async) each map onto one of these reference patterns — none needed
bespoke orchestration. The decision hinges on **3 orthogonal questions** (who runs the undifferentiated
heavy lifting; which serving engine turns weights into tokens; how consumers reach it) and on the
**latency tolerance for cold starts** (the tax you pay for scaling to zero).

The single best internal reference is the wiki decision guide **"Deploying Open Models on AWS"**
(`w.amazon.com/bin/view/Ai-inference/decision-matrix/`) — it maps every serving option including their
scale-to-zero story. For queue-driven batch, the canonical AWS reference architecture is the
**Sept 2026 ECS Managed Instances + SQS + scale-to-zero** blog with `aws-samples/sample-ecs-gpu-inference`.

Key finding: **scale-to-zero always trades idle cost for cold-start latency.** Every path below scales
to zero; they differ only in cold-start magnitude (SageMaker async ~2-5 min model load; Serverless
sub-second but no GPU; Inference Components with Fast Model Loader up to 15× faster weight load; EKS
Karpenter+KEDA 7-84s depending on image-pull mitigation) and in how much ops you own.

## AWS-native scale-to-zero options

### 1. SageMaker real-time endpoints — scale down to zero instances (Nov 2024 launch)
- Auto-scaling can reduce in-service instances to **zero** during idle periods; you save cost when the
  endpoint isn't serving. `[L4:established]` AWS_DOCS "Scale an endpoint to zero instances"
  (`docs.aws.amazon.com/sagemaker/latest/dg/endpoint-auto-scaling-zero-instances.html`)
- Launch announcement: "Unlock cost savings with the new scale down to zero feature in SageMaker Inference"
  (Nov 2024) `[L4:established]` `aws.amazon.com/blogs/machine-learning/unlock-cost-savings-with-the-new-scale-down-to-zero-feature-in-amazon-sagemaker-inference/`
- Implemented via **Inference Components (IC)**: each IC packs a model + CPU/GPU/mem into one unit,
  scales **independently** and **can scale in to zero** (`minCopies=0`). This is the answer to
  "many teams, many models, do not waste GPUs." `[L4:established]` (internal decision guide + hosting notes)
- Internal note (`WWSO-SageMaker/focus-areas/inference`): IC is "when packing GPU per model for FM/LLM
  and scaling them independently down to zero." `[L4:reported]`

### 2. SageMaker Asynchronous Inference — queue-based, scales to zero natively
- Queues incoming requests, processes asynchronously; **can scale the instance count to zero when there
  are no requests**. Requests received at zero instances are **queued** until the endpoint scales up.
  `[L1:verified]` AWS_DOCS `async-inference-autoscale.html` + `async-inference.html`
- Ideal for large payloads (up to **1GB**), long processing (up to **1 hour**), near-real-time latency.
  You place the payload in S3, pass a pointer via `InvokeEndpointAsync`, results land back in S3, optional
  SNS success/error notification. `[L1:verified]`
- **Critical cold-start-from-zero gotcha:** once scaled to zero, the endpoint won't scale up again until
  the backlog exceeds the target-tracking value — causing long queue waits. To scale up from zero for
  requests *below* the queue target, add the extra scaling policy **`HasBacklogWithoutCapacity`**.
  `[L1:verified]` AWS_DOCS `async-inference-troubleshooting.html` + `async-inference-autoscale.html#async-inference-autoscale-scale-up`
- Uses S3 + SNS (+ optional SQS subscriber) — this is AWS's own queue-driven pattern, managed for you.
  `[L1:verified]`

### 3. SageMaker Serverless Inference — scales to zero, but NO GPU
- "During times when there are no requests, Serverless Inference scales your endpoint down to 0."
  `[L4:established]` AWS_DOCS `serverless-endpoints.html`
- **Hard constraint: CPU-only, no GPU support**, small size caps (memory 1024–6144 MB, 5 GB ephemeral
  disk, 10 GB container image, 4 MB payload, 200 max concurrent/endpoint, 1000 total concurrency/account
  major regions). **Not usable for LLMs / GPU inference.** `[L4:established]` internal hosting notes +
  decision guide ("Serverless Inference — scales to zero but has no GPU support and small size caps.
  Not for LLMs.")

### 4. EKS: Karpenter (node) + KEDA (pod) — true scale-to-zero for self-managed GPU
- AWS's own EKS guidance documents the split: **KEDA scales pods to zero when idle** and back up on demand;
  **Karpenter provisions GPU nodes when pods are Pending** and removes them when replicas scale back down.
  `[L4:established]` AWS_DOCS EKS User Guide "Autoscale AI inference with HPA and KEDA"
  (`docs.aws.amazon.com/eks/latest/userguide/ml-inference-autoscaling-hpa-keda.html`) + "Autoscale AI
  model inference on GPUs with Amazon EKS" (`.../ml-inference-autoscaling.html`)
- Pattern: KEDA scales replicas off **queue depth / GPU utilization** (not CPU); Karpenter reacts to the
  resulting Pending pods. vLLM/SGLang/TGI in the pod. `[L4:established]` (blog.easecloud.io, cast.ai,
  markaicode.com all corroborate) `[L6:established]`

### 5. Amazon Bedrock — serverless, native scale-to-zero for hosted/imported models
- **Base models** (Llama, Mistral, DeepSeek, Nova, Qwen…): pure serverless, per-token, **native base
  models scale to zero — no idle GPU bill**. `[L4:established]` internal decision guide
- **Custom Model Import (CMI):** bring your own fine-tuned open weights; AWS serves behind the Bedrock API;
  **billed usage-driven in 5-minute windows only during active invocations — no charge while idle
  (scale-to-zero)**; cold start "tens of seconds depending on model size, acceptable for batch." Region-
  limited (us-east-1/2, us-west-2, eu-central-1); architecture allow-list applies. `[L4:established]`
  internal PSV design doc §7.2.1 + decision guide
- **`InvokeModel` vs Converse API:** CMI supports only `InvokeModel` (per-model request/response coding);
  natively-hosted Bedrock models support the unified **Converse / ConverseStream API** (swap models via a
  config line, no code change). Image-to-image models (e.g. Stability upscalers) use `InvokeModel` only.
  `[L1:verified]` internal PSV design doc §7.1/§7.2.1

### 6. SageMaker HyperPod — scales from zero on a resilient cluster
- Managed **Karpenter autoscaling that "dynamically scales from zero to production"**, with KV caching,
  intelligent routing, MIG (Multi-Instance GPU) support. Built for fleet-scale training+inference; overkill
  for serving one 70B to a few teams. `[L4:reported]` internal `WWSO-SageMaker/focus-areas/inference` +
  decision guide Option 3

### Decision matrix (from the internal guide, condensed) `[L4:established]`
| Situation | Use |
|---|---|
| Ship this week, model on the menu | Bedrock base models |
| Own fine-tuned Llama/Mistral/Qwen, want serverless | Bedrock Custom Model Import |
| Specific open model + engine control, AWS runs nodes | SageMaker endpoint + LMI/vLLM |
| Many teams, many models, hate idle GPUs | **SageMaker Inference Components (scale-to-zero, model packing)** |
| Latency-tolerant, large payloads, bursty | **SageMaker Async Inference (scale-to-zero + queue)** |
| Already run k8s, platform team, cheapest at scale | **EKS + vLLM + Karpenter (+KEDA for pod scale-to-zero)** |
| Cost-sensitive steady volume, supported model | inf2 (Neuron) on endpoints or EKS |
| Fleet-scale train+serve, node failures hurt | HyperPod |

## Cold-start mitigation

The dominant cold-start cost for GPU serving is **image pull + weight load**, not container init.
AWS's own data: **image pull time is >75% of total container startup for large images.** `[L6:established]`
(aditmodi.hashnode.dev citing AWS)

### Image / container pull
- **SOCI (Seekable OCI) lazy loading** — index-based selective file download so containers start with only
  needed files; **pull time becomes ~size-independent.** Measured: 1.3 GB image 20s→~2.8s (7.4×), 2.5 GB
  image 9.3×. `[L1:verified]` arXiv 2607.06868 "Seekable OCI: Lazy-Loading Container Images via Range-Request
  Indexing". AWS blog "Reducing container cold start times using SOCI index on DLAMI and DLC"
  (`aws.amazon.com/blogs/machine-learning/reducing-container-cold-start-times-using-soci-index-on-dlami-and-dlc/`) `[L4:established]`
- **CAVEAT — SOCI is weak for ML inference specifically:** lazy-pull snapshotters (SOCI lazy mode, stargz,
  nydus) help when a container touches only a small fraction of its bytes at boot; **ML inference often
  reads nearly the whole image before serving**, eroding the benefit. `[L6:reported]` (hackernoon
  "Your 12GB ML Container Is a Cold-Start Tax"). Independent study: lazy pulling makes cold
  time-to-first-prediction *size-independent* (16.9–17.6s vs 24.5–573.0s eager) but **defers cost to first
  request** and changes failure semantics. `[L1:verified]` arXiv 2608.19412 "The Lazy Pod That Lies"
- On EKS, SOCI snapshotter reportedly cuts a ~10 GB vLLM DLC pull from 1m52s and 40–60 GB model-bundled
  images from 6–8 min dramatically. `[L6:reported]` aditmodi.hashnode.dev

### Weight load (the SageMaker-native answers, reInvent 2024)
- **Fast Model Loader** — streams model weights **directly from S3 to the accelerator**, up to **15× faster
  loading** vs traditional methods; purpose-built to accelerate autoscaling of LLMs. `[L4:established]`
  AWS blog Parts 1 & 2 (`introducing-fast-model-loader-in-sagemaker-inference...`)
- **Container Caching** — caches container images for GenAI scaling: **up to 56% latency reduction when
  scaling a new model copy, 30% when adding a copy on a new instance.** `[L4:established]` AWS blog
  "Supercharge your auto scaling for generative AI inference – Introducing Container Caching"
- **SageMaker HyperPod model caching (Sept 2026)** — weights caching + image caching (independently or
  together) for **faster inference autoscaling and reduced cold starts**; works with JumpStart (open +
  gated) and custom S3/FSx models. `[L4:established]` `aws.amazon.com/about-aws/whats-new/2026/09/sgm-hyperpod-model-caching-inf/`
  + AWS_DOCS `sagemaker-hyperpod-model-deployment-model-caching.html`

### Warm pools / provisioned concurrency / snapshotting (Lambda analogues)
- BuilderHub Golden Path (Lambda web service) documents the general cold-start toolkit that maps to GPU
  serving conceptually: **Provisioned Concurrency** removes cold start (always-warm containers, higher
  cost) vs **SnapStart** which *reduces* (not removes) cold start to sub-second via snapshot restore
  (Java/Python/.NET only; incompatible with container packaging and PC simultaneously). `[L4:established]`
  `docs.hub.amazon.dev/docs/golden-path/web-service-lambda/.../cold-start/`
- General cost-management guidance (BuilderHub Personal Stacks) endorses **scheduled scaling to zero on
  nights/weekends** and `minInstances=0` for ECS/EC2/Lambda as the baseline idle-cost control. `[L4:established]`
- Keeping model weights on a persistent volume / FSx and using S3 Mountpoint for weight streaming is a
  common EKS mitigation (PV for model weights + secondary boot disk / GKE analog). `[L6:reported]`
  (dev.to "Production-Ready GPU Inference Autoscaling on EKS with Karpenter, KEDA, and Dragonfly": Dragonfly
  P2P image distribution → cold 84s / warm 7s.)

### Tiered KV cache (advanced, reduces recompute not scale-up)
- "Tiered KV cache for large LLMs on SageMaker HyperPod with Curvine" — offloads KV cache to a tiered store
  to avoid recomputing identical prompts, cutting TTFT without oversizing GPUs. Orthogonal to scale-to-zero
  but reduces per-request latency. `[L4:reported]` `aws.amazon.com/blogs/machine-learning/tiered-kv-cache-for-large-llms-on-amazon-sagemaker-hyperpod-with-curvine/`

## Queue-driven autoscaling

The canonical AWS pattern is **target-tracking on SQS "backlog per instance"** — this is what the custom
SQS orchestrators in the explored repos are reimplementing.

- **Backlog-per-instance metric math** (the reference formula): `ApproximateNumberOfMessagesVisible ÷
  InService instance count`. Set the target so average backlog per instance = (acceptable latency ÷
  per-message processing time). AWS's worked example: 1s/image processing, target ≈ 100 images
  backlog/instance. `[L4:established]` AWS_DOCS `as-using-sqs-queue.html`,
  `ec2-auto-scaling-target-tracking-metric-math.html`, `scale-sqs-queue-cli.html`, and compute blog
  "Scaling an ASG using target tracking with a dynamic SQS target"
- **ECS Managed Instances + SQS + scale-to-zero (Sept 2026)** — the newest canonical reference architecture
  for GPU *batch* inference; example uses Qwen3-TTS on vLLM-Omni but "the infrastructure pattern applies to
  any GPU model that processes jobs from a queue." `[L4:established]`
  `aws.amazon.com/blogs/containers/run-gpu-batch-inference-on-amazon-ecs-managed-instances-with-scale-to-zero/`
  + `github.com/aws-samples/sample-ecs-gpu-inference`
  - **CAVEAT (independent):** this sample's Application Auto Scaling target is min 0 / **max 1**, using
    `ExactCapacity` to set desired=1 whenever any message is visible — it "scales to one, not out"; it does
    **not** compute worker count from queue depth / oldest-message age / target jobs-per-worker. Adapt for
    real fan-out. `[L6:reported]` windowsforum.com analysis
- **EKS: KEDA off SQS/Redis Streams queue depth** is the k8s-native equivalent (see §4 above). KEDA can
  scale deployments to **zero** replicas when idle and back on demand. `[L4:established]` AWS EKS docs +
  `[L6:established]` markaicode/spheron ("scale on inference queue depth, not instance metrics; add a
  budget guard that scales to zero if spend crosses a threshold").
- **Cost-guard pattern:** scale the group to zero if spend crosses a threshold — recommended alongside
  queue-depth scaling. `[L6:reported]` markaicode "Terraform AI Infrastructure: GPU Autoscaling and Cost Guards"

Community/prior-art Terraform modules implementing exactly this (evidence the pattern is standardized):
- `celestn1/terraform-aws-sqs-spot-gpu` — SQS-backlog-driven, Spot-first GPU autoscaling with scale-to-zero
  + graceful Spot-interruption handling, for ASR/inference/transcode. `[L6:reported]`
- `hirentimbadiya/ecs-sqs-autoscaling-terraform` — ECS Fargate autoscaling on SQS depth, Step Scaling +
  Target Tracking, scale-from-zero. `[L6:reported]`
- `adityonugrohoid/gpu-autoscale-inference` — scale-to-zero GPU inference on k8s with KEDA pod autoscaling
  + Cluster Autoscaler node provisioning. `[L6:reported]`

## Internal prior art / reference architectures (cite URLs)

1. **"Deploying Open Models on AWS: A Decision Guide"** — `w.amazon.com/bin/view/Ai-inference/decision-matrix/`
   (owner hkshah). THE canonical internal map. Covers Bedrock / SageMaker endpoints+IC / HyperPod / EKS+ECS /
   raw EC2, the "three questions that decide everything," serving-engine table (vLLM, TensorRT-LLM, SGLang,
   TGI, LMI/DJL, Neuron), and per-option scale-to-zero notes. **Read this first.** `[L4:established]`

2. **PSV Video Generation — Production Architecture Design** — `w.amazon.com/bin/view/Yankai/PSVScaling/`
   (owner yankai). Real, recent (Aug 2026) internal design that **explicitly evaluated 3 GPU-hosting options
   with scale-to-zero as a first-class criterion** for a 10K-ASIN/day GenAI video pipeline:
   - Option A SageMaker self-host (Inference Components, `minCopies=0`, cold start ~2-5 min) — cheapest/video (~$0.006)
   - Option B Bedrock Custom Model Import (5-min-window usage billing = scale-to-zero, cold start tens of s) — ~$0.011
   - Option C **(selected)** Native Bedrock via Converse API (base models scale to zero, model swap = config
     change, no Shinrai/BTPT clearance) — ~$0.050/video, ~8.8× A but chosen for ops simplicity + swap agility
   - Also: super-resolution self-host (RealESRGAN on `ml.g5.xlarge` `minInstances=0`, ~15s active/batch,
     ~500× cheaper) vs Bedrock Stability Fast Upscale (chosen for Bedrock-first consistency).
   This doc is a **worked, HITL-reviewed cost/latency comparison of scale-to-zero GPU options** — the best
   internal template for making this decision. `[L1:verified]`

3. **White paper: Semantic Code Search** — `ai.hub.amazon.dev/white-paper-semantic-code-search` (BuilderHub).
   Production internal pattern: **"use managed serving, but own the deployed artifact"** — SageMaker manages
   GPU endpoints (creation, health, **automatic scaling**, monitoring) while the team controls container +
   weights (patched TEI DLC image in ECR, Jina weights as `model.tar.gz` in S3). Also demonstrates the
   **latency-isolation pattern**: separate endpoints for interactive query (low-latency) vs SQS-fed indexing
   (batch, absorbs bursts) — query cannot wait behind a repo backfill. Indexing fleet on `ml.g5.xlarge`
   (A10G 24GB). `[L1:verified]`

4. **WWSO-SageMaker focus-areas/inference** — `w.amazon.com/bin/view/WWSO-SageMaker/focus-areas/inference/`
   — field content index: SageMaker Inference L400 deep dives, HyperPod inference (managed Karpenter, scales
   0→prod), the scale-down-to-zero + Container Caching + Fast Model Loader reInvent launches, and the
   `aws-samples/sagemaker-genai-hosting-examples` + FM hosting workshop (`catalog.workshops.aws/fm-inference/`).
   `[L4:established]`

5. **BuilderHub Managing Cost (Personal Stacks)** — `docs.hub.amazon.dev/docs/personal-stacks/user-guide/howto-managing-cost/`
   — baseline scale-to-zero hygiene: `minInstances=0`, scheduled scaling to zero nights/weekends for
   EC2/ECS, remove provisioned concurrency. `[L4:established]`

6. **BuilderHub Lambda cold-start Golden Path** — `docs.hub.amazon.dev/docs/golden-path/web-service-lambda/.../cold-start/`
   — Provisioned Concurrency vs SnapStart tradeoffs (conceptual analog for GPU warm pools). `[L4:established]`

## Sources (URLs + [L#:confidence])

Internal:
- [L4:established] https://w.amazon.com/bin/view/Ai-inference/decision-matrix/ — Deploying Open Models on AWS (decision guide)
- [L1:verified]   https://w.amazon.com/bin/view/Yankai/PSVScaling/ — PSV Production Architecture (worked scale-to-zero option eval)
- [L1:verified]   https://ai.hub.amazon.dev/white-paper-semantic-code-search — managed-serving-own-artifact + latency isolation
- [L4:established] https://w.amazon.com/bin/view/WWSO-SageMaker/focus-areas/inference/ — SageMaker inference field index
- [L4:established] https://docs.hub.amazon.dev/docs/personal-stacks/user-guide/howto-managing-cost/ — scale-to-zero cost hygiene
- [L4:established] https://docs.hub.amazon.dev/docs/golden-path/web-service-lambda/recommendation/operations/troubleshooting-and-performance-optimization/cold-start/

AWS docs (L4:established / L1:verified where quoted verbatim):
- https://docs.aws.amazon.com/sagemaker/latest/dg/endpoint-auto-scaling-zero-instances.html
- https://docs.aws.amazon.com/sagemaker/latest/dg/async-inference.html
- https://docs.aws.amazon.com/sagemaker/latest/dg/async-inference-autoscale.html (HasBacklogWithoutCapacity)
- https://docs.aws.amazon.com/sagemaker/latest/dg/async-inference-troubleshooting.html
- https://docs.aws.amazon.com/sagemaker/latest/dg/serverless-endpoints.html (scales to 0, no GPU)
- https://docs.aws.amazon.com/sagemaker/latest/dg/inference-cost-optimization.html
- https://docs.aws.amazon.com/sagemaker/latest/dg/hosting-faqs.html
- https://docs.aws.amazon.com/sagemaker/latest/dg/sagemaker-hyperpod-model-deployment-model-caching.html
- https://docs.aws.amazon.com/eks/latest/userguide/ml-inference-autoscaling-hpa-keda.html
- https://docs.aws.amazon.com/eks/latest/userguide/ml-inference-autoscaling.html
- https://docs.aws.amazon.com/autoscaling/ec2/userguide/as-using-sqs-queue.html
- https://docs.aws.amazon.com/autoscaling/ec2/userguide/ec2-auto-scaling-target-tracking-metric-math.html
- https://docs.aws.amazon.com/autoscaling/ec2/userguide/scale-sqs-queue-cli.html

AWS blogs / what's-new (L4:established):
- https://aws.amazon.com/blogs/machine-learning/unlock-cost-savings-with-the-new-scale-down-to-zero-feature-in-amazon-sagemaker-inference/
- https://aws.amazon.com/blogs/machine-learning/introducing-fast-model-loader-in-sagemaker-inference-accelerate-autoscaling-for-your-large-language-models-llms-part-1/
- https://aws.amazon.com/blogs/machine-learning/introducing-fast-model-loader-in-sagemaker-inference-accelerate-autoscaling-for-your-large-language-models-llms-part-2/
- https://aws.amazon.com/blogs/machine-learning/supercharge-your-auto-scaling-for-generative-ai-inference-introducing-container-caching-in-sagemaker-inference/
- https://aws.amazon.com/about-aws/whats-new/2026/09/sgm-hyperpod-model-caching-inf/
- https://aws.amazon.com/blogs/machine-learning/reducing-container-cold-start-times-using-soci-index-on-dlami-and-dlc/
- https://aws.amazon.com/blogs/machine-learning/tiered-kv-cache-for-large-llms-on-amazon-sagemaker-hyperpod-with-curvine/
- https://aws.amazon.com/blogs/containers/run-gpu-batch-inference-on-amazon-ecs-managed-instances-with-scale-to-zero/
- https://aws.amazon.com/blogs/compute/scaling-an-asg-using-target-tracking-with-a-dynamic-sqs-target/
- https://github.com/aws-samples/sample-ecs-gpu-inference

External research / community (L1:verified papers; L6 community):
- [L1:verified] https://arxiv.org/abs/2607.06868 — Seekable OCI (SOCI) lazy-loading, size-independent pull
- [L1:verified] https://arxiv.org/abs/2608.19412 — "The Lazy Pod That Lies" (deferred cost / failure semantics of lazy pull for model serving)
- [L6:reported]  https://aditmodi.hashnode.dev/soci-snapshotter-on-eks-eliminating-the-8-minute-gpu-cold-start-nobody-talks-about
- [L6:reported]  https://hackernoon.com/your-12gb-ml-container-is-a-cold-start-tax (SOCI weak for ML — reads whole image)
- [L6:established] https://dev.to/tazmainiandevil/production-ready-gpu-inference-autoscaling-on-eks-with-karpenter-keda-and-dragonfly-2f1p (cold 84s/warm 7s)
- [L6:established] https://blog.easecloud.io/ai-cloud/gpu-autoscaling-for-llm-inference/ (KEDA pods off queue depth, Karpenter nodes)
- [L6:established] https://cast.ai/blog/kubernetes-gpu-autoscaling/ (Karpenter+HPA+KEDA true scale-to-zero)
- [L6:reported]  https://www.spheron.network/blog/keda-knative-gpu-autoscaling-kubernetes-llm-cold-start/ (KEDA + Knative scale-to-zero)
- [L6:reported]  https://markaicode.com/terraform-ai-gpu-autoscaling-cost-guard/ (scale on queue depth + budget guard to zero)
- [L6:reported]  https://github.com/celestn1/terraform-aws-sqs-spot-gpu
- [L6:reported]  https://github.com/hirentimbadiya/ecs-sqs-autoscaling-terraform
- [L6:reported]  https://github.com/adityonugrohoid/gpu-autoscale-inference
- [L6:reported]  https://windowsforum.com/... — ECS Managed Instances sample "scales to one, not out" caveat

## Open questions

1. **Cold-start budget:** what's the acceptable p99 first-request latency after idle? This is the single
   variable that eliminates options — sub-second rules out any scale-to-zero GPU path (only Serverless
   CPU or always-warm PC qualifies); minutes-tolerant unlocks SageMaker async / IC / Bedrock CMI.
2. **Which explored repo maps to which pattern?** The custom SQS orchestrator ≈ EC2/ECS ASG target-tracking
   on backlog-per-instance (or should be replaced by SageMaker Async which does this managed); KEDA-on-EKS ≈
   the AWS EKS reference architecture (validate they use `HasBacklogWithoutCapacity`-equivalent scale-from-
   zero); SageMaker async endpoints are already canonical (validate the extra scale-up-from-zero policy is set).
3. **SOCI applicability:** given ML containers read most bytes at boot, is SOCI actually helping the explored
   repos, or is Fast Model Loader (S3→accelerator streaming) / model-on-FSx the better lever? Needs measured
   image-touch ratio.
4. **Bedrock region + architecture allow-list:** do the target models fit CMI's architecture allow-list and
   the us-east-1/2 / us-west-2 / eu-central-1 region limit? If not, self-host IC is forced.
5. **Consolidation opportunity:** could the repos' 3 separate reinventions collapse onto ONE shared pattern
   (e.g. SageMaker Async for batch + IC scale-to-zero for interactive multi-model), removing bespoke
   orchestration entirely? The PSV doc and decision guide suggest yes.
6. **Neuron/inf2:** none of the explored repos mention Inferentia2 — for steady/supported models it's ~40-50%
   cheaper/token; worth a cost spike if any workload is steady rather than bursty.
