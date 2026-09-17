# Resources

Verified sources for the generative-media-pipelines workspace. Two tiers: the **explored platform
repos** (primary, L1 — the code that implements these patterns) and the **prior-art research**
(L2-L5 — AWS docs, internal wiki, external guides). Full findings with per-claim tags live in
`.memory/research/world-models-and-genmedia/`.

## Primary sources — the three platform repos (L1:verified, via .references/ symlinks)

| Repo | What it demonstrates |
|------|----------------------|
| `studio-model-service` | Custom scale-to-zero orchestrator: manifest registry, SQS FIFO, claim→commit, cold-start SLO, runner strategies |
| `ArtSmoker` | Artist studio over Bedrock + self-deployed SageMaker; universal inference handler; two-level 2D pipeline; 1-click deploy; image→3D + engine export |
| `riot-comfy-ui-platform` | ComfyUI on EKS (headless) + AppStream (UI); FSxN+FlexClone model store; KEDA autoscaling; vending/approval governance |

Per-repo findings (every claim file-path-cited):
`.memory/research/world-models-and-genmedia/repo-findings/{studio-model-service,artsmoker,riot-comfy-ui-platform}.md`

## Prior-art research (gap-research/, tagged [L#:confidence])

| Topic area | Source (representative) | Trust |
|------------|-------------------------|-------|
| Scale-to-zero serving | "Deploying Open Models on AWS: A Decision Guide" (`w.amazon.com/bin/view/Ai-inference/decision-matrix/`) | L4:established |
| SageMaker Async / Inference Components | AWS SageMaker docs (async inference, scale-to-zero minCopies) | L4:verified |
| Cold-start mitigation | SageMaker Fast Model Loader, Container Caching, SOCI lazy loading (AWS docs) | L4:verified |
| ComfyUI at scale | `aws-samples/comfyui-on-eks`, `cost-effective-aws-deployment-of-comfyui` (GitHub) | L4:established |
| ComfyUI API surface | ComfyUI official docs (/prompt, /ws, /history, /object_info) | L4:verified |
| LoRA / fine-tuning | HuggingFace diffusers + Kohya_ss docs; internal broadcast 942863 "Fine-tune SDXL with Kohya" | L4:established |
| SageMaker Training vs HyperPod | AWS SageMaker HyperPod docs + AIM205 recipes talk | L4:verified |
| image→3D models | TRELLIS.2 / Hunyuan3D / TripoSG / TripoSR model cards + papers; internal IML "3D assets from product images" | L2-L4 |
| Hunyuan3D licensing | Tencent Hunyuan3D non-commercial license (territorial carve-out) | L2:verified |
| Speech generation | Amazon Polly + Nova Sonic docs; internal Connect UTTS / XBLocalizedVideo dubbing | L4:established |

Gap-research files: `.memory/research/world-models-and-genmedia/gap-research/*.md`

## Source-authority note

Where a repo and an external doc conflict, the running code (L1) wins for "what this platform
does"; the AWS doc (L4) wins for "what the managed service supports." The `riot-comfy-ui-platform`
package did not surface in InternalSearch — the AWS ComfyUI reference samples are prior art,
verified independently, not claims about that repo.
