# TTS & Speech/Audio Generation — Gap Research

_Research date: 2026-09-16. Filling the speech-generation gap: five explored repos cover image/video/3D but almost no speech gen (only one STT capability)._

## Summary

AWS covers speech generation on two axes: **managed** (Amazon Polly for TTS with a Generative voice engine + bidirectional streaming; Amazon Nova Sonic / Nova 2 Sonic on Bedrock for real-time speech-to-speech) and **self-hosted** (open TTS/voice-cloning models on SageMaker GPU endpoints). Internal prior art is strong and recent: Connect's **UTTS** (Unified TTS) productionizes 3P TTS models self-hosted on per-cell SageMaker endpoints, **Project Svalbard** documents a full managed→self-hosted fallback matrix including a SageMaker audio-model table (Chatterbox, Kokoro, XTTS-v2, Dia), and **XBLocalizedVideo** runs a GPU dubbing pipeline with CosyVoice2 voice cloning. Speech-gen fits the scale-to-zero GPU pattern the same way image/video models do — SageMaker Async or scale-to-zero real-time endpoints for bursty, cost-sensitive workloads; real-time/provisioned for latency-critical conversational voice.

## AWS-native options

### Amazon Polly (managed TTS)
- Fully-managed text-to-speech: converts text to an audio stream, dozens of lifelike voices across many languages. Engines: standard, neural, and a **Generative voice engine** (the most expressive/human-like tier). [L4:established]
- **Bidirectional Streaming API** (launched ~Mar 2026): real-time speech synthesis for conversational AI — send text incrementally, receive audio incrementally over a persistent stream, reducing time-to-first-audio for voice agents. A March 2026 update added 10 new Generative voices, 2 new regions, and the bidirectional streaming API. [L4:established]
- Controls: SSML (W3C standard) for phrasing/emphasis/intonation, custom lexicons for pronunciation of acronyms/company names, and automatic speech-duration adjustment for multilingual dubbing. Use cases explicitly called out: voiceovers for animations/games/media from scripts, IVR prompts, accessibility. [L4:established]
- Governed by an AWS AI Service Card (Polly), current as of Feb 11, 2026. [L4:verified]

### Amazon Nova Sonic / Nova 2 Sonic (Bedrock speech-to-speech)
- **Nova Sonic**: proprietary foundation model that unifies speech understanding AND generation into ONE model for real-time, human-like voice conversations, low latency, industry-leading price-performance. Takes speech in, outputs speech + text. ~300k-token context (~30 min conversation). Handles interruptions ("barge-in"), function calling, agentic workflows. Originally English/Spanish; July 16 2025 added French/Italian/German + six expressive voices. [L4:established]
- **Nova 2 Sonic** (GA Dec 2 2025): next-generation speech-to-speech FM for conversational AI; more languages than v1; governed by its own AI Service Card (as of Dec 2025). [L4:established]
- Internal note (Voice Internship demos, 2026): as of that recording Nova (2) Sonic was **the only speech-to-speech model on Bedrock**; the two main S2S models supporting telephony audio were Nova Sonic (WebSocket, needs an "AI bridge service") and GPT real-time (SIP, no bridge needed). This is the key AWS-native gen-voice primitive. [L5:reported]
- Pattern reference: "Real-time voice agents with Stream Vision Agents and Amazon Nova 2 Sonic" (AWS ML blog) — production voice-agent orchestration guidance (speech-to-speech model + low-latency audio streaming + connection lifecycle). [L4:established]

### Other AWS audio capabilities (adjacent, not gen-TTS)
- **Amazon Transcribe** — speech-to-TEXT; better than model-native transcription for speaker separation/diarization (single session detects + labels speakers). Complements gen pipelines (e.g., dubbing needs diarization). [L5:reported]
- The **Nova family** positions Sonic as the speech pillar alongside Canvas (image) and Reel (video) — i.e., speech-gen is the audio leg of the Nova generative-media stack. [L4:established]

## Self-hosted / open models

Teams self-host open TTS/voice-cloning models on SageMaker GPU endpoints (or ComfyUI) for full control, no per-request API cost (compute only), and data-never-leaves-AWS compliance. Models seen in internal prior art + external deployment guides:

| Model | Task | License | VRAM / instance | Notes |
|-------|------|---------|-----------------|-------|
| **Chatterbox** (Resemble AI) | TTS + voice cloning | MIT | ~1x T4 (16GB) | Internal Svalbard: "matches ElevenLabs (63.75% pref)". OpenAI-compatible server images exist. [L5/L6] |
| **Kokoro-82M** | TTS (no cloning) | Apache 2.0 | 2–3 GB, runs on CPU | 82M params, ~96x real-time; RTF ~0.03 on A100; tiny footprint → many instances per GPU. Best lightweight narration. [L5/L6] |
| **Coqui XTTS-v2** | TTS + voice cloning | MPL-2.0 (non-commercial caveat) | ~1x T4 | ~6-second voice clone, 17 languages. [L5/L6] |
| **F5-TTS** (SWivid/Shanghai AI Lab) | TTS + zero-shot cloning | open | GPU | Flow-matching DiT; clones from 5–15s reference; rivals commercial APIs on zero-shot. [L6] |
| **Dia-1.6B** (Nari Labs) | Multi-speaker TTS | open | ~1x A10G (24GB) | Realistic multi-speaker dialogue. [L5] |
| **CosyVoice2-0.5B** (Alibaba) | Voice cloning | open | GPU | Used in XBLocalizedVideo dubbing (clone original speaker). [L4:internal] |
| **OpenVoice V2** | Voice cloning | open | GPU | Common in self-host guides alongside XTTS/F5. [L6] |
| **Fish Speech / Breeze / Qwen3-TTS** | TTS/cloning | varies | GPU | Newer entrants in 2026 arena rankings. [L6] |
| **Demucs** (Meta) | Music/voice separation | MIT | ~1x T4 | Audio pre/post-processing, not TTS. [L5] |
| **UVR-MDX-NET** | Sound separation | open | GPU | Used in XBLocalizedVideo dubbing. [L4:internal] |

Deployment shape (external guides, corroborating internal): package model in a container exposing `POST /invocations` + `GET /ping`, deploy to a SageMaker endpoint (real-time, async, or scale-to-zero), FastAPI wrappers common for local/GPU-cloud. Break-even vs managed APIs depends on request volume (self-host wins at scale). [L6:reported]

## Internal prior art (cite wiki/builderhub URLs)

1. **Connect UTTS — Self-Hosted 3P TTS on SageMaker** (Lily Wizards team). The strongest internal reference for *productionizing* self-hosted speech gen.
   - Architecture: https://w.amazon.com/bin/view/Lily/Wizards/Projects/UTTS/Connect-Hosted-3P-TTS-Model-Architecture/
   - Threat model: https://w.amazon.com/bin/view/Lily/Wizards/Projects/UTTS/Connect-Hosted-3P-TTS-Threat-Model/
   - Key design: UTTS library (Provider Router + Self-hosted Provider Plugin + Audio Stream Manager) inside LilyIvrService; **one SageMaker real-time endpoint per cell** invoked via `InvokeEndpointWithResponseStream` (streams audio chunks back); SageMaker infra in standalone accounts; ECR model registry with cross-account image replication from 3P provider accounts; a validation/deployment pipeline (vuln scan → functional "produces valid audio" → latency/throughput benchmarks → approval gates → versioned tags → rollback). Cartesia and Rime are the first models; provider-agnostic hosting contract. Motivation: cell isolation, keep PII inside AWS (regulated industries), remove customer API-key friction, support providers with no public endpoint. [L4:internal-verified]
2. **Project Svalbard — Multi-Level Fallback System** (yashalk). Managed→self-hosted fallback matrix mapping FAL/Replicate/ElevenLabs → AWS. Audio row: Polly (neural+generative, 60+ voices, SSML) as the managed fallback; a **SageMaker self-hosted audio table** (Chatterbox 1x T4, Kokoro 1x T4, XTTS-v2 1x T4, Dia-1.6B 1x A10G, Demucs 1x T4) with instance/cost estimates; explicit recommendation to "use SageMaker Serverless or Async Inference for bursty workloads." https://w.amazon.com/bin/view/Users/yashalk/Docs/ProjectSvalbardMultiLevelFallbackSystem/ [L4:internal]
3. **XBLocalizedVideo Design** (AEE_SE_Team). Video localization/dubbing pipeline that self-hosts speech models on GPU: Step Functions → SageMaker Processing Job (ml.g6.xlarge GPU) runs 7-step dub: extract audio → voice/background separation (UVR-MDX-NET) → speaker diarization (CAMPPlus) → **TTS per sentence via CosyVoice2 voice cloning** → time-stretch → merge. Whisper (ASR) on CPU, Claude 3.7 (Bedrock) for translation. Notably chose SageMaker **Processing Jobs** over Async/ECS for unlimited runtime + $0 idle (scale-to-zero) on long videos. https://w.amazon.com/bin/view/AEE_SE_Team/XBLocalizedVideo/ [L4:internal]
4. **PSV Video Generation — Production Architecture** (Yankai). Self-managed SageMaker GPU endpoint (own serving container, own scaling, own model updates) that **scales to zero when idle** to control cost — the generative-media serving pattern speech gen slots into. https://w.amazon.com/bin/view/Yankai/PSVScaling/ [L4:internal]
5. **AGI Model Offerings (internal Nova hub)** — positions Nova Sonic as the Speech-to-Speech pillar; links prompt-engineering guide + GitHub repo; internal pricing discounts off public Bedrock rates. https://w.amazon.com/bin/view/AGIFMS_Stage/HomepageV1/ [L4:internal]
6. **ML deployment / inference-option guidance** (reusable for hosting speech models):
   - AmazonFreight ML Inference Guidelines (endpoint-type decision table, scale-to-zero, pre-warming): https://w.amazon.com/bin/view/AmazonFreight/AFTech/Pricing/DesignGuidelines/MLInference/ [L4:internal]
   - SageMaker ML Deployment (mcbmarwa): https://w.amazon.com/bin/view/Users/mcbmarwa/Quip/SageMakerMLDeployment/ [L4:internal]
   - Kotochi SageMaker hosting cohort (Inference Components scale-to-zero, MME/MCE): https://w.amazon.com/bin/view/Users/kotochi/KotochiStudy/KotochiSageMakerAISMECohortTrainingQ3/Session4HostingModelDeployment/ [L4:internal]
   - BuilderHub SageMaker (CDK) template + Model Hosting Framework: https://docs.hub.amazon.dev/docs/native-aws/developer-guide/cdk-templates-sagemaker/ and https://w.amazon.com/bin/view/AlexaShopping/MLS/ModelHostingFramework [L4:internal]
7. **APG Library pattern — config-driven batch video/image/audio generation on SageMaker + ComfyUI**: pattern that runs ComfyUI workflows (incl. audio) as SageMaker jobs, queuing one workflow per prompt via the ComfyUI REST API. https://apg-library.amazonaws.com/content/5d2698b3-50bb-477a-95c8-24dc32e12f14 [L4:established]
8. **Broadcast enablement**: "The Future of Voice Interaction: Getting Started with Amazon Nova Speech-to-Speech" https://broadcast.amazon.com/videos/1519508 ; Voice Internship Final Demos 2026 (S2S model comparison, latency) https://broadcast.amazon.com/videos/2079863 ; B&G Hero D-10 GenAI (Nova Sonic for personalized live sports commentary) https://broadcast.amazon.com/videos/1941959 [L5:reported]

## How it fits generative-media pipelines

Speech gen slots into the **same scale-to-zero GPU serving pattern** as image/video/3D models — the choice hinges on latency tolerance:

- **Latency-critical, conversational** (voice agents, IVR, live commentary): use **managed Nova Sonic (S2S)** or **Polly bidirectional streaming**, or self-hosted TTS on **SageMaker real-time endpoints** (optionally with provisioned/warm capacity). Real-time can't scale to zero (min 1 instance) but **Inference Components** can scale each packed model down to zero for FMs/LLMs. UTTS uses per-cell real-time endpoints with response streaming. [L4:established]
- **Bursty / cost-sensitive / batch** (dubbing, voiceover generation from scripts, audiobook batch): use **SageMaker Async Inference** (scale to zero via `MinInstanceCount=0` / AutoScaling `MinCapacity:0`, S3-in/S3-out, up to 1GB payload, up to 1h, cold start ~5–10 min on instance launch), **Serverless Inference** (auto scale-to-zero, but NO GPU + 6GB mem + 60s cap → only CPU-friendly models like Kokoro), or **Processing Jobs** (unlimited runtime, $0 idle — XBLocalizedVideo's choice for long dubbing). [L4:established]

Scale-to-zero mechanics (SageMaker): async endpoints scale in to zero when the queue empties and queue incoming requests until an instance spins up (autoscale on `ApproximateBacklogSizePerInstance`); real-time endpoints gained a **scale-down-to-zero** feature (Dec 2024) for intermittent gen-AI traffic; serverless scales to zero natively but is CPU-only. Cold start is the tradeoff: serverless ~1–2 min (container), async ~5–10 min (instance launch, can hit ~20 min for large HF/TGI images). Pre-warm pattern: do model load in `model_fn` before the health check passes. [L4:established]

Pipeline composition mirrors the image/video repos: presigned S3 upload → Step Functions orchestration → SageMaker GPU job/endpoint per stage (separation, diarization, TTS/clone, mux) → S3 output + DynamoDB status. Managed Bedrock (Nova Sonic/Polly, Claude for text) and self-hosted GPU models mix freely in one Step Functions graph. A managed→self-hosted **fallback ladder** (Svalbard) gives resilience: 3P API → Polly/Nova Sonic → self-hosted SageMaker.

## Sources

- [L4:established] AWS AI Service Card — Nova Sonic: https://docs.aws.amazon.com/ai/responsible-ai/nova-sonic/overview.html
- [L4:established] AWS AI Service Card — Nova 2 Sonic: https://docs.aws.amazon.com/ai/responsible-ai/nova-2-sonic/overview.html
- [L4:established] Bedrock model card — Nova Sonic: https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-amazon-nova-sonic.html
- [L4:established] Introducing Amazon Nova Sonic (blog, Apr 2025; Jul 2025 language update): https://aws.amazon.com/blogs/aws/introducing-amazon-nova-sonic-human-like-voice-conversations-for-generative-ai-applications
- [L4:established] Introducing Amazon Nova 2 Sonic (blog, GA Dec 2 2025): https://aws.amazon.com/blogs/aws/introducing-amazon-nova-2-sonic-next-generation-speech-to-speech-model-for-conversational-ai/
- [L4:established] Real-time voice agents with Stream Vision Agents + Nova 2 Sonic (ML blog): https://aws.amazon.com/blogs/machine-learning/real-time-voice-agents-with-stream-vision-agents-and-amazon-nova-2-sonic/
- [L4:established] Amazon Polly — What is text-to-speech: https://aws.amazon.com/polly/what-is-text-to-speech/
- [L4:established] Amazon Polly Bidirectional Streaming (ML blog): https://aws.amazon.com/blogs/machine-learning/introducing-amazon-polly-bidirectional-streaming-real-time-speech-synthesis-for-conversational-ai/
- [L4:established] Polly Generative TTS expansion — 10 voices, 2 regions, bidirectional streaming (What's New, Mar 2026): https://aws.amazon.com/about-aws/whats-new/2026/03/amazon-polly-expands-TTS-new-voices-and-bidirectional-streaming/
- [L4:verified] AWS AI Service Card — Amazon Polly (Feb 11 2026): https://docs.aws.amazon.com/pdfs/ai/responsible-ai/amazon-polly/amazon-polly.pdf
- [L4:established] SageMaker — Scale an endpoint to zero instances: https://docs.aws.amazon.com/sagemaker/latest/dg/endpoint-auto-scaling-zero-instances.html
- [L4:established] SageMaker — Autoscale an async endpoint (scale to zero): https://docs.aws.amazon.com/sagemaker/latest/dg/async-inference-autoscale.html
- [L4:established] SageMaker — Serverless Inference (scales to zero, CPU-only): https://docs.aws.amazon.com/sagemaker/latest/dg/serverless-endpoints.html
- [L4:established] SageMaker scale-down-to-zero feature (ML blog, Dec 2024): https://aws.amazon.com/blogs/machine-learning/unlock-cost-savings-with-the-new-scale-down-to-zero-feature-in-amazon-sagemaker-inference/
- [L4:established] SageMaker AI inference endpoints — gen-AI best practices (Prescriptive Guidance): https://docs.aws.amazon.com/prescriptive-guidance/latest/gen-ai-inference-architecture-and-best-practices-on-aws/amazon-sage-maker-ai-inference-endpoints.html
- [L4:internal-verified] Connect UTTS Model Architecture: https://w.amazon.com/bin/view/Lily/Wizards/Projects/UTTS/Connect-Hosted-3P-TTS-Model-Architecture/
- [L4:internal] Connect UTTS Threat Model: https://w.amazon.com/bin/view/Lily/Wizards/Projects/UTTS/Connect-Hosted-3P-TTS-Threat-Model/
- [L4:internal] Project Svalbard Multi-Level Fallback System: https://w.amazon.com/bin/view/Users/yashalk/Docs/ProjectSvalbardMultiLevelFallbackSystem/
- [L4:internal] XBLocalizedVideo Design (CosyVoice2 dubbing pipeline): https://w.amazon.com/bin/view/AEE_SE_Team/XBLocalizedVideo/
- [L4:internal] PSV Video Generation Production Architecture (scale-to-zero GPU endpoint): https://w.amazon.com/bin/view/Yankai/PSVScaling/
- [L4:internal] AmazonFreight ML Inference Guidelines: https://w.amazon.com/bin/view/AmazonFreight/AFTech/Pricing/DesignGuidelines/MLInference/
- [L4:internal] SageMaker ML Deployment (endpoint types): https://w.amazon.com/bin/view/Users/mcbmarwa/Quip/SageMakerMLDeployment/
- [L4:internal] Kotochi SageMaker hosting cohort (Inference Components, scale-to-zero): https://w.amazon.com/bin/view/Users/kotochi/KotochiStudy/KotochiSageMakerAISMECohortTrainingQ3/Session4HostingModelDeployment/
- [L4:internal] AGI Model Offerings (Nova hub): https://w.amazon.com/bin/view/AGIFMS_Stage/HomepageV1/
- [L4:established] APG Library — config-driven batch video/image/audio gen on SageMaker + ComfyUI: https://apg-library.amazonaws.com/content/5d2698b3-50bb-477a-95c8-24dc32e12f14
- [L4:internal] BuilderHub SageMaker (CDK) template: https://docs.hub.amazon.dev/docs/native-aws/developer-guide/cdk-templates-sagemaker/
- [L5:reported] Voice Internship Final Demos 2026 (Bedrock S2S model landscape): https://broadcast.amazon.com/videos/2079863
- [L5:reported] Getting Started with Amazon Nova Speech-to-Speech (Broadcast): https://broadcast.amazon.com/videos/1519508
- [L5:reported] B&G Hero D-10 GenAI (Nova Sonic live commentary): https://broadcast.amazon.com/videos/1941959
- [L6:reported] Spheron — Self-host XTTS-2/F5-TTS/OpenVoice V2 on GPU cloud (deployment guide, GPU sizing, FastAPI): https://www.spheron.network/blog/self-host-voice-cloning-gpu-cloud-xtts-f5-tts-openvoice-v2/
- [L6:reported] Spheron — Deploy Kokoro/Fish Speech/Hume on GPU cloud: https://www.spheron.network/blog/deploy-open-source-tts-gpu-cloud-2026/
- [L6:reported] localaimaster — Kokoro vs XTTS vs Chatterbox comparison: https://localaimaster.com/blog/kokoro-vs-xtts-vs-chatterbox
- [L6:reported] localaimaster — F5-TTS setup guide: https://localaimaster.com/blog/f5-tts-setup-guide
- [L6:reported] Chatterbox TTS self-host server (GitHub): https://github.com/malammar/Chatterbox-TTS-Server-upstream

## Open questions

- **Bedrock music/sound-effects generation?** No AWS-native general audio/music-generation model surfaced (Nova stack = speech-to-speech only; no "Nova Audio"/music model found). Confirm whether any music-gen model (e.g., via Bedrock Marketplace or a 3P) is available. [gap]
- **Polly custom/brand voice cloning:** Polly's Brand Voice (custom NTTS voice built with the Polly team) exists historically but wasn't confirmed in this pass for the Generative engine — verify current custom-voice availability and whether it's self-service or engagement-based.
- **Nova Sonic latency/telephony in a batch pipeline:** Sonic is optimized for real-time conversation; unclear if/how it's used for non-conversational TTS (narration/voiceover) vs Polly. UTTS/Svalbard use Polly + self-hosted for TTS, not Sonic — confirm the intended split.
- **Scale-to-zero for real-time voice:** conversational S2S needs warm capacity (cold start kills UX). Quantify the cost of keeping Nova Sonic / a self-hosted endpoint warm vs Inference-Component scale-to-zero for intermittent voice traffic.
- **Licensing for commercial use:** XTTS-v2 (MPL-2.0, non-commercial caveat noted externally) and several models have commercial-use restrictions — validate license terms before recommending any self-hosted model for a shipping product.
- **ComfyUI audio nodes on SageMaker:** the APG pattern mentions audio but detail is thin — confirm which audio/TTS custom nodes run under the ComfyUI-on-SageMaker pattern.
