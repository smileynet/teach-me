# LoRA / Fine-tuning TRAINING Pipelines for Generative Image/Video Models on AWS

Research date: 2026-09-16. Fills the "training tier" gap: explored serving platforms HOST
LoRAs but none TRAINS them. This documents the canonical fine-tuning workflows, the AWS
training-tier choices (SageMaker training jobs vs HyperPod), internal Amazon prior art, and
the data-flywheel pattern that feeds training with user feedback.

## Summary

- **LoRA (Low-Rank Adaptation) is the dominant technique** for personalizing diffusion models
  (SDXL, FLUX, SD 1.5/2.1). It trains a small number of low-rank matrices injected into the
  attention layers instead of all weights — quality "on par with full fine-tuning" at a
  fraction of the parameters, producing 3–200 MB `.safetensors` adapters rather than multi-GB
  checkpoints [L4:established]. **DreamBooth** is the *method* (personalize from 3–5 subject
  images with a trigger word); **LoRA** is the *parameter-efficient mechanism* — they are
  routinely combined ("DreamBooth LoRA") [L4:established].
- **Two canonical tooling stacks**: (1) HuggingFace **diffusers** training scripts
  (`train_dreambooth_lora_flux.py`, SDXL equivalents) driven by `accelerate` + PEFT, and (2)
  **Kohya_ss** (kohya-ss/sd-scripts), a GUI/CLI trainer that consumes a TOML config and is the
  de-facto community tool for SDXL LoRAs [L4:established].
- **AWS gives two training tiers**: **SageMaker training jobs** (ephemeral, serverless,
  pay-per-use, minutes to start, single-to-few instances) for periodic/one-off LoRA/DreamBooth
  jobs; **SageMaker HyperPod** (persistent resilient clusters, SLURM or EKS orchestration,
  hours to set up but persists, up to hundreds of instances, auto-recovery checkpointing) for
  large-scale/continuous/foundation-model training [L4:established]. For a single LoRA on
  SDXL/FLUX, a training job on one GPU instance is the right tier; HyperPod is for org-scale or
  continuous training [L1:verified internal + L4].
- **There IS internal Amazon prior art** for exactly this gap: an AWS SA built a full
  end-to-end SageMaker + Kohya SDXL LoRA fine-tuning solution (CloudFormation →
  CodeCommit/CodeBuild → ECR → SageMaker training job → LoRA `.safetensors` in S3), presented on
  Broadcast with a public GitHub sample. HyperPod also ships a "Fine-tuning Platform" sample and
  HyperPod **recipes** for fine-tuning [L1:verified].
- **The data flywheel** is the pattern that closes the loop: production usage (prompt/response
  logs, user feedback, expert labeling) becomes curated training data that improves the model,
  which attracts more usage — a self-reinforcing cycle. Best documented by NVIDIA (NeMo
  microservices, Data Flywheel Blueprint) but the pattern is platform-agnostic [L4:established].

## LoRA / fine-tuning workflows

### What LoRA is and why it's the default

LoRA is a fine-tuning technique that makes slight adjustments to the crucial **cross-attention
layers where images and prompts intersect**. It "achieves quality on par with full fine-tuned
models while being much faster and requiring less compute" [L4:established —
huggingface-blog/sdxl_lora_advanced_script]. Historically (per an internal AWS re:Post answer)
LoRA adapted to DreamBooth meant training only ~3–5M parameters (the attention layer), cutting a
1K-step run to ~8 minutes on 6 GB VRAM and producing a 3–6 MB output vs a full DreamBooth +5 GB
checkpoint [L6:reported — re:Post post 330827, 4 years old, early-LoRA numbers].

**Modern architecture note (matters for FLUX/SD3):** LoRA was first applied to the **UNet**
cross-attention layers. SOTA text-to-image models (FLUX, SD3) replaced the UNet with a
**diffusion Transformer (DiT)**, so LoRA now targets DiT blocks — attention projections
(`attn.to_k/to_q/to_v/to_out.0`), and optionally the added projections and feed-forward layers.
The diffusers `--lora_layers` flag lets you name exact modules/blocks [L4:verified — diffusers
README_flux.md].

### DreamBooth vs LoRA vs full fine-tuning

- **DreamBooth**: method to personalize a text→image model from just 3–5 images of a subject,
  binding it to a rare "trigger word" [L4:verified — diffusers README_flux].
- **LoRA**: parameter-efficient mechanism (low-rank adapters). "DreamBooth LoRA" = DreamBooth
  method implemented with LoRA adapters — the common combination.
- **Full fine-tuning / full checkpoint**: trains all weights; highest fidelity, multi-GB output,
  much higher VRAM. Kohya supports this ("DreamBooth / fine-tuning" tab) but LoRA is preferred
  for cost and portability [L4:established].

### Key hyperparameters (diffusers FLUX/SDXL, verified)

- **`--rank`** — dimension of the trainable LoRA matrices. Higher rank = more expressiveness +
  more parameters + larger output file.
- **`--lora_alpha`** — scaling factor; the LoRA update is scaled by `lora_alpha / rank`.
  - `alpha == rank` → scaling 1.0 (applied at learned strength). Common starting point.
  - `alpha < rank` → dampens (subtle changes, avoid overpowering base). e.g. alpha=8, rank=16.
  - `alpha > rank` → amplifies (lets a low-rank LoRA hit harder). e.g. alpha=32, rank=16.
  - Rule of thumb: start `alpha == rank`; some set `alpha = 2×rank`; halve alpha if "overcooking"
    [L4:verified — diffusers README_flux].
- **Optimizer**: `prodigy` (adaptive; "eliminates" manual LR tuning — set `--learning_rate=1.0`)
  or `adamw` (+ `--use_8bit_adam` for memory) [L4:verified].
- **`--max_train_steps`**: example scripts use ~500–1000; Kohya SDXL example ran ~2500 steps for
  35 images [L1:verified internal video].
- **Text-encoder training**: optional (`--train_text_encoder`). FLUX has two encoders (CLIP L/14
  + T5-XXL); only CLIP is fine-tunable in diffusers today, T5 stays frozen [L4:verified].

### Memory requirements & optimizations (the real cost driver)

- **FLUX LoRA is memory-intensive**: a rank-16 LoRA with all components trained "can exceed 40 GB
  of VRAM" [L4:verified — diffusers README_flux]. SDXL LoRA is much lighter (community trains on
  6–12 GB with Kohya) [L4:established].
- Memory levers (diffusers, verified): lower `--resolution` (default 512; SDXL wants 1024 for
  good results), `--gradient_accumulation_steps` (>1 reduces passes), `--gradient_checkpointing`
  (recompute activations, slower backward), `--use_8bit_adam` (bitsandbytes), `--cache_latents`
  (pre-encode with VAE then free it), and saving LoRA layers in bf16 [L4:verified].
- **Instance sizing implication**: FLUX LoRA needs an A100/H100-class GPU (40–80 GB) → SageMaker
  `ml.p4d/p4de/p5`; SDXL LoRA fits on `ml.g5` (A10G 24 GB). The internal Kohya demo used a
  `p3.8xlarge`-class ("8 XL") and ~1 hour for 2500 steps [L1:verified internal + L4 inference].

### Kohya_ss workflow (community + internal-adopted stack)

Kohya is a GUI tool with a CLI that accepts a config file so it can run headless/programmatically
— exactly what the internal SageMaker solution uses [L1:verified internal video]. Kohya expects a
specific **folder-naming convention** for training data: `NN_triggerword_classname` where `NN` is
the repetition count per image (higher = more steps, longer training). Each image gets a matching
`.caption`/`.txt` caption file describing the image, which improves prompt binding
[L1:verified internal video].

### Video models

Video diffusion (e.g. Stable Video Diffusion, and newer WAN/CogVideoX-class models) is LoRA-able
in principle and the same PEFT/diffusers machinery applies, but this research surfaced far less
canonical AWS tooling for video LoRA than for image — flagged as an open question below.
(Internal "Accelerating Inference for Stable Diffusion Models" wiki notes `stable-fast` supports
`StableVideoDiffusionPipeline` on the *inference* side, not training [L1:verified].)

## AWS training tiers (SageMaker jobs vs HyperPod)

Primary source: AWS Builder Center / re:Post decision guide "Choosing Between Amazon SageMaker
Training Jobs and Amazon SageMaker HyperPod" [L4:established] + internal AIM205 re:Invent talk
[L1:verified].

### SageMaker training jobs (ephemeral / serverless)

- Managed, on-demand, **serverless** training tasks. You hand SageMaker an estimator (container +
  `entry_point` script + instance type/count + hyperparameters) and it provisions, runs, and
  tears down.
- **Best for**: periodic training, smaller models, single-to-few instances, dev/testing, limited
  budgets. **This is the right default tier for a single SDXL/FLUX LoRA or DreamBooth job.**
- **Cost model**: pay only for actual training time, no minimum commitment, higher per-hour rate,
  infra management included.
- **Setup time**: minutes. **Checkpointing**: basic. **Scale**: single to few instances.
- Managed service handles cluster provisioning, workload orchestration, and cluster teardown —
  "customers can focus on the code" [L1:verified — AIM205].
- **Warm pools** (`keep_alive_period_in_seconds`) keep the training instance alive after a job so
  iterative hyperparameter tuning avoids cold-start provisioning [L1:verified — internal GPT-OSS
  fine-tuning wiki].

### SageMaker HyperPod (persistent clusters)

- Provisions **resilient, persistent clusters** for ML training and developing state-of-the-art
  models — LLMs, **diffusion models**, and foundation models. Removes the heavy lifting of
  building/maintaining large accelerator clusters [L4:established — repost, explicitly names
  diffusion models].
- **Orchestration**: SLURM or Amazon EKS. Gives OS-level control (change drivers, model-parallel
  strategies, custom libraries) that training jobs don't [L1:verified — AIM205].
- **Best for**: training/fine-tuning LLMs & foundation models needing significant compute,
  production-scale distributed training with persistent infra, long-running research with heavy
  HPO and continuous improvement.
- **Cost model**: reserved capacity or on-demand + storage for persistence. Claims **up to 40%
  lower model-development cost** via task governance/queueing and resource sharing; EC2 **spot**
  support can save up to 90% on instances; multi-instance GPU (MIG) can split one GPU across up
  to 7 workloads [L1:verified — internal HyperPod videos].
- **Setup time**: hours (but persists). **Checkpointing**: advanced with auto-recovery. **Scale**:
  up to hundreds of instances. Elastic training can dynamically rescale/reshard mid-run
  [L4:established].
- **Flexible training plans**: reserve GPU capacity up to **8 weeks in advance**; once reserved,
  usable within ~30 minutes — predictable access to scarce GPUs [L1:verified — AIM205].
- HyperPod now also does **inference/serving** (KV caching, intelligent routing, deploy FMs on
  HyperPod-EKS) — so a cluster can train, fine-tune, and serve [L1:verified — internal videos].

### HyperPod recipes (bridges both tiers)

SageMaker **HyperPod recipes** are pre-built fine-tuning/pre-training configurations that run on
*both* HyperPod clusters and SageMaker training jobs — the same recipe, two execution backends.
Demonstrated for LLM fine-tuning in AIM205; the pattern generalizes to diffusion fine-tuning
[L1:verified — AIM205 title + talk].

### Decision matrix (for the training tier)

| Situation | Tier |
|---|---|
| One SDXL/FLUX LoRA, occasional retrains, small team | **Training job**, single GPU instance |
| Iterative HPO loop, many short runs | **Training job + warm pools** |
| Continuous/scheduled retraining, org-scale, many concurrent jobs, scarce-GPU reservation | **HyperPod** (SLURM/EKS, flexible training plans) |
| Full foundation-model or large multi-node distributed training | **HyperPod** |
| Want one config to run either place | **HyperPod recipes** |

Rough cost anchors [L5:reported — third-party estimate, treat as order-of-magnitude]: light
experimentation ≈ $89/mo; a 4-node HyperPod cluster for a month ≈ $29,374. Confirm against the
SageMaker pricing page before quoting.

## Data flywheel pattern

**Definition**: a self-reinforcing cycle — data collected from user interactions improves the
model, which delivers better results, which attracts more users who generate more data, further
enhancing the system in a continuous improvement loop [L4:established — NVIDIA glossary]. The
"data exhaust" is production prompt/response logs, end-user feedback (thumbs up/down, accept/
reject, edits), and expert labeling [L4:verified — NVIDIA Data Flywheel Blueprint README].

**Applied to a generative-image LoRA product** (the pattern for this project's training tier):

1. **Serve** the base model + hosted LoRAs; capture generations, prompts, and the LoRA/weights
   used.
2. **Collect feedback**: explicit (user keeps/downloads/favorites an image, rates it, picks among
   a batch) and implicit (regeneration = dissatisfaction; the winning seed/sampler).
3. **Curate**: filter to high-quality accepted outputs; pair images with their prompts/captions
   to form new training pairs. (The internal Kohya demo stresses "the dataset you use is very
   critical" — high-res, hand-picked, captioned images [L1:verified].)
4. **Train**: launch a SageMaker training job (or HyperPod for scale) to fine-tune a new/updated
   LoRA on the curated set.
5. **Evaluate & redeploy**: gate on quality metrics, then hot-swap the LoRA into the serving
   tier. NVIDIA's blueprint automates the evaluate→distill→redeploy leg [L4:established].

**Feedback-driven fine-tuning refinements** worth teaching: **curriculum learning** (introduce
training data progressively by complexity) and **MAPE control loops** (Monitor-Analyze-Plan-
Execute) to systematically turn negative samples into targeted training data — a 3-month study
collected 495 negative RAG samples to close the loop [L4:established — NVIDIA code-review post;
L4:reported — arXiv 2510.27051]. These are LLM-centric writeups; the loop structure transfers to
image models, the curation/labeling specifics differ (aesthetic/preference scoring vs text
correctness).

**Caveat**: the richest flywheel documentation is NVIDIA/NeMo (LLM + distillation focused) and a
RAG-agent paper. I did **not** find a canonical AWS-published image-diffusion data-flywheel
reference; the pattern is sound and platform-agnostic but the image-specific automation is
assembled from parts (SageMaker training jobs + S3 feedback store + eval), not a turnkey AWS
blueprint. Flagged as an open question.

## Internal prior art (cite URLs)

- **Fine-tune Stable Diffusion XL (SDXL) with Kohya** — internal Broadcast talk by an AWS Senior
  SA (US West). A complete, IaC-automated SDXL **LoRA** fine-tuning solution on SageMaker,
  explicitly built *because* "Bedrock and SageMaker JumpStart are currently not fine-tunable for
  SDXL 1.0." Architecture: CloudFormation provisions everything → source in **CodeCommit** →
  EventBridge triggers **CodeBuild** to build the Kohya training container → pushed to **ECR** →
  **SageMaker pipeline** pulls the image + training assets (images + captions + Kohya TOML config)
  from **S3** → **SageMaker training job** runs Kohya headless → outputs a **LoRA `.safetensors`**
  back to S3 → load into a WebUI (AUTOMATIC1111) `models/Lora` folder for inference. ~35 images,
  ~2500 steps, ~1 hour on an "8 XL"-class GPU instance. Inference hosting was noted as the "next
  iteration" (not yet a SageMaker endpoint). Forked from the official aws/amazon-sagemaker-examples
  repo (`use-cases/text-to-image-fine-tuning`).
  https://broadcast.amazon.com/videos/942863 [L1:verified — full transcript read]
- **AWS Samples: Amazon SageMaker HyperPod Fine-tuning Platform** — internal Broadcast sample
  (Frontier AI Startups). HyperPod-based fine-tuning platform.
  https://broadcast.amazon.com/videos/2008368 [L1:verified it exists; transcript not retrievable]
- **AIM205 (re:Invent): Fine-tuning LLMs with Amazon SageMaker HyperPod and SageMaker Training
  Jobs using HyperPod recipes** — the canonical internal explainer of the two-tier model (managed
  training jobs vs OS-level-control HyperPod), recipes that run on both, and flexible training
  plans (reserve capacity 8 weeks ahead). https://broadcast.amazon.com/videos/1519815
  [L1:verified — partial transcript read]
- **Serving GenAI models at scale with SageMaker HyperPod** — one-click cluster, EC2 spot (up to
  90% savings), MIG (split 1 GPU across 7 workloads), Jupyter on HyperPod, ~40% TCO reduction.
  https://broadcast.amazon.com/videos/1859173 [L1:verified — partial transcript]
- **Deploy Foundation models on SageMaker HyperPod-EKS** — HyperPod's arc from train/fine-tune to
  full lifecycle incl. serving. https://broadcast.amazon.com/videos/1645017 [L1:verified — partial]
- **Domain-Adapt and Fine-Tune OpenAI GPT-OSS Models on SageMaker AI Using Hugging Face
  Libraries** — internal wiki. Two-stage (continued pre-training → SFT) with HF **TRL** +
  **Accelerate** + **DeepSpeed ZeRO-3**, full-param training of a 20B MoE on a single
  `ml.p4de.24xlarge` (8 GPUs). Directly relevant knobs: **`use_peft: true` + `lora_r: 64,
  lora_alpha: 128`** to fine-tune a fraction of params for resource-constrained runs;
  `keep_alive_period_in_seconds` **warm pools** for fast iteration; `EarlyStoppingCallback`;
  sequence packing. Text-LLM not diffusion, but the SageMaker-job mechanics, PEFT/LoRA config,
  and warm-pool pattern transfer directly.
  https://w.amazon.com/bin/view/Networking/NMR/NetworkAi/NetworkAssistant/LLM-finetuning/
  [L1:verified — read]
- **How do you host a Stable Diffusion fine-tuning SaaS on SageMaker?** — internal re:Post Q&A on
  architecting an SD fine-tuning *service* (cellular multi-account/multi-region vs batched
  create-training-job per customer, GPU packing). Confirms "many just use SM training jobs in the
  back." Old (4 yrs) but the SaaS-scaling framing is still useful.
  https://answers.amazon.com/posts/330827 [L6:reported]
- **Accelerating Inference for Stable Diffusion Models** — internal 3P Model Team blog. fp16 VAE,
  DeepSpeed, `stable-fast` (supports LoRA/ControlNet + `StableVideoDiffusionPipeline`). Inference,
  not training, but pairs with the training tier for the serve leg.
  https://w.amazon.com/bin/view/Users/fnp/3PModTeam/blog/2024/09/AccelInferenceStableDiffusion/
  [L1:verified]
- **Running POCs with Neuron** (Inferentia/Trainium) — SDXL/SD1.5/2.1 supported on Neuron; LoRA
  adapters for Stable Diffusion supported via Optimum-Neuron 0.1.0 (ip-adapters). Note the Neuron
  "LORA adapter note": for LLMs adapters must be *fused* for inference. Relevant if training/serving
  on Trainium/Inferentia instead of GPU. https://w.amazon.com/bin/view/Inferentia/inferentia/POCs/
  [L1:verified]

## Sources (URLs + [L#:confidence])

Internal:
- https://broadcast.amazon.com/videos/942863 — SDXL+Kohya SageMaker LoRA solution [L1:verified]
- https://broadcast.amazon.com/videos/2008368 — HyperPod Fine-tuning Platform sample [L1:verified exists]
- https://broadcast.amazon.com/videos/1519815 — AIM205 HyperPod + training jobs + recipes [L1:verified]
- https://broadcast.amazon.com/videos/1859173 — Serving GenAI at scale on HyperPod [L1:verified]
- https://broadcast.amazon.com/videos/1645017 — Deploy FMs on HyperPod-EKS [L1:verified]
- https://w.amazon.com/bin/view/Networking/NMR/NetworkAi/NetworkAssistant/LLM-finetuning/ — GPT-OSS SageMaker fine-tune (PEFT/LoRA, warm pools, DeepSpeed) [L1:verified]
- https://answers.amazon.com/posts/330827 — SD fine-tuning SaaS on SageMaker architecture Q&A [L6:reported]
- https://w.amazon.com/bin/view/Users/fnp/3PModTeam/blog/2024/09/AccelInferenceStableDiffusion/ — SD inference optimization [L1:verified]
- https://w.amazon.com/bin/view/Inferentia/inferentia/POCs/ — Neuron SD + LoRA adapter support [L1:verified]

AWS official / docs:
- https://repost.aws/articles/ARqYgZU7-kTjOYeoi8pZ94ZA/choosing-between-amazon-sagemaker-training-jobs-and-amazon-sagemaker-hyperpod-a-quick-decision-making-guide-for-ml-workloads — decision guide [L4:established]
- https://aws.amazon.com/sagemaker/hyperpod/ — HyperPod product (up to 40% cost reduction) [L4:established]
- https://aws.amazon.com/blogs/machine-learning/reduce-ml-training-costs-with-amazon-sagemaker-hyperpod/ [L4:established]
- https://aws.amazon.com/blogs/machine-learning/adaptive-infrastructure-for-foundation-model-training-with-elastic-training-on-sagemaker-hyperpod [L4:established]
- https://docs.aws.amazon.com/sagemaker/latest/dg/sagemaker-hyperpod-gpu-sagemaker-training-jobs-pretrain-tutorial.html — training-job pretrain tutorial [L4:verified]
- https://aws.amazon.com/blogs/machine-learning/generative-ai-foundation-model-training-on-amazon-sagemaker/ [L4:established]

Third-party (technique canon):
- https://github.com/huggingface/diffusers/blob/main/examples/dreambooth/README_flux.md — FLUX DreamBooth/LoRA scripts, rank/alpha, 40GB VRAM, memory opts, Kontext [L4:verified]
- https://github.com/huggingface/diffusers/blob/main/examples/advanced_diffusion_training/README_flux.md — advanced FLUX DreamBooth LoRA [L4:established]
- https://huggingface.co/blog/linoyts/new-advanced-flux-dreambooth-lora — advanced FLUX LoRA blog [L4:established]
- huggingface-blog/sdxl_lora_advanced_script.md — SDXL LoRA (cross-attention, on-par quality) [L4:established]
- https://github.com/kohya-ss/sd-scripts (via FurkanGozukara SDXL/Kohya tutorials) — Kohya trainer [L4:established]
- https://github.com/cloneofsimo/lora — original LoRA-for-diffusion repo [L6:reported, historical]

Data flywheel:
- https://www.nvidia.com/en-us/glossary/data-flywheel/ — definition [L4:established]
- https://github.com/NVIDIA-AI-Blueprints/data-flywheel/blob/main/README.md — data exhaust definition [L4:verified]
- https://developer.nvidia.com/blog/maximize-ai-agent-performance-with-data-flywheels-using-nvidia-nemo-microservices/ [L4:established]
- https://developer.nvidia.com/blog/fine-tuning-small-language-models-to-optimize-code-review-accuracy/ — curriculum learning + flywheel [L4:established]
- https://arxiv.org/html/2510.27051v1 — MAPE control loops for AI agent improvement [L4:reported]

Pricing (order-of-magnitude only):
- https://markaicode.com/pricing/amazon-sagemaker-pricing/ — $89/mo experimentation, ~$29,374/mo 4-node HyperPod [L5:reported]

## Open questions

1. **Video LoRA on AWS** — no canonical AWS training tooling surfaced for video-diffusion LoRA
   (SVD/WAN/CogVideoX). Is there an internal sample, or is it "bring your own diffusers/PEFT script
   to a p5 training job"? Video's higher VRAM/temporal-consistency needs likely push toward multi-
   GPU HyperPod. Needs a targeted search.
2. **Turnkey AWS image data-flywheel** — the flywheel canon is NVIDIA/NeMo (LLM-centric). Is there
   an AWS reference architecture for an *image* preference→LoRA-retrain loop (e.g. SageMaker +
   feedback store + aesthetic/preference scorer + auto-retrain), or must it be assembled from
   training jobs + S3 + eval?
3. **Preference/quality scoring for image curation** — LLM flywheels use LLM-as-judge; image
   curation needs aesthetic predictors / human preference models. Which are recommended on AWS?
4. **FLUX.1 [dev] licensing** — it's a *gated* model (accept the gate + auth). Are there
   commercial-use / redistribution constraints that affect a hosted LoRA-training product? Not
   investigated here.
5. **Current SageMaker JumpStart / Bedrock fine-tuning status for SDXL/FLUX** — the internal Kohya
   solution exists *because* JumpStart/Bedrock couldn't fine-tune SDXL 1.0 (as of the talk, ~2024).
   Has that changed? Would remove the need for a custom training container if so.
6. **Exact instance recommendations & current pricing** — confirm `ml.g5` (SDXL) vs `ml.p4d/p5`
   (FLUX) sizing and live per-hour rates against the SageMaker pricing page before quoting cost.
