# Serving Real-Time Interactive Video / World Models — Prior Art & Guides

Research target: the `delirium` repo serves a real-time (~14fps) video-diffusion world model on
AWS Trainium2 + NVIDIA GPU with frame streaming. This document maps the reference patterns behind
that architecture: how these models are served, how Trainium/Neuron handles video-diffusion
inference, how real-time diffusion is optimized, and the internal Amazon prior art.

Sources tagged `[L#:confidence]` per the source-authority hierarchy (L1 = observed artifact … L6 =
community). Every claim carries a citation.

---

## Summary

Real-time interactive video/world models are a distinct, fast-moving class (2024→2026) that
replaced the "slow bidirectional diffusion" paradigm with **causal, autoregressive, few-step
(often 1-step) diffusion** so that frames can be *streamed* to a user and *conditioned on live
input* (keyboard, mouse, camera, text). The delirium pattern (~14fps, Trainium2 + GPU, frame
streaming) sits squarely in this lineage. The reference stack has four layers:

1. **Model paradigm** — a bidirectional video-diffusion teacher (e.g. a Wan/DiT-style model) is
   converted into a *causal autoregressive student* that generates one latent frame (or chunk) at a
   time using a KV cache, trained with **Self Forcing** (rollout-on-own-outputs) to kill exposure
   bias/drift. [L1:established]
2. **Latency reduction** — the student is distilled to **1–4 denoising steps** via **Distribution
   Matching Distillation (DMD/DMD2)** or GAN/score-distillation, trading a small quality hit for a
   10–50× step reduction that makes real-time fps reachable. [L4:established]
3. **Serving** — frames are pushed to the client over **WebRTC** (sub-500ms glass-to-glass, the
   near-universal choice for interactive video) or WebSocket/SSE; the KV cache is managed with a
   **rolling/sliding window + attention sinks** to bound memory over unbounded-length streams.
   [L4:established]
4. **Hardware** — on Trainium the winning teams (Decart/"Descartes", Reactor) *start from
   hand-written NKI kernels / "mega-kernels"* rather than PyTorch, because real-time inference is
   memory-bandwidth-bound and needs the tensor engine kept ~100% utilized. Decart went from 2 s/frame
   → 25 fps (~20×) via kernel work, and projects ~4× better perf on Trainium3 vs H200/P200 GPUs.
   [L1:verified]

The single most relevant internal artifact is **Decart/"Descartes"** — the customer who built the
exact delirium-shaped workload (real-time video/world model, frame-by-frame, Trainium2→3, kernel-first).
Their public models **Oasis** (playable Minecraft-style world model) and **Mirage/MirageLSD/Lucy**
(live video-to-video restyle) are the closest open reference points. [L1:verified][L4:established]

---

## Streaming inference patterns

**The core shift: bidirectional → causal autoregressive.** Classic video diffusion denoises *all*
frames simultaneously with uniform noise, so it's fixed-length, slow, and can't stream or take
interactive input. Autoregressive video diffusion adds *independent* noise per frame, letting you
denoise frame 1, then 2, then 3… so you can (a) stream each frame as it finishes, (b) accept a
control input before generating the next frame, and (c) run unbounded length. This is exactly why
world models need it. [L5:established — Kiwhan Song internal talk, broadcast.amazon.com/videos/1687738]

**KV-cache is the mechanism that makes AR video diffusion real-time.** Bidirectional models re-run
full transformer inference over many steps *without* KV caching; AR models cache the keys/values of
past frames so each new frame only attends to cached context — the same trick that made LLM decoding
fast. [L5:established — same internal talk]

**Self Forcing (train-test alignment).** The dominant training recipe: during training, condition
each frame on *previously self-generated* outputs by performing autoregressive rollout with KV
caching, instead of on ground-truth context. This closes the train/test gap (exposure bias) that
otherwise causes error accumulation and drift, and enables real-time streaming with sub-second
latency on a single GPU. [L4:established — Self Forcing, arxiv.org/abs/2506.08009]

**Rolling / sliding-window KV cache + attention sinks (long-horizon memory).** For unbounded
streams the KV cache must be bounded, so it's a *rolling* window that forgets distant frames.
Patterns:
- **Rolling Forcing** — non-overlapping windows, mitigates exposure bias on self-generated history;
  multi-minute real-time video on a single GPU. [L4:established — arxiv.org/abs/2509.25161]
- **StreamingLLM-style attention sinks** applied to video, but naive application degrades fidelity
  and causes motion stagnation — so "Deep Sink" / participative compression variants exist.
  [L4:reported — arxiv.org/html/2512.05081]
- **Compressed historical latent tokens in the KV cache** encoding relative actions + absolute
  camera poses, for implicit 3D-consistent retrieval and long-term coherence with minimal overhead
  (RELIC, 14B, 16fps). [L4:reported — arxiv.org/abs/2512.04040]
- **Reconstituted Context Memory / temporal reframing** to keep geometrically-important long-past
  frames accessible against memory attenuation (WorldPlay, 720p 24fps). [L4:reported — arxiv.org/html/2512.14614]
- **Cache sharing** — precompute the KV of conditional frames once in a prior AR step and reuse it
  every subsequent step, eliminating redundant compute (causal generation). [L4:reported — arxiv.org/html/2411.16375]

**Chunked vs per-frame + pyramid/interleaved sampling.** Frames can be emitted one at a time or in
small chunks; "pyramid sampling" partially denoises frame N while starting frame N+1, an interleaved
AR schedule that's faster than naive sequential AR. [L5:established — Kiwhan Song internal talk]

**Transport (frame streaming to the client):**
- **WebRTC is the default** for interactive generative video — built for low-latency A/V over UDP,
  prioritizes latency over guaranteed delivery, targets the sub-500ms budget natural interaction
  needs. Decart streams camera/video input in and modified frames out over browser WebRTC at
  sub-500ms. [L4:established — getstream.io, gmicloud.ai]
- **SSE / HTTP2 / gRPC streaming** are used for token/text incremental output; **WebRTC for
  audio+video** is the recommended split. [L4:established — technolynx.com]
- Realistic latency: independent glass-to-glass WebRTC tests land ~0.6–1.3s CDN-delivered; treat
  advertised sub-500ms as best-case. A ~14fps target ⇒ ~71ms/frame compute budget, well inside the
  WebRTC transport envelope, so the bottleneck is model compute, not transport. [L6:reported — forasoft.com]
- Open frameworks: `realtime-ai` (WebRTC, GStreamer-style modular pipeline), Livepeer live-video-to-video
  (ComfyStream/Cascade), jetson-inference WebRTC server. [L6:reported — github/realtime-ai, docs.livepeer.org]

---

## Trainium / Neuron for video-gen (cite URLs)

**NKI (Neuron Kernel Interface) is the low-level lever.** NKI is a Pythonic, tile-based kernel
language exposing the Trainium ISA (tensor/vector/scalar/GPSIMD engines); you write NKI kernels
"when you need to beat the compiler." Neuron ships an open-source high-performance kernel library
(attention, RoPE, MLP) you can drop into models.
- NKI docs: https://awsdocs-neuron.readthedocs-hosted.com/en/latest/nki/index.html [L4:verified]
- NxD Inference (the inference runtime + parallelism): https://awsdocs-neuron.readthedocs-hosted.com/en/latest/libraries/nxd-inference/index.html [L4:verified]
- NKI tutorials incl. Introduction to NKI Kernel Optimization, Trainium2/Trainium3 architecture
  guides for NKI, Fused Mamba, and "Insert NKI Kernels into Models" (mixing custom kernels with
  compiled PyTorch). [L4:verified — same NKI index]

**Neuron core physical model (why kernels matter for real-time).** Each Trainium3 chip has 4 HBM
banks (~500 GB/s each) feeding 8 neuron cores; on-core acceleration is ~10 TB/s (~20× HBM). Data
flows HBM → DMA → State Buffer (SBUF) → tensor engine (systolic array, matmul) → PSUM → back. The
performance-engineering goal is to **keep the tensor engine ~100% utilized** and **minimize DMA
reads** by loading the largest tiles possible and pipelining. A first-pass compiler trace of VJEPA-2
showed only ~27% MFU with many DMA gaps — the target of hand kernels. [L1:verified — internal talk
transcript, broadcast.amazon.com/videos/1904847]

**PyTorch-native / eager on Neuron (2026).** Neuron SDK added a private-beta PyTorch-native path
(eager execution + `torch.compile`) where you largely just change `.to("cuda")` → `.to("neuron")`
and add a compile step; VJEPA-2 off Hugging Face ran on Trainium with mostly device-string changes.
GA/eager-mode was slated ~Q1 2026 ("Neuron 2.24" referenced for image-gen inference GA). [L1:verified
— broadcast.amazon.com/videos/1904847; L5:reported — broadcast.amazon.com/videos/1786251]

**Parallelism for long-sequence DiT/video (the ~40k+ sequence problem).** Video DiTs blow up
sequence length (image DiT ~4096 → video ~40k, "10×" scaling was called out as the next Neuron
target). Relevant parallelism primitives:
- **Context parallelism** partitions activations along the *sequence* dimension — the right axis for
  long video sequences, since attention cost grows quadratically in sequence length; more impactful
  than tensor parallelism (which splits the hidden dim). SMP v2 exposes `context_parallel_degree`
  with `p2p` (async, overlaps compute) or `all_gather` implementations.
  https://docs.aws.amazon.com/sagemaker/latest/dg/model-parallel-core-features-v2-context-parallelism.html [L4:verified]
- NxD Inference exposes **Tensor Parallelism (TP), Data Parallelism (DP), Decode Context Parallelism
  (DCP), Expert Parallelism (EP), Vision Encoder Parallelism**, plus multimodal features (Vision
  Attention, On-Device Encoder Cache, M-RoPE, Block Packing) — the building blocks for a video/vision
  transformer served on Trn. https://awsdocs-neuron.readthedocs-hosted.com/en/latest/libraries/nxd-inference/index.html [L4:verified]

**Diffusion transformers on Trn/Inf today.** Internal TFC session "AIM123: Diffusion Transformers on
Trainium and Inferentia" demos FLUX image-gen on Inferentia, discusses diffusion-step caching
(TeaCache/"mi cache") and the coming push to video-diffusion + AR image gen; committed image-gen
inference GA in a Neuron release. broadcast.amazon.com/videos/1519787 [L5:established]

**Hardware limits / knobs to know:** Trainium3 GA'd 2025-12-02; Trn3 UltraServers up to 144 chips,
~362 FP8 PFLOPs, 4.4× compute / 4× mem-bandwidth vs Trn2; ~5× interactivity and ~6× throughput vs
Trn2 for LLM serving; up to 6× improvement in all-reduce/all-gather latency (matters for
model-sharded video DiT). https://w.amazon.com/bin/view/Neighorn/Test/Messaging/Amazon-Silicon/
[L4:established]. Getting-started + "how to assess a model" for Trn: broadcast.amazon.com/videos/1901489 [L5:reported].

---

## Real-time diffusion optimization

The latency equation for interactive video is roughly `time/frame = (denoising steps) ×
(transformer forward cost) / (parallelism × kernel efficiency)`. Every real-time system attacks all
three factors.

**1. Cut the number of denoising steps (biggest lever).**
- **Distribution Matching Distillation (DMD/DMD2)** distills a many-step teacher (e.g. 50-step) into
  a few-step (4-step) or 1-step generator without one-to-one trajectory matching. **CausVid** applies
  DMD to video: bidirectional→AR + 50-step→4-step, giving ~1.3s initial latency then ~9.4fps
  streaming. https://arxiv.org/html/2412.07772 [L4:established]
- **1-step (1NFE) AR generation** is achievable: "Autoregressive Adversarial Post-Training" generates
  one latent frame per single neural function evaluation and streams in real time.
  https://arxiv.org/html/2506.09350v1 [L4:reported]
- DMD degrades under very low NFE budgets (layout instability, oversaturation, broken motion) —
  hence variants: **Rewarded DMD / Reward Forcing** (23.1fps on one H100), **Copula-aware DMD**,
  **Transition Matching Distillation** (speed/quality trade-off knob), few-step DMD via subinterval
  score matching. arxiv.org/html/2512.04678, /2606.21982, /2601.09881, /2510.27684 [L4:reported]

**2. Combine distillation with Self Forcing** so the few-step student is also causal and drift-robust
— this pairing (Self Forcing + DMD) is the recurring production recipe (e.g. streaming video
stylization distills a bidirectional teacher into a few-step AR model via Self Forcing + DMD).
https://arxiv.org/abs/2604.13509 [L4:established]

**3. Reduce per-step transformer cost.**
- **Diffusion-step caching** (TeaCache / "mi cache") reuses transformer features across adjacent
  denoising steps. [L5:established — AIM123 talk, broadcast.amazon.com/videos/1519787]
- **Cache sharing** of conditional-frame KV across AR steps. [L4:reported — arxiv.org/html/2411.16375]
- **Adaptive compute** — spend fewer denoising passes on easy chunks, more on hard ones
  ("what to remember, when to skip"). [L4:reported — arxiv.org/html/2607.18436]

**4. fps vs quality vs memory is an explicit trilemma.** Long-horizon memory mechanisms degrade
real-time fps; the three goals (real-time streaming, spatial memory, precise control) are usually
solved in isolation, and unifying them is the open frontier (RELIC, WorldPlay, Matrix-Game 3.0).
Published operating points for calibration: CausVid ~9.4fps; RELIC 16fps@14B; Matrix-Game 2.0 25fps;
OmniForcing 25fps; Reward Forcing 23.1fps@H100; WorldPlay 720p@24fps; Matrix-Game 3.0 up to 40fps@720p@5B;
MaineCoon 47.5fps@22B single GPU; GameNGen 20fps on one TPU; Decart Mirage ~24fps @ ≤40ms.
[L4:established / L4:reported — arxiv links above; L6:reported — aisharenet for Mirage 40ms figure]

**Delirium's ~14fps** sits at the low end of this band, consistent with a larger model, a higher
resolution, or running within a bounded step count on Trn2 hardware — i.e. a reasonable
production operating point, not an outlier.

---

## Internal prior art (cite URLs)

**Decart / "Descartes" — the direct analog to delirium (highest-value reference).**
- Adam Stanley (FMP SA) + Emily Weber (Annapurna Labs) — "Neuron: World models on AWS Trainium with
  PyTorch Native and NKI Kernels": Decart builds real-time video/world models on Trainium; started
  at **2 s/frame**, reached **25 fps** for the re:Invent 2025 sprint (~20×) by writing hand-tuned
  **mega-kernels** (bypassing the compiler), starting from hardware fundamentals not PyTorch. Same
  talk walks the Trn3 neuron-core datapath and runs VJEPA-2 on Neuron. Peter DeSantis's re:Invent
  keynote demo (live restyle of him into "Werner Vogels" style, frame-by-frame on Trainium3) is
  Decart. https://broadcast.amazon.com/videos/1904847 [L1:verified]
- "Getting started with Trainium / how to assess a model": Decart named alongside Anthropic/OpenAI;
  Decart leverages Trn3 HBM + on-chip SRAM + high memory-compute bandwidth for "stream and broadcast
  interactive experiences," projecting **~4× better perf on Trainium3 vs P200/H200 GPUs**, heavy hand
  kernel customization supported by Annapurna. https://broadcast.amazon.com/videos/1901489 [L1:verified]
- re:Cap Trn3: Decart = "4× faster inference for real-time generative video at half the cost of GPUs";
  Torch-native support + new kernel-interface iteration + expanded profiler are the Trn3 software
  headlines; >50% of Bedrock inference now on Trainium. https://broadcast.amazon.com/videos/1786251 [L5:established]
- Silicon messaging wiki (verbatim): "Decart is achieving 4x faster inference for real-time
  generative video at half the cost of GPUs." https://w.amazon.com/bin/view/Neighorn/Test/Messaging/Amazon-Silicon/ [L4:established]
- Decart public models (external, closest open references to delirium): **Oasis** (DiT + ViT
  autoencoder, action-conditioned AR frame gen, playable Minecraft-style, open 500M weights w/
  Etched — openreview.net/pdf?id=ocMWhGLHqu, github.com/spikedoanz/realtime-oasis); **Mirage /
  MirageLSD / Lucy** (causal AR video-to-video live restyle, ≤40ms latency, 24fps, unbounded length,
  WebRTC) — cookbook.decart.ai, aisharenet.com/en/miragelsd, techzine.eu (LSD v2 causal AR).
  [L4:established / L6:reported]

**Reactor (Bryce Schmidtchen, CTO; co-founder ex-Luma AI) — "Developer Platform for World Models."**
One of the few teams granted **Trainium3 early access**; already ported world models to Trn2; demoed
first world model on Trn3 (Sept, AI Infra Summit, Santa Clara). Key engineering claims: real-time
inference is *fundamentally different from batch* — needs "capillary compute distribution across
regions, **GPU time-slicing** (serving 3 users streaming video from 1 GPU), and kernel-level
optimization"; runs managed real-time inference for robotics/avatar/video customers; can host
arbitrary models via API. https://broadcast.amazon.com/videos/2026575 [L5:established]

**Kiwhan Song — Video World Models for Robotics (Weekly Research Reading Group, 2025-09-04).** Best
internal technical primer on the *paradigm*: bidirectional (fixed-length, slow, no KV cache) vs AR
(variable-length, real-time, KV-cached, easier to distill to few-step). Introduces **Diffusion
Forcing Transformer** — independent per-frame noise levels enabling arbitrary AR sampling schedules
(incl. pyramid/interleaved), and discusses error-accumulation mitigation. Directly explains the
delirium-style inference loop. https://broadcast.amazon.com/videos/1687738 [L5:established]

**AIM123: Diffusion Transformers on Trainium and Inferentia (TFC).** FLUX image-gen on Inf, diffusion
step caching, roadmap to video-diffusion + AR image gen, image-gen inference GA commitment.
https://broadcast.amazon.com/videos/1519787 [L5:established]

**Internal enablement to pursue:** the Annapurna **NKI kernel-writing boot camp** (3-day, Cupertino,
internal) — the sanctioned path to learn the mega-kernel technique delirium/Decart rely on.
[L1:verified — broadcast.amazon.com/videos/1904847]

---

## Sources (URLs + [L#:confidence])

Internal (Amazon):
- https://broadcast.amazon.com/videos/1904847 — Neuron: World Models on Trainium, PyTorch Native + NKI (Decart 2s→25fps, mega-kernels, neuron-core datapath, VJEPA-2) [L1:verified]
- https://broadcast.amazon.com/videos/1901489 — Getting started with Trainium; Decart Trn3 ~4× vs GPU, stream/broadcast interactive [L1:verified]
- https://broadcast.amazon.com/videos/1786251 — re:Cap Trn3 (Torch-native, kernel interface, profiler; Decart 4× / half cost) [L5:established]
- https://broadcast.amazon.com/videos/2026575 — Reactor world-model platform (Trn3 early access, GPU time-slicing, real-time ≠ batch) [L5:established]
- https://broadcast.amazon.com/videos/1687738 — Kiwhan Song, Video World Models for Robotics (Diffusion Forcing, AR vs bidirectional, KV cache) [L5:established]
- https://broadcast.amazon.com/videos/1519787 — AIM123 Diffusion Transformers on Trn/Inf (FLUX, step caching) [L5:established]
- https://w.amazon.com/bin/view/Neighorn/Test/Messaging/Amazon-Silicon/ — Amazon Silicon messaging (Trn3 specs, Decart 4× claim) [L4:established]
- https://awsdocs-neuron.readthedocs-hosted.com/en/latest/nki/index.html — NKI docs (kernel lib, tutorials, arch guides) [L4:verified]
- https://awsdocs-neuron.readthedocs-hosted.com/en/latest/libraries/nxd-inference/index.html — NxD Inference (TP/DP/DCP/EP, vision/multimodal) [L4:verified]
- https://docs.aws.amazon.com/sagemaker/latest/dg/model-parallel-core-features-v2-context-parallelism.html — Context parallelism (seq-dim sharding, p2p/all_gather) [L4:verified]

External — model paradigm / streaming inference:
- https://arxiv.org/abs/2506.08009 — Self Forcing (AR video diffusion, KV cache, exposure bias) [L4:established]
- https://arxiv.org/abs/2509.25161 — Rolling Forcing (rolling window, multi-minute real-time) [L4:established]
- https://arxiv.org/html/2411.16375 — Efficient AR video diffusion, causal gen + cache sharing [L4:reported]
- https://arxiv.org/abs/2512.04040 — RELIC (KV-cache long-horizon memory, 14B, 16fps) [L4:reported]
- https://arxiv.org/html/2512.14614 — WorldPlay (Reconstituted Context Memory, 720p 24fps) [L4:reported]
- https://arxiv.org/html/2512.05081 — Deep Sink / participative compression (attention sinks for video) [L4:reported]
- https://arxiv.org/html/2603.11647 — OmniForcing (rolling KV-cache, 25fps audio-visual) [L4:reported]
- https://arxiv.org/html/2508.13009 — Matrix-Game 2.0 (open real-time streaming world model, 25fps) [L4:reported]
- https://arxiv.org/html/2604.08995 — Matrix-Game 3.0 (40fps@720p 5B) [L4:reported]

External — distillation / latency:
- https://arxiv.org/html/2412.07772 — CausVid (bidirectional→AR, DMD 50→4 step, ~9.4fps) [L4:established]
- https://arxiv.org/html/2506.09350v1 — AR Adversarial Post-Training (1NFE per frame, real-time) [L4:reported]
- https://arxiv.org/html/2512.04678 — Reward Forcing / Rewarded DMD (23.1fps H100) [L4:reported]
- https://arxiv.org/html/2601.09881 — Transition Matching Distillation (speed/quality knob) [L4:reported]
- https://arxiv.org/abs/2604.13509 — Streaming video stylization (Self Forcing + DMD, AR DiT) [L4:established]

External — game/world-model foundations:
- https://arxiv.org/html/2408.14837 — GameNGen (diffusion = real-time game engine, DOOM, 20fps/TPU) [L4:established]
- https://openreview.net/pdf?id=ocMWhGLHqu — Oasis (Decart/Etched; ViT autoencoder + DiT backbone) [L4:established]
- https://github.com/spikedoanz/realtime-oasis — Oasis inference code (action-conditional AR) [L6:reported]
- https://arxiv.org/html/2605.30263 — minWM (open full-stack framework: bidirectional T2V → few-step AR world model) [L4:reported]

External — serving/transport:
- https://www.gmicloud.ai/en/blog/decart-real-time-video-webrtc — Decart WebRTC, sub-500ms live video-to-video [L4:reported]
- https://getstream.io/blog/webrtc-ai-voice-video/ — WebRTC for real-time AI A/V (UDP, sub-500ms) [L4:established]
- https://www.technolynx.com/post/real-time-streaming-for-generative-ai-applications — SSE/gRPC/WebRTC split [L4:established]
- https://www.forasoft.com/blog/article/whip-whep-replace-rtmp-live-streaming-2026 — real WebRTC glass-to-glass 0.6–1.3s [L6:reported]
- https://docs.livepeer.org/network/guides/orchestrator-realtime-ai — Livepeer live-video-to-video (ComfyStream) [L6:reported]

---

## Open questions

1. **What does delirium's model actually distill from / to?** Is it a Self-Forcing + DMD student of a
   Wan/DiT teacher (the dominant recipe), an Oasis-style action-conditioned DiT, or a JEPA-family
   model? ~14fps + "world model" + Trn2/GPU strongly implies causal-AR-DiT few-step, but confirm
   against the repo's model card / training code.
2. **Trn2 vs GPU parity in delirium** — is the same model served on both (dual-backend abstraction),
   or is one a reference/fallback? What's the fps delta Trn2↔GPU, and does it use hand-written NKI
   kernels like Decart, or the PyTorch-native/eager Neuron path (beta)?
3. **KV-cache/memory policy** — which long-horizon scheme (rolling window, attention sinks, compressed
   pose-encoded tokens)? This determines drift behavior and max session length.
4. **Frame transport in delirium** — WebRTC vs WebSocket vs SSE, and where the VAE decode + encode
   happens (on-accelerator vs host) relative to the ~71ms/frame budget.
5. **Internal Decart engagement docs** — the broadcast talks are public-ish; is there a deeper
   internal runbook / NKI kernel repo / Bedrock-hosting design for the Decart or Reactor world-model
   workload that delirium could reuse? (Search Quip/wiki with names "Decart", "Reactor", "Oasis",
   "world model serving", "NKI mega-kernel".)
6. **Context parallelism on Neuron for video DiT** — SMP context-parallelism docs are GPU/SageMaker;
   what's the *Neuron* equivalent for the 40k-sequence video-DiT case (DCP is decode-focused)? Confirm
   the supported path for long-sequence video attention on Trn.
