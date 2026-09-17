# Speech Generation in Generative-Media Pipelines — Deep Research (lesson support)

_Research date: 2026-09-17. Second pass — goes deeper on the five lesson-shaped gaps left open by `tts-speech-generation.md`. Corrects two license errors from the first pass (XTTS-v2, F5-TTS) and adds a new internal async-pattern reference (Brilliance Voice Labs / Ryu)._

## Summary

Speech generation is a **family of distinct tasks**, not one thing — and the AWS decision is a two-axis choice: **task** (what you're generating) × **serving pattern** (how latency-tolerant the workload is). The clean split a learner needs:

1. **Task taxonomy.** TTS (text→speech), STT/ASR (speech→text, *not* generation — the inverse), S2S (speech→speech, one model), voice cloning (TTS conditioned on a reference clip), dubbing (a *pipeline* — ASR + translate + clone + time-align + mux, not a single model), and music/SFX (a separate model class). Each maps to a specific AWS-managed service or open model.
2. **AWS-native managed.** **Amazon Polly** owns batch/streaming TTS (generative voice engine + a new bidirectional-streaming API, Mar 2026). **Amazon Nova 2 Sonic** (GA Dec 2 2025) owns real-time conversational S2S on Bedrock. There is **no native Bedrock music/SFX model** — that gap is filled by self-host or Bedrock Marketplace (MusicGen, Stable Audio).
3. **Self-host open models.** For voice cloning, per-request-cost avoidance, or data-residency, teams self-host on SageMaker GPU. **License is the gating decision, not quality:** only **Chatterbox (MIT)**, **Kokoro (Apache-2.0)**, and **CosyVoice2 (Apache-2.0)** are commercial-safe; **XTTS-v2 (CPML, non-commercial, vendor defunct)**, **F5-TTS (CC-BY-NC)**, and **Fish Speech (CC-BY-NC-SA)** are commercial dead ends.
4. **Serving-pattern fit** is the crux. Dubbing/voiceover/audiobook batch = **large payload, long job, bursty** → the **SageMaker Asynchronous Inference** sweet spot (S3-pointer in/out, ≤1 GB payload, ≤1 hr/request, scale-to-zero, SNS notify). Real-time conversational voice = the opposite → a **warm streaming endpoint** (Nova Sonic managed, or a self-hosted real-time endpoint that can't fully scale to zero without cold-start UX damage). For *unbounded* jobs (long videos) even Async's 1-hr cap is too small → **Processing Jobs**.
5. **Internal prior art is deep and recent.** Connect **UTTS** (per-cell real-time streaming endpoints), **Brilliance Voice Labs / Ryu** (audiobook narrator voice-clone fixes on **SageMaker Async + SNS fan-in** — the textbook async example), **XBLocalizedVideo** (GPU dubbing, chose Processing Jobs over Async for unlimited runtime), and **Project Svalbard** (managed→self-host fallback matrix). All four are citable.

## Taxonomy (task → tool matrix)

| Task | Input → Output | What it is | AWS-managed | Open / self-host | Notes |
|------|----------------|-----------|-------------|------------------|-------|
| **TTS** (text-to-speech) | text → audio | Synthesize a voice reading text | **Amazon Polly** (standard / neural / long-form / **generative** engines) | Kokoro, Chatterbox, CosyVoice2, XTTS-v2, F5-TTS, Dia | The default "narration/voiceover" primitive. [L4:established] |
| **STT / ASR** (speech-to-text) | audio → text | Transcription — the **inverse** of generation | **Amazon Transcribe** (diarization, 100+ langs) | Whisper (OpenAI), FunASR, SenseVoice | Not generation; belongs in a pipeline (dubbing needs it). Transcribe > model-native transcription for speaker diarization. [L5:reported] |
| **S2S** (speech-to-speech) | audio (+text) → audio (+text) | One model that hears and speaks — conversational | **Amazon Nova 2 Sonic** (Bedrock) | Moshi, GLM-Voice (rare in prod) | Nova Sonic was the *only* S2S model on Bedrock as of 2026. Real-time; needs a warm/streaming path. [L4:established] |
| **Voice cloning** | text + reference clip → audio in that voice | TTS conditioned on a target speaker | Polly **Brand Voice** (engagement-based, not self-service) | Chatterbox, XTTS-v2, F5-TTS, CosyVoice2, OpenVoice V2 | Zero-shot clone from 5–15 s of reference audio. License matters most here. [L6:reported] |
| **Dubbing** | video → same video, new language, voice preserved | A **pipeline**, not a model: ASR → translate → clone-TTS → time-align → mux | Composed: Transcribe + Bedrock (Claude) + Polly/self-host | UVR (separation) + CAMPPlus (diarize) + CosyVoice2 (clone) + Whisper (ASR) | XBLocalizedVideo's exact 7-step recipe. Large/long/bursty → batch pattern. [L4:internal] |
| **Music generation** | text → music | Text-to-music | **None native** on Bedrock | MusicGen (Meta), Stable Audio (Stability) | Via **Bedrock Marketplace** or SageMaker self-host. [L4:established] |
| **SFX / general audio** | text → sound | Text-to-sound-effect | **None native** | Stable Audio, AudioGen | Same gap as music. [L5:reported] |
| **Audio pre/post** | audio → stems / clean audio | Source separation (voice/background) | None native | Demucs (Meta, MIT), UVR-MDX-NET | Pipeline glue for dubbing. [L4:internal] |

**The one distinction learners get wrong:** STT/ASR is *transcription*, the inverse of TTS — it belongs in the "understanding" half of a pipeline, not the "generation" half. And **dubbing is a pipeline, not a model** — the single biggest conceptual unlock.

## AWS-native (Polly + Nova Sonic, managed-vs-self-host decision)

### Amazon Polly — managed TTS
- **Engines:** standard, neural, **long-form**, and **generative** (most expressive/human-like). [L4:established]
- **Two APIs with very different limits** [L4:verified — Polly docs]:
  - `SynthesizeSpeech` (real-time, sync): **6,000 characters total, ≤3,000 billable** per request. Console "Listen/Download" greys out above 3,000. Use for short/interactive.
  - `StartSpeechSynthesisTask` (**async, long-form**): **200,000 characters total, ≤100,000 billable**; writes the audio to **S3**. This is Polly's *own* batch pattern — the managed analog of "put a big job in, get an S3 file out." Use for audiobooks/long voiceover.
  - `StartSpeechSynthesisStream` (**bidirectional streaming**, Mar 2026): real-time synthesis over **HTTP/2**, send text incrementally / receive audio incrementally → low time-to-first-audio for voice agents. Supports all engines and speech marks. [L4:established]
- **Default quota:** 80 TPS for `SynthesizeSpeech` (standard voices), per region per account (raisable). [L4:verified]
- **Controls:** SSML (phrasing/emphasis/pauses), custom lexicons (acronyms/brand names), speech-duration adjustment for multilingual dubbing. [L4:established]
- **Brand Voice** (custom cloned NTTS voice) exists but is **engagement-based with the Polly team**, not self-service — the reason internal teams needing self-service cloning go to self-hosted models instead. [L5:inferred]
- Governed by an AWS AI Service Card (Polly), current Feb 11 2026. [L4:verified]

### Amazon Nova 2 Sonic — managed real-time S2S (Bedrock)
- **What it is:** proprietary FM that unifies speech understanding + generation in ONE model; preserves acoustic context (adapts to *how* something was said, not just *what*). GA **Dec 2 2025**. Model ID `amazon.nova-2-sonic-v1:0`. [L4:established]
- **Languages (7):** English, French, Italian, German, Spanish + **Portuguese, Hindi** (added in v2). **Polyglot voices** — one voice (e.g. Tiffany) switches languages mid-conversation (code-switching). [L4:established]
- **Conversational features:** natural turn-taking with **configurable VAD sensitivity** (high/medium/low), **barge-in** (interruption handling), **asynchronous tool calling** (keeps responding while tools run in background), **crossmodal** (switch text↔voice mid-session), improved ASR on alphanumerics, short utterances, and **8 kHz telephony** audio + noisy/accented speech. [L4:established]
- **Telephony/platform integrations (built-in):** Amazon Connect, Vonage, Twilio, Audiocodes, LiveKit, Pipecat — handle codec optimization, session lifecycle, bidirectional event handling. [L4:established]
- **API:** same **bidirectional streaming API** as v1 (drop-in model-ID swap to upgrade). [L4:established]
- **Regions (GA):** US East (N. Virginia), US West (Oregon), Asia Pacific (Tokyo). (Stockholm was rolled back 12/12/25.) [L4:established]
- **Pricing:** ~**$3 / M speech-input tokens, $12 / M speech-output tokens** (~$0.003/$0.012 per 1K), ≈$0.015/min estimated — reported ~80% cheaper than OpenAI GPT-4o Realtime. Internal Bedrock rates discount off public. [L5:reported / L4:internal for the discount]
- Governed by its own AI Service Card (Dec 2025). [L4:established]

### Managed vs self-host decision (the lesson's core AWS judgment)

| Choose **managed** (Polly / Nova Sonic) when… | Choose **self-host** (SageMaker) when… |
|---|---|
| You want zero infra + instant scale | You need a **specific open voice/clone model** Polly/Sonic don't offer |
| Conversational S2S in a supported language → **Nova Sonic** | You need **self-service voice cloning** (Polly Brand Voice is engagement-based) |
| Standard narration/voiceover → **Polly** (generative engine) | **Per-request API cost** dominates at your volume (self-host = compute-only, wins at scale) |
| You lack GPU/MLOps capacity | **Data residency**: text/audio must never leave your account (regulated industries) — the UTTS motivation |
| Latency-critical and you want it handled | A provider distributes **only** as a container/SageMaker model (no public API) — UTTS problem #4 |

**Fallback ladder (Svalbard):** 3P API → Polly / Nova Sonic (managed AWS) → self-hosted SageMaker. Gives resilience + a graceful degrade path. [L4:internal]

## Self-hosted open models (sizes / GPU / license)

**License is the gating decision.** Corrected from the first pass — two models were mislabeled. Commercial-safety verdicts below are from multiple 2026 sources.

| Model | Task | Params / size | GPU fit | Latency / RTF | License | **Commercial-safe?** |
|-------|------|---------------|---------|---------------|---------|----------------------|
| **Kokoro-82M** | TTS (no cloning) | 82M, ~2–3 GB | Runs on **CPU** or 1× T4; many per GPU | ~96× real-time (RTF ~0.03 on A100) | **Apache-2.0** | ✅ **Yes** |
| **Chatterbox** (Resemble AI) | TTS + voice cloning | ~0.5B class | 1× T4 (16 GB); "heavier to run" than Kokoro | near real-time | **MIT** | ✅ **Yes** — matches ElevenLabs (63.75% pref, internal) |
| **CosyVoice2-0.5B** (Alibaba/FunAudioLLM) | TTS + zero-shot cloning + streaming | 0.5B | 1× GPU (used on ml.g6.xlarge internally) | **~150 ms** bi-streaming | **Apache-2.0** | ✅ **Yes** — the internal workhorse (XBLocalizedVideo, BVL/Ryu) |
| **XTTS-v2** (Coqui) | TTS + voice cloning | ~0.5B | 1× T4 | 6-s clone, 17 langs | **CPML** (non-commercial) — **Coqui defunct Jan 2024, no license to buy** | ❌ **No** (was mislabeled MPL-2.0 in pass 1) |
| **F5-TTS** (SWivid/Shanghai AI Lab) | TTS + zero-shot cloning | DiT + ConvNeXt-V2 | 1× GPU (fits RTX 3060 12 GB) | clones from 5–15 s ref | **CC-BY-NC** (non-commercial) | ❌ **No** (was "open" in pass 1) |
| **Dia-1.6B** (Nari Labs) | Multi-speaker dialogue TTS | 1.6B | 1× A10G (24 GB) | — | open (verify) | ⚠️ verify |
| **Fish Speech** | TTS + cloning | — | 1× GPU | — | **CC-BY-NC-SA** | ❌ **No** |
| **Piper** | lightweight TTS | tiny | CPU / Raspberry Pi | fast | **MIT** | ✅ **Yes** |
| **Demucs** (Meta) | source separation (pipeline glue) | — | 1× T4 | — | **MIT** | ✅ **Yes** |
| **UVR-MDX-NET** | source separation | — | 1× GPU | — | open | ⚠️ verify |

**GPU cheat-sheet (Svalbard cost table):** `ml.g4dn.xlarge` (1× T4 16 GB) → Kokoro, Chatterbox, Demucs. `ml.g5.xlarge`/`g5.2xlarge` (1× A10G 24 GB) → Dia-1.6B. `ml.g6.xlarge` (1× L4) → CosyVoice2 dubbing (internal). Music/large models need A100 (`ml.p4d`). [L4:internal]

**The ship-it rule for a lesson:** if the product is commercial, your realistic open choices are **Kokoro** (narration, no cloning), **Chatterbox** (cloning, MIT), or **CosyVoice2** (cloning + streaming, Apache-2.0). The best-*sounding* cloners (XTTS-v2, F5-TTS, Fish Speech) are all non-commercial — a classic "don't pick on quality alone" trap.

**Music/SFX self-host:** MusicGen (Meta) and Stable Audio (Stability, trained on licensed data) on SageMaker GPU or via **Bedrock Marketplace** ("AI Music Generation Server" listing) — since Bedrock has no first-party music model. [L4:established]

## Speech on SageMaker Async vs real-time (the serving-pattern fit)

This is the lesson's spine: **the task's latency profile picks the serving pattern.**

### SageMaker Asynchronous Inference — the dubbing/voiceover sweet spot
From the async-inference doc (verified) — Async **queues** requests and processes them off a queue: [L4:verified]
- **Large payloads:** up to **1 GB** (an audio/video file, not a JSON blob).
- **Long processing:** up to **1 hour** per request.
- **S3-pointer I/O:** you put the payload in **S3** and pass a pointer in `InvokeEndpointAsync`; SageMaker returns an identifier + output S3 location immediately, then writes the result to S3 when done.
- **SNS notify:** optionally get success/error notifications via **Amazon SNS** (`SuccessTopic`/`ErrorTopic`) — no polling.
- **Scale to zero:** autoscale instance count to **0** when the queue is empty (autoscale on `ApproximateBacklogSizePerInstance`); **you pay only while processing**. Requests queue until an instance spins up.
- **Cold-start tradeoff:** ~5–10 min on instance launch (up to ~20 min for large HF/TGI images) — acceptable for batch, fatal for conversation.
- **Exclusions:** some endpoint features are incompatible with Async (check the Exclusions page before designing).

**Why it fits speech-gen batch:** dubbing a video, generating a chapter of an audiobook, or rendering voiceover from a script = one large input, minutes of GPU work, arriving in bursts. S3-in/S3-out + scale-to-zero + SNS is exactly this shape. **The `Polly StartSpeechSynthesisTask` API is the managed mirror of this pattern** (big text in, S3 audio out) — a nice teaching parallel: Async is "roll your own long-form TTS job," Polly's async task is "the managed one."

### Real-time / streaming — the conversational path
- Conversational S2S (Nova Sonic) and low-latency voice agents need **warm capacity** and a **persistent stream** (HTTP/2 or WebSocket). Cold start kills the UX.
- Self-hosted real-time endpoints **can't fully scale to zero** without a cold-start penalty. Two mitigations: (1) **Inference Components** scale-down-to-zero (Dec 2024) for intermittent FM/LLM traffic; (2) keep ≥1 warm instance (cost). UTTS runs **one real-time endpoint per cell**, invoked with `InvokeEndpointWithResponseStream` to stream audio chunks back. [L4:established / L4:internal]

### Serving-pattern decision table

| Workload | Latency need | Pattern | Why |
|----------|--------------|---------|-----|
| Conversational voice agent, IVR, live commentary | real-time | **Nova Sonic** (managed) or self-host **real-time + streaming** | warm, persistent stream; can't tolerate cold start |
| Short narration snippets, interactive TTS | low, sync | **Polly `SynthesizeSpeech`** or self-host real-time | ≤3–6k chars, instant |
| Audiobook / long voiceover from script | batch, tolerant | **Polly `StartSpeechSynthesisTask`** or **SageMaker Async** | ≤200k chars / big payload → S3 out |
| Dubbing a short/medium video | batch, bursty | **SageMaker Async** (S3-in/out, SNS, scale-to-zero) | large payload, <1 hr, cost-sensitive |
| Dubbing a **long** video (>1 hr work) | batch, unbounded | **SageMaker Processing Jobs** | Async's 1-hr cap + payload limits break; Processing = unlimited runtime, $0 idle (XBLocalizedVideo's choice) |
| CPU-only tiny TTS (Kokoro) | batch | **SageMaker Serverless** | native scale-to-zero, but **no GPU**, 6 GB, 60 s cap → CPU models only |

**Cold-start ladder (from XBLocalizedVideo's own eval):** Processing ~5–10 min (→~2 min with warm pools); Async ~8–20 min; ECS ~3–5 min. Idle cost: Processing $0, Async $0 (or $271–813/mo kept warm), ECS $0 (or $576/mo warm). [L4:internal]

## Internal prior art (cite URLs)

1. **Brilliance Voice Labs (BVL) / Ryu — audiobook narrator voice-clone on SageMaker ASYNC** _(NEW this pass — the textbook async example)_. Brilliance Publishing's `BPubRyu*` package family. **Ryu** = a manuscript-correction pipeline; **BVL** = the voice-synthesis engine that clones the *narrator's* voice to regenerate small audio fixes without a re-record session (live in beta). Architecture is **event-driven, NO Step Functions**: Harmony UI → API Gateway → Lambda → **SageMaker ASYNC endpoints** (`cosyvoice-endpoint` for voice fixes, `whisper-endpoint` for transcription; an F5-TTS/`ryu-endpoint` is deployed but not in active use) → async writes output to S3 + publishes to **SNS** (`ryu-sagemaker-completion`) → **RyuNotifyLambda** (SNS consumer) does per-take status + a **DynamoDB atomic counter** for fan-in (first completion flips job COMPLETE). Deterministic `InferenceId = <jobId>:<take>`; idempotency keyed on the S3 output key (SNS is at-least-once). Browser ↔ S3 directly via presigned PUT/GET. Models: **CosyVoice2-0.5B** (voice clone) + **Whisper** (transcription), both on async endpoints. This is the async-serving pattern for speech, in production. https://w.amazon.com/bin/view/Brilliance_Publishing/Information_Technology/Development/Runbooks/BVL/ [L4:internal-verified]

2. **Connect UTTS — self-hosted 3P TTS on SageMaker (real-time streaming per cell)** (Lily Wizards). The strongest reference for productionizing self-hosted conversational TTS. Provider-agnostic hosting contract; **Cartesia Sonic 3** first, Rime second — onboarding a provider = config only (TtsProvider enum + TtsProviderConfig image/health-timeout + per-cell CellEndpointConfig), no code. **One SageMaker real-time endpoint per cell**, invoked via `InvokeEndpointWithResponseStream` (streams audio chunks). CDK stack owns Model/EndpointConfig/Endpoint + per-variant target-tracking autoscaling + IAM exec role + CloudWatch alarms (latency/5XX/GPU/concurrency); IVR Service CDK owns the `InvokeEndpoint*` permissions. Four self-host motivations (the managed-vs-self-host lesson in one list): **cell isolation, PII-stays-in-AWS (regulated industries), remove customer API-key friction, support providers with no public endpoint.** Provider config = constant across cells; cell config = per-cell (instance types, concurrency ceilings, variant weights).
   - Architecture: https://w.amazon.com/bin/view/Lily/Wizards/Projects/UTTS/Connect-Hosted-3P-TTS-Model-Architecture/
   - SageMaker Model Deployment LLD (CDK constructs): https://w.amazon.com/bin/view/Lily/Wizards/Projects/UTTS/SageMaker-Model-Deployment-Infrastructure-LLD/
   - Unified TTS LLD (Provider Router / Plugin / streaming): https://w.amazon.com/bin/view/Lily/Wizards/Projects/UTTS/Unified-TTS-LLD/ (also https://w.amazon.com/bin/view/Ramin/UTTS/)
   - Threat model (data-stays-in-AWS, cell isolation, supply-chain, least-priv): https://w.amazon.com/bin/view/Lily/Wizards/Projects/UTTS/Connect-Hosted-3P-TTS-Threat-Model/ [L4:internal-verified]

3. **XBLocalizedVideo — GPU dubbing pipeline (chose Processing Jobs over Async)** (AEE_SE_Team). API GW → Lambda (FastAPI) → **Step Functions** → **SageMaker Processing Job** → Bedrock. 4 phases: upload (presigned S3) → understand (Whisper ASR on CPU `ml.c5a.xlarge`, or PaddleOCR on GPU) → translate (Claude 3.7 Sonnet, Bedrock, glossary-aware) → **dub** (GPU `ml.g6.xlarge`, 7 steps: extract audio → UVR-MDX-NET separation → CAMPPlus diarization → **CosyVoice2 per-sentence voice clone** → time-stretch → merge audio → mux to video). **Explicit compute alternatives eval** — chose Processing Jobs because Async has a **1-hr hard cap** and would need chunking + parallel orchestration for long videos; Processing = unlimited runtime, native long-video, $0 idle. Storage: S3 + DynamoDB (scale-to-zero, $0 idle). https://w.amazon.com/bin/view/AEE_SE_Team/XBLocalizedVideo/ [L4:internal-verified]

4. **Project Svalbard — Multi-Level Fallback System** (yashalk). Managed→self-host fallback matrix mapping FAL/Replicate/ElevenLabs → AWS. Audio managed fallback = Polly (neural+generative, 60+ voices, SSML). **Self-hosted SageMaker audio table:** Chatterbox (MIT, 1× T4), Kokoro (Apache-2.0, 1× T4), XTTS-v2 (page says MPL-2.0 — external sources say CPML/non-commercial; treat as non-commercial, 1× T4), Dia-1.6B (1× A10G), Demucs (MIT, 1× T4). GPU cost table + explicit "use SageMaker Serverless or Async for bursty workloads." https://w.amazon.com/bin/view/Users/yashalk/Docs/ProjectSvalbardMultiLevelFallbackSystem/ [L4:internal]

5. **PSV Video Generation — scale-to-zero GPU endpoint** (Yankai). Self-managed SageMaker GPU endpoint (own serving container/scaling/updates) that **scales to zero when idle** — the generative-media serving pattern speech gen slots into. https://w.amazon.com/bin/view/Yankai/PSVScaling/ [L4:internal]

6. **AGI Model Offerings (internal Nova hub)** — positions Nova Sonic as the S2S pillar alongside Canvas (image)/Reel (video); prompt-engineering guide + repo links; internal Bedrock pricing discounts. https://w.amazon.com/bin/view/AGIFMS_Stage/HomepageV1/ [L4:internal]

7. **Reusable hosting guidance:** AmazonFreight ML Inference Guidelines (endpoint-type decision table, scale-to-zero, pre-warming) https://w.amazon.com/bin/view/AmazonFreight/AFTech/Pricing/DesignGuidelines/MLInference/ ; Kotochi SageMaker hosting cohort (Inference Components scale-to-zero, MME/MCE) https://w.amazon.com/bin/view/Users/kotochi/KotochiStudy/KotochiSageMakerAISMECohortTrainingQ3/Session4HostingModelDeployment/ ; BuilderHub SageMaker CDK template https://docs.hub.amazon.dev/docs/native-aws/developer-guide/cdk-templates-sagemaker/ [L4:internal]

8. **APG Library — config-driven batch video/image/audio gen on SageMaker + ComfyUI** (runs ComfyUI workflows incl. audio as SageMaker jobs, one workflow per prompt via ComfyUI REST). https://apg-library.amazonaws.com/content/5d2698b3-50bb-477a-95c8-24dc32e12f14 [L4:established]

9. **Broadcast enablement (video):** "Getting Started with Amazon Nova Speech-to-Speech" https://broadcast.amazon.com/videos/1519508 ; Voice Internship Final Demos 2026 (Bedrock S2S landscape, latency) https://broadcast.amazon.com/videos/2079863 ; B&G Hero D-10 (Nova Sonic live sports commentary) https://broadcast.amazon.com/videos/1941959 [L5:reported]

## Lesson framing (what a learner should be able to do after)

After this lesson, a learner should be able to:

1. **Name the task correctly.** Given a requirement ("make the app talk", "let users converse", "translate this video keeping the voice", "add background music"), classify it as TTS / S2S / voice-clone / dubbing-pipeline / music-gen — and recognize that **STT is the inverse (understanding), and dubbing is a pipeline, not a model.**
2. **Make the managed-vs-self-host call** with a real rubric: reach for **Polly** (narration/voiceover, generative engine) or **Nova 2 Sonic** (real-time conversation) first; go self-host only for a specific open model, self-service cloning, per-request-cost avoidance at scale, or data residency (the four UTTS motivations).
3. **Pick a commercial-safe open model.** Know that **license gates the choice before quality does**: Kokoro / Chatterbox / CosyVoice2 = shippable; XTTS-v2 / F5-TTS / Fish Speech = non-commercial only. Not pick the best-sounding cloner and get blocked at launch.
4. **Map the workload to a SageMaker serving pattern.** Batch dubbing/voiceover → **Async** (S3-pointer, ≤1 GB, ≤1 hr, SNS, scale-to-zero); long video → **Processing Jobs** (unlimited runtime); CPU-tiny TTS → **Serverless**; conversation → **warm real-time/streaming** (Nova Sonic or per-cell endpoint). Explain *why* real-time can't just scale to zero (cold start).
5. **Sketch the pipeline.** Presigned S3 upload → orchestration (Step Functions or event-driven Lambda + SNS fan-in) → SageMaker job/endpoint per stage → S3 output + DynamoDB status — and know a real Amazon example for each shape (BVL/Ryu = async+SNS, XBLocalizedVideo = Step Functions+Processing, UTTS = per-cell real-time streaming).
6. **Recognize the music/SFX gap:** no native Bedrock model; use Bedrock Marketplace (MusicGen) or self-host (Stable Audio / MusicGen).

Suggested lesson artifact: a **decision-tree diagram** (task → managed?/self-host? → serving pattern) plus a **one-model-per-task table** the learner can apply to their own project.

## Sources

**AWS-native (managed):**
- [L4:established] Amazon Polly — SynthesizeSpeech vs StartSpeechSynthesisStream compared (6,000/3,000-char limit, all engines, HTTP/2): https://docs.aws.amazon.com/polly/latest/dg/bidirectional-streaming-choosing.html
- [L4:verified] Polly limits — SynthesizeSpeech 6,000/3,000; StartSpeechSynthesisTask 200,000/100,000; 80 TPS default: https://docs.aws.amazon.com/polly/latest/dg/limits.html and https://docs.aws.amazon.com/sdk-for-python/v1/reference/clients/polly/errors/TextLengthExceededException/
- [L4:established] Polly bidirectional streaming (ML blog, Mar 2026): https://aws.amazon.com/blogs/machine-learning/introducing-amazon-polly-bidirectional-streaming-real-time-speech-synthesis-for-conversational-ai
- [L4:established] Polly generative TTS expansion — 10 voices, 2 regions, bidirectional streaming (What's New, Mar 2026): https://aws.amazon.com/about-aws/whats-new/2026/03/amazon-polly-expands-TTS-new-voices-and-bidirectional-streaming/
- [L4:established] Polly long audio files (async console, 3,000-char sync cap): https://docs.aws.amazon.com/polly/latest/dg/longer-console.html
- [L4:verified] AWS AI Service Card — Amazon Polly (Feb 11 2026): https://docs.aws.amazon.com/pdfs/ai/responsible-ai/amazon-polly/amazon-polly.pdf
- [L4:established] Introducing Amazon Nova 2 Sonic (blog, GA Dec 2 2025) — 7 langs, polyglot, async tools, VAD, crossmodal, telephony, 3 regions, model ID: https://aws.amazon.com/blogs/aws/introducing-amazon-nova-2-sonic-next-generation-speech-to-speech-model-for-conversational-ai/
- [L4:established] Bedrock model card — Nova 2 Sonic: https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-amazon-nova-2-sonic.html
- [L4:established] Nova Sonic user guide (S2S usage): https://docs.aws.amazon.com/nova/latest/userguide/speech.html
- [L4:established] Introducing Amazon Nova Sonic (blog, Apr 2025): https://aws.amazon.com/blogs/aws/introducing-amazon-nova-sonic-human-like-voice-conversations-for-generative-ai-applications
- [L4:established] Real-time voice agents with Stream Vision Agents + Nova 2 Sonic (ML blog): https://aws.amazon.com/blogs/machine-learning/real-time-voice-agents-with-stream-vision-agents-and-amazon-nova-2-sonic/
- [L4:established] AI Service Card — Nova Sonic: https://docs.aws.amazon.com/ai/responsible-ai/nova-sonic/overview.html
- [L5:reported] Nova 2 Sonic pricing ($3/M in, $12/M out, ~$0.015/min, ~80% cheaper than GPT-4o Realtime): https://rywalker.com/research/aws-nova-2-sonic

**SageMaker serving patterns:**
- [L4:verified] SageMaker Asynchronous Inference (1 GB payload, 1 hr, S3-pointer, SNS, scale-to-zero): https://docs.aws.amazon.com/sagemaker/latest/dg/async-inference.html
- [L4:established] Async endpoint autoscale to zero: https://docs.aws.amazon.com/sagemaker/latest/dg/async-inference-autoscale.html
- [L4:established] Async check prediction results (SNS SuccessTopic/ErrorTopic): https://docs.aws.amazon.com/sagemaker/latest/dg/async-inference-check-predictions.html
- [L4:established] Scale an endpoint to zero instances: https://docs.aws.amazon.com/sagemaker/latest/dg/endpoint-auto-scaling-zero-instances.html
- [L4:established] Serverless Inference (scale-to-zero, CPU-only): https://docs.aws.amazon.com/sagemaker/latest/dg/serverless-endpoints.html
- [L4:established] Scale-down-to-zero feature (ML blog, Dec 2024): https://aws.amazon.com/blogs/machine-learning/unlock-cost-savings-with-the-new-scale-down-to-zero-feature-in-amazon-sagemaker-inference/
- [L4:established] Gen-AI inference best practices (Prescriptive Guidance): https://docs.aws.amazon.com/prescriptive-guidance/latest/gen-ai-inference-architecture-and-best-practices-on-aws/amazon-sage-maker-ai-inference-endpoints.html

**Open models + licenses:**
- [L6:established] XTTS-v2 CPML non-commercial, Coqui defunct: https://localaimaster.com/blog/xtts-coqui-commercial-license
- [L6:established] License matrix — Chatterbox MIT / Kokoro Apache / XTTS CPML / F5 CC-BY-NC / Fish CC-BY-NC-SA: https://www.forasoft.com/blog/article/voice-cloning-synthesis and https://d-central.tech/local-voice-ai-models/
- [L6:reported] Kokoro vs XTTS vs Chatterbox: https://localaimaster.com/blog/kokoro-vs-xtts-vs-chatterbox
- [L4:established] CosyVoice2/3 Apache-2.0, 0.5B, 150 ms bi-streaming, 9 langs: https://github.com/FunAudioLLM/CosyVoice and issue confirming Apache-2.0: https://github.com/QwenAudio/CosyVoice/issues/1945
- [L6:reported] CosyVoice 2 paper (streaming, human-parity): https://arxiv.org/pdf/2412.10117
- [L6:reported] F5-TTS (flow-matching DiT, ConvNeXt-V2): https://github.com/SWivid/F5-TTS
- [L6:reported] Chatterbox (Resemble AI, MIT): https://github.com/resemble-ai/chatterbox
- [L6:reported] Spheron self-host guides (XTTS/F5/OpenVoice; Kokoro/Fish): https://www.spheron.network/blog/self-host-voice-cloning-gpu-cloud-xtts-f5-tts-openvoice-v2/ , https://www.spheron.network/blog/deploy-open-source-tts-gpu-cloud-2026/

**Music/SFX:**
- [L4:established] Bedrock Marketplace "AI Music Generation Server" (MusicGen self-host): https://aws.amazon.com/marketplace/pp/prodview-xcizbxbx6hvoy
- [L5:reported] Stable Audio 3.0 (Stability, licensed-data, open-weight): https://stability.ai/stable-audio
- [L5:reported] MusicGen (Meta): https://audiocraft.metademolab.com/musicgen.html
- [L4:established] Bedrock Marketplace: https://aws.amazon.com/bedrock/marketplace/

**Internal prior art:**
- [L4:internal-verified] Brilliance Voice Labs / Ryu (SageMaker Async + SNS fan-in, CosyVoice2 + Whisper): https://w.amazon.com/bin/view/Brilliance_Publishing/Information_Technology/Development/Runbooks/BVL/
- [L4:internal-verified] Connect UTTS Model Architecture: https://w.amazon.com/bin/view/Lily/Wizards/Projects/UTTS/Connect-Hosted-3P-TTS-Model-Architecture/
- [L4:internal-verified] UTTS SageMaker Model Deployment LLD: https://w.amazon.com/bin/view/Lily/Wizards/Projects/UTTS/SageMaker-Model-Deployment-Infrastructure-LLD/
- [L4:internal] UTTS Unified TTS LLD: https://w.amazon.com/bin/view/Lily/Wizards/Projects/UTTS/Unified-TTS-LLD/
- [L4:internal] UTTS Threat Model: https://w.amazon.com/bin/view/Lily/Wizards/Projects/UTTS/Connect-Hosted-3P-TTS-Threat-Model/
- [L4:internal-verified] XBLocalizedVideo Design (Processing Jobs vs Async eval, CosyVoice2 dubbing): https://w.amazon.com/bin/view/AEE_SE_Team/XBLocalizedVideo/
- [L4:internal] Project Svalbard Multi-Level Fallback System: https://w.amazon.com/bin/view/Users/yashalk/Docs/ProjectSvalbardMultiLevelFallbackSystem/
- [L4:internal] PSV Video Generation scale-to-zero GPU endpoint: https://w.amazon.com/bin/view/Yankai/PSVScaling/
- [L4:internal] AGI Model Offerings (Nova hub): https://w.amazon.com/bin/view/AGIFMS_Stage/HomepageV1/
- [L4:internal] AmazonFreight ML Inference Guidelines: https://w.amazon.com/bin/view/AmazonFreight/AFTech/Pricing/DesignGuidelines/MLInference/
- [L4:internal] Kotochi SageMaker hosting cohort: https://w.amazon.com/bin/view/Users/kotochi/KotochiStudy/KotochiSageMakerAISMECohortTrainingQ3/Session4HostingModelDeployment/
- [L4:established] APG Library ComfyUI-on-SageMaker batch pattern: https://apg-library.amazonaws.com/content/5d2698b3-50bb-477a-95c8-24dc32e12f14
- [L4:internal] BuilderHub SageMaker CDK template: https://docs.hub.amazon.dev/docs/native-aws/developer-guide/cdk-templates-sagemaker/
- [L5:reported] Broadcast: Nova S2S getting started https://broadcast.amazon.com/videos/1519508 ; Voice Internship demos https://broadcast.amazon.com/videos/2079863 ; B&G Hero D-10 https://broadcast.amazon.com/videos/1941959

## Open questions

- **Polly Brand Voice for the generative engine:** confirmed engagement-based (not self-service), but whether the *generative* engine supports custom brand voices (vs only neural) is unconfirmed — verify before recommending Polly for a custom-voice product.
- **Nova Sonic for non-conversational TTS:** Sonic is real-time-conversation-optimized; internal TTS pipelines (UTTS, Svalbard, BVL) use Polly + self-host, NOT Sonic, for narration/voiceover. The intended split is confirmed by usage but not by an explicit AWS statement — treat "use Polly not Sonic for narration" as inferred-from-practice.
- **Dia-1.6B and UVR-MDX-NET licenses:** listed "open" but not verified to a specific commercial-safe license — verify before recommending for a shipping product.
- **Async cold-start for GPU speech models:** the 5–20 min range is doc/internal-eval general; the *specific* cold start for a CosyVoice2/Chatterbox container on `ml.g6.xlarge` isn't measured here. A spike would pin it.
- **ComfyUI audio nodes on SageMaker:** the APG pattern mentions audio but which TTS/music custom nodes actually run under it is still thin.
- **Nova 2 Omni:** announced in preview (Dec 2025) — may add audio-out modalities beyond Sonic; not researched here.
