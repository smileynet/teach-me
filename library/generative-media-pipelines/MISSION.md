# Mission: Understand generative media pipelines on AWS

## Why

Turning "a research model on a GPU" into "a capability a creative team actually uses" is a
platform problem, not a model problem. Three real platforms — a custom scale-to-zero orchestrator,
an artist web studio over Bedrock + SageMaker, and a ComfyUI-on-EKS platform — all solve the same
core: host arbitrary generative models on GPUs, serve them through a stable async interface, and
don't pay for idle GPUs. This track teaches that shared architecture so "how do we host and serve
image/video/speech/3D generation?" becomes a design you reason about, not a wheel you reinvent —
and so you know which AWS reference pattern each hand-rolled orchestrator is really re-implementing.

## Success looks like

- Can draw the universal serving pipeline (client → auth → submit → queue → scale-to-zero GPU
  worker → weight staging → infer → output store → progress stream) and name where each of the
  three platforms diverges
- Can choose a scale-to-zero path (SageMaker Async vs Inference-Component minCopies=0 vs
  EKS Karpenter+KEDA vs Bedrock) for a given workload and justify it against cold-start cost
- Can explain onboarding-as-data (manifest/registry/workflow-container) vs per-model endpoints,
  and why weights never live in the image
- Can host ComfyUI headlessly (the /prompt + /ws + /history contract) and name its scaling traps
- Can place LoRA correctly: a hosted category, trained in a separate tier (SageMaker Training Jobs
  vs HyperPod) — not in the serving platform

## Constraints

- Architecture-agnostic where possible; AWS-specific where the reference patterns are AWS
  (SageMaker, Bedrock, EKS/Karpenter/KEDA, FSxN)
- Every load-bearing claim cites a source: a repo file path (the three explored platforms) or an
  `[L#:confidence]`-tagged external/internal source (the gap research) — no parametric memory
- Conceptual track — validation is source-verification + `mise run verify` (links/lint/SVG/glossary),
  not a runtime code harness
- Adjacent to gltf-format / godot-asset-pipeline (image→3D *output* feeds them) — reference, don't
  duplicate their engine-import mechanics
