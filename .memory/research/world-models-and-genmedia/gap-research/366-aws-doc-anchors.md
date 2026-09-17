# 366 — AWS Doc Anchors for SERVING Real-Time Video/World Models on AWS Accelerators

Research target: find a canonical AWS-doc through-line for the world-models domain's
**serving** topic — the way SageMaker Async Inference anchors the sibling
generative-media-pipelines domain. The serving story for real-time world models splits
into three doc families: (a) Trainium/Neuron inference + parallelism, (b) real-time /
streaming serving on SageMaker, (c) inference optimization (step reduction, distillation,
speculative decoding).

## Summary

Two families carry the weight. For **accelerator-native serving**, the AWS Neuron SDK docs
(`awsdocs-neuron.readthedocs-hosted.com`) are the authoritative first-party source — NxD
Inference (NeuronX Distributed Inference) is the deploy library, NKI is the custom-kernel
escape hatch, and the parallelism techniques (tensor/sequence/context) live inside the NxD
Core + NxD Inference guides. For **real-time delivery to a client**, the SageMaker Developer
Guide's Real-time inference section (`docs.aws.amazon.com/sagemaker`) plus the response-streaming
API (`InvokeEndpointWithResponseStream`) are canonical. Inference optimization has its own
first-party SageMaker page (`model-optimize.html`) covering quantization, speculative decoding,
and compilation.

Note on scope: AWS has **no dedicated real-time _video_ generation doc** yet. The closest
first-party artifacts are the diffusion-transformer inference blogs (PixArt-Σ, Stable Diffusion
on Inf2/Trn) — L4/L5, not reference docs. The honest anchor for a "serving real-time world
models" lesson is the Neuron NxD Inference guide (accelerator serving) threaded with SageMaker
real-time + response streaming (client delivery), with the diffusion blogs as the concrete
"video/diffusion on this hardware" evidence layer.

## Neuron/Trainium inference docs (URLs)

- **NxD Inference (NeuronX Distributed Inference) — index** — the deploy library for LLMs/DiT
  on Inf2/Trn; continuous batching, speculative decoding, model support.
  https://awsdocs-neuron.readthedocs-hosted.com/en/latest/libraries/nxd-inference/index.html
- **NxD Inference — Model Support (incl. vLLM integration)** — which models are supported and
  how to configure online vs offline; anchors "can my world model even run here."
  https://awsdocs-neuron.readthedocs-hosted.com/en/latest/libraries/nxd-inference/models/index.html
- **Work with training and inference libraries (NxD ecosystem overview)** — the layered NxD
  architecture (Core primitives → training/inference); anchors where parallelism lives.
  https://awsdocs-neuron.readthedocs-hosted.com/en/latest/libraries/
- **NxD Core — index** — the distributed primitives package (XLA-friendly TP/PP/SP
  implementations) underneath NxD Inference.
  https://awsdocs-neuron.readthedocs-hosted.com/en/latest/libraries/neuronx-distributed/index.html
- **Neuron Kernel Interface (NKI) — index** — bare-metal language/compiler for custom operators
  on NeuronCores; the escape hatch for fusing a diffusion/attention kernel the compiler won't.
  https://awsdocs-neuron.readthedocs-hosted.com/en/latest/nki/index.html
- **NKI Language Guide (programming model)** — the "learn NKI" entry point: tile-level model,
  key concepts for writing kernels.
  https://awsdocs-neuron.readthedocs-hosted.com/en/latest/nki/programming_model.html
- **NKI API reference (nki.language)** — high-level constructs (tensor creation, math, loops)
  the compiler lowers to hardware.
  https://awsdocs-neuron.readthedocs-hosted.com/en/latest/nki/api/nki.language.html
- **Activation Memory Reduction developer guide (tensor + sequence parallelism)** — the concrete
  doc that names ColumnParallel/RowParallel linear layers and `sequence_parallel_enabled`;
  anchors the "how tensor/sequence parallel is actually wired" claim.
  https://awsdocs-neuron.readthedocs-hosted.com/en/latest/libraries/neuronx-distributed/activation_memory_reduction_developer_guide.html
- **vLLM Neuron Plugin (Beta)** — full vLLM serving stack on Trainium: continuous batching,
  EAGLE3 speculative decoding, disaggregated inference, multimodal, OpenAI-compatible API.
  https://awsdocs-neuron.readthedocs-hosted.com/en/latest/vllm-neuron/docs/index.html
- **NxD Inference GA announcement (What's New, May 2025)** — dates the GA + feature set; use for
  freshness/versioning, not as the teaching anchor.
  https://aws.amazon.com/about-aws/whats-new/2025/05/aws-neuron-nxd-inference-ga/

## Real-time serving docs (URLs)

- **Real-time inference (SageMaker Developer Guide)** — canonical entry for low-latency,
  interactive endpoints; the SageMaker-side counterpart to Async Inference's anchor role.
  https://docs.aws.amazon.com/sagemaker/latest/dg/realtime-endpoints.html
- **Deploy models for real-time inference (inference components)** — multi-model / shared-accelerator
  endpoints via inference components; anchors packing a heavy world model + auxiliaries.
  https://docs.aws.amazon.com/sagemaker/latest/dg/realtime-endpoints-deploy-models.html
- **Invoke models for real-time inference** — how a client calls the endpoint (SDK/CLI/Studio).
  https://docs.aws.amazon.com/sagemaker/latest/dg/realtime-endpoints-test-endpoints.html
- **InvokeEndpointWithResponseStream (API Reference)** — THE streaming API: payload delivered
  incrementally as parts; the anchor for streaming a frame/token sequence back in real time.
  https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_runtime_InvokeEndpointWithResponseStream.html
- **Invoke endpoints with OpenAI-compatible APIs** — `/v1/chat/completions`-style path on
  SageMaker real-time endpoints; anchors "keep your existing streaming client."
  https://docs.aws.amazon.com/sagemaker/latest/dg/realtime-endpoints-openai-compatible.html
- **Hosting FAQ (endpoint-type sizing table)** — the authoritative limits: real-time = ms latency,
  ≤25 MB payload, 60 s regular / 8 min streaming; the "which endpoint type" decision anchor.
  https://docs.aws.amazon.com/sagemaker/latest/dg/hosting-faqs.html
- **Deploy models for inference (options overview)** — real-time vs serverless vs async;
  anchors the sibling-domain contrast (this domain = real-time, media-pipelines = async).
  https://docs.aws.amazon.com/sagemaker/latest/dg/deploy-model.html
- **Blog: Introducing streaming support in Amazon SageMaker hosting** — explains the HTTP/1.1
  chunked-encoding mechanism behind response streaming (the SSE/WebSocket-adjacent pattern).
  https://aws.amazon.com/blogs/machine-learning/elevating-the-generative-ai-experience-introducing-streaming-support-in-amazon-sagemaker-hosting/

## Inference-optimization docs (URLs)

- **Inference optimization for Amazon SageMaker AI models** — canonical first-party page:
  quantization, speculative decoding, compilation as first-class optimization jobs.
  https://docs.aws.amazon.com/sagemaker/latest/dg/model-optimize.html
- **Large model inference with DeepSpeed and DJL Serving (LMI DLCs)** — the LMI container path;
  continuous/rolling batching for high-throughput serving.
  https://docs.aws.amazon.com/sagemaker/latest/dg/large-model-inference-tutorials-deepspeed-djl.html
- **Solution: Generative AI Model Optimization using Amazon SageMaker** — packaged guidance
  combining speculative decoding + quantization + compilation.
  https://docs.aws.amazon.com/solutions/generative-ai-model-optimization-using-amazon-sagemaker/index.html
- **Blog: EAGLE-based adaptive speculative decoding on SageMaker AI** — step/latency reduction
  via speculative decoding; the "generate fewer expensive steps" evidence for real-time.
  https://aws.amazon.com/blogs/machine-learning/amazon-sagemaker-ai-introduces-eagle-based-adaptive-speculative-decoding-to-accelerate-generative-ai-inference/
- **Blog: Cost-effective AI image generation with PixArt-Σ on Trainium and Inferentia** — a real
  diffusion-transformer (DiT) served on AWS accelerators; nearest first-party artifact to a
  video/world-model diffusion serving story.
  https://aws.amazon.com/blogs/machine-learning/cost-effective-ai-image-generation-with-pixart-%CF%83-inference-on-aws-trainium-and-aws-inferentia/
- **Blog: Maximize Stable Diffusion performance and lower inference cost with Inferentia2** —
  diffusion inference latency/cost on Inf2; the step-count/latency framing for generation.
  https://aws.amazon.com/blogs/machine-learning/maximize-stable-diffusion-performance-and-lower-inference-costs-with-aws-inferentia2/
- **Blog: ByteDance multimodal video understanding on Inferentia2** — video-scale inference on
  AWS accelerators at production volume (understanding, not generation; use as scale evidence).
  https://aws.amazon.com/blogs/machine-learning/bytedance-processes-billions-of-daily-videos-using-their-multimodal-video-understanding-models-on-aws-inferentia2/

## Recommended anchor(s) for the serving topic

Thread **two** docs through the serving topic, mirroring how Async Inference anchors the
media-pipelines domain:

1. **NxD Inference (NeuronX Distributed Inference) index** —
   `https://awsdocs-neuron.readthedocs-hosted.com/en/latest/libraries/nxd-inference/index.html`
   — the **accelerator-native serving anchor**. Threads through: (a) "what serves the model on
   Trainium/Inferentia," (b) parallelism (link out to NxD Core + the Activation Memory Reduction
   guide for tensor/sequence parallel; note context parallelism is the long-context extension),
   (c) NKI as the custom-kernel escape hatch when a diffusion/attention op needs hand-tuning.

2. **SageMaker Real-time inference + `InvokeEndpointWithResponseStream`** —
   `https://docs.aws.amazon.com/sagemaker/latest/dg/realtime-endpoints.html` +
   `https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_runtime_InvokeEndpointWithResponseStream.html`
   — the **real-time delivery anchor**. Threads through: (a) why a world model that must emit
   frames continuously uses a real-time endpoint (not async — the deliberate contrast with the
   sibling domain), (b) how the frame/latent stream reaches the client via chunked-encoding
   response streaming, (c) the endpoint-type sizing limits (Hosting FAQ) that force real-time.

Supporting (evidence layer, not the spine): the **PixArt-Σ / Stable-Diffusion-on-Inf2 blogs**
for "a real diffusion transformer served on this hardware," and **`model-optimize.html` +
EAGLE speculative-decoding blog** for the step-reduction/distillation angle that makes
real-time generation feasible.

Topic mapping:
- "What serves the model on the accelerator" → **NxD Inference index** (anchor 1)
- "Parallelism for a model too big for one core" → NxD Core + Activation Memory Reduction guide
- "Custom kernel when the compiler isn't enough" → NKI index + Language Guide
- "Delivering frames in real time to a client" → **SageMaker Real-time + response streaming** (anchor 2)
- "Endpoint type decision (real-time vs async vs serverless)" → deploy-model.html + Hosting FAQ
- "Making generation fast enough (step reduction / spec decoding / quant)" → model-optimize.html + EAGLE blog
- "Diffusion/video on AWS accelerators, concretely" → PixArt-Σ + SD-on-Inf2 blogs

## Sources

- [L4:verified] NxD Inference index — awsdocs-neuron.readthedocs-hosted.com/en/latest/libraries/nxd-inference/index.html (first-party Neuron SDK docs; confirmed via web_search + InternalSearch AWS_DOCS)
- [L4:verified] Work with training/inference libraries (NxD ecosystem) — .../en/latest/libraries/
- [L4:verified] NxD Core index — .../en/latest/libraries/neuronx-distributed/index.html
- [L4:verified] NxD Inference model support / vLLM — .../en/latest/libraries/nxd-inference/models/index.html
- [L4:verified] NKI index — .../en/latest/nki/index.html
- [L4:verified] NKI Language Guide — .../en/latest/nki/programming_model.html
- [L4:verified] NKI API (nki.language) — .../en/latest/nki/api/nki.language.html
- [L4:verified] Activation Memory Reduction dev guide (TP/SP) — .../libraries/neuronx-distributed/activation_memory_reduction_developer_guide.html
- [L4:verified] vLLM Neuron Plugin — .../en/latest/vllm-neuron/docs/index.html
- [L4:verified] SageMaker Real-time inference — docs.aws.amazon.com/sagemaker/latest/dg/realtime-endpoints.html
- [L4:verified] Deploy real-time (inference components) — .../dg/realtime-endpoints-deploy-models.html
- [L4:verified] Invoke real-time inference — .../dg/realtime-endpoints-test-endpoints.html
- [L4:verified] InvokeEndpointWithResponseStream — docs.aws.amazon.com/sagemaker/latest/APIReference/API_runtime_InvokeEndpointWithResponseStream.html
- [L4:verified] OpenAI-compatible endpoints — .../dg/realtime-endpoints-openai-compatible.html
- [L4:verified] Hosting FAQ (endpoint sizing) — .../dg/hosting-faqs.html
- [L4:verified] Deploy models for inference (options) — .../dg/deploy-model.html
- [L4:verified] Inference optimization (SageMaker) — .../dg/model-optimize.html
- [L4:verified] Large model inference DeepSpeed/DJL — .../dg/large-model-inference-tutorials-deepspeed-djl.html
- [L4:verified] GenAI Model Optimization solution — docs.aws.amazon.com/solutions/generative-ai-model-optimization-using-amazon-sagemaker/index.html
- [L5:verified] Blog: SageMaker streaming support (chunked encoding) — aws.amazon.com/blogs/machine-learning/elevating-the-generative-ai-experience-introducing-streaming-support-in-amazon-sagemaker-hosting/
- [L5:verified] Blog: EAGLE adaptive speculative decoding — aws.amazon.com/blogs/machine-learning/amazon-sagemaker-ai-introduces-eagle-based-adaptive-speculative-decoding-...
- [L5:verified] Blog: PixArt-Σ (DiT) on Trainium/Inferentia — aws.amazon.com/blogs/machine-learning/cost-effective-ai-image-generation-with-pixart-...
- [L5:verified] Blog: Stable Diffusion on Inferentia2 — aws.amazon.com/blogs/machine-learning/maximize-stable-diffusion-performance-...
- [L5:verified] Blog: ByteDance video understanding on Inf2 — aws.amazon.com/blogs/machine-learning/bytedance-processes-billions-of-daily-videos-...
- [L6:reported] NxD Inference GA What's New (May 2025) — aws.amazon.com/about-aws/whats-new/2025/05/aws-neuron-nxd-inference-ga/ (dating/versioning only)

## Open

- **Version pinning.** The Neuron docs URLs above use `/en/latest/`. NKI/NxD pages churn per
  release (v2.21 → v2.32 seen in results). For a lesson, pin to a specific version once
  (e.g. the current stable at authoring time) to avoid a `latest`-drift dead link, and note the
  version. `latest` is fine for the through-line anchor if the lesson flags it as tracking-head.
- **Context parallelism specifically.** Confirmed as a documented Neuron parallelism dimension
  in the NxD ecosystem and in general LLM-inference literature (arXiv), but I did not land a
  single canonical `awsdocs-neuron` page titled "context parallelism for inference." The
  Activation Memory Reduction guide + NxD Core index cover TP/SP concretely; CP likely lives in
  an NxD Inference features/config subpage or the Trn2 Llama-405B tutorial — worth one more
  targeted fetch when authoring if the lesson needs a CP-specific citation.
- **No first-party real-time _video generation_ reference doc exists.** Video-generation-on-AWS-
  accelerators is currently blog-level (image DiT: PixArt-Σ, SDXL; video: only ByteDance
  *understanding*). If the lesson claims "real-time video generation on Trainium," frame it as
  extrapolation from DiT image serving + streaming delivery, not as a documented AWS reference
  workflow. Flag this gap to the lesson author.
- **WebSocket/SSE specifics.** AWS's real-time streaming is HTTP/1.1 chunked encoding at the
  SageMaker layer (not native WebSocket). A true WebSocket front is an API Gateway pattern
  layered on top — no single canonical doc surfaced; treat as an architecture pattern (blog/
  solution level) rather than a reference-doc anchor.
