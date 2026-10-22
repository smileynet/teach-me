# Resources

Verified sources for the generative-media-pipelines workspace. Two tiers: three **explored
platforms** (primary, L1 — non-public codebases that implement these patterns, described here
generically) and the **prior-art research** (L2-L5 — public AWS docs and external guides).

## Primary sources — three platforms (L1:verified, non-public)

| Platform | What it demonstrates |
|----------|----------------------|
| DCC service (a custom scale-to-zero model service) | Custom scale-to-zero orchestrator: manifest registry, SQS FIFO, claim→commit, cold-start SLO, runner strategies |
| Artist studio (a web studio over Bedrock + SageMaker) | Artist studio over Bedrock + self-deployed SageMaker; universal inference handler; two-level 2D pipeline; 1-click deploy; image→3D + engine export |
| ComfyUI platform (a game studio's ComfyUI platform on EKS) | ComfyUI on EKS (headless) + AppStream (UI); FSxN+FlexClone model store; KEDA autoscaling; vending/approval governance |

## Prior-art research (tagged [L#:confidence])

| Topic area | Source (representative) | Trust |
|------------|-------------------------|-------|
| SageMaker Async / Inference Components | AWS SageMaker docs (async inference, scale-to-zero minCopies) | L4:verified |
| Cold-start mitigation | SageMaker Fast Model Loader, Container Caching, SOCI lazy loading (AWS docs) | L4:verified |
| ComfyUI at scale | `aws-samples/comfyui-on-eks`, `cost-effective-aws-deployment-of-comfyui` (GitHub) | L4:established |
| ComfyUI API surface | ComfyUI official docs (/prompt, /ws, /history, /object_info) | L4:verified |
| LoRA / fine-tuning | HuggingFace diffusers + Kohya_ss docs | L4:established |
| SageMaker Training vs HyperPod | AWS SageMaker HyperPod docs + AIM205 recipes talk | L4:verified |
| image→3D models | TRELLIS.2 / Hunyuan3D / TripoSG / TripoSR model cards + papers | L2-L4 |
| Hunyuan3D licensing | Tencent Hunyuan3D non-commercial license (territorial carve-out) | L2:verified |
| Speech generation | Amazon Polly + Nova Sonic docs | L4:established |

## Source-authority note

Where a platform and an external doc conflict, the running code (L1) wins for "what this
platform does"; the AWS doc (L4) wins for "what the managed service supports." The AWS ComfyUI
reference samples are prior art, verified independently, not claims about the ComfyUI platform.
