# World Models — Briefing Guide & Study Guide

Synthesized 2026-09-15 from two repos: `world-models` (the benchmark/eval research project) and
`delirium-world-models-poc` (the browser-playable generator PoC). Every claim traces to those
repos' own docs; file paths are cited in the source findings at
`.scratch/research/world-models.md` and `.scratch/research/delirium-world-models-poc.md`.

---

## PART 1 — BRIEFING GUIDE

### What a "world model" is (the definition these projects use)

A **world model** is an AI system that learns to *simulate an interactive environment* —
predicting the next visual state given the current state and an action — instead of rendering
from a hand-coded game engine. It models spatial and physical dynamics, not text. The key word
is **interactive**: you feed it actions (WASD, buttons, camera) and it produces the world's
next frames (`world-models/.memory/CONTEXT.md`).

Contrast with a normal video generator: a text-to-video model produces a fixed clip. A world
model must stay *steerable and consistent over time* as a player drives it.

### Why it matters right now (the two open problems)

The two repos attack the two halves of the same problem:

1. **Can we generate a steerable world in real time?** (delirium) — Yes, at ~14 fps on AWS
   Trainium2, by forking a research video-diffusion model and adding an action pathway.
2. **Can we tell whether a world model is actually good?** (world-models) — This is the *named
   gap*: there are no accepted eval metrics that separate "looks real" from "plays correctly."
   The project's answer is a new metric, the **Fidelity Divergence Score (FDS)**.

The central insight tying them together is **"vivid dream"** (Roblox's framing): today's
interactive video models can look photoreal while lacking interactivity, challenge, and
persistence. A model can win visual-quality metrics (like FVD) while failing to follow the
player's actions — the **ranking reversal**. A benchmark has to catch that
(`world-models/docs/games-wmlbench-proposal.md`).

### The landscape (six architectures, three deployability tiers)

The `world-models` synthesis groups the field six ways
(`world-models/.memory/world-models-synthesis.md`):

| # | Family | How it works | Examples |
|---|--------|--------------|----------|
| 1 | Video-latent | Autoregressive/diffusion frame prediction, action-conditioned | Genie, Cosmos, Oasis, Odyssey, Runway |
| 2 | 3D-native | Generates meshes / Gaussian splats | Roblox Cube, World Labs, Tencent HY-World |
| 3 | Hybrid engine + model | Model augments a real engine | Roblox Reality |
| 4 | Latent-dynamics RL | Learns dynamics in latent space for control | Dreamer v3, DIAMOND, TD-MPC2 |
| 5 | JEPA (joint-embedding predictive) | Non-generative; predicts representations | Meta V-JEPA 2 |
| 6 | Action foundation models | Large action-conditioned models | General Intuition |

**AWS-deployability tiers:** self-hostable today (Cosmos 3, Roblox Cube, Tencent HY-World 2.0),
walled (Genie 3), API-only (Runway GWM-1, Decart Oasis, World Labs, Odyssey).

### The benchmark's key idea: the engine is the oracle

Robotics world-model eval is hard because "ground truth" is a physical camera you can't
rewind. **Games don't have that problem.** A game engine, re-run from the identical seed frame
with the identical action sequence, produces deterministic, bit-reproducible ground truth. So
you can compare the model's rollout against the engine's rollout *frame by frame*, and pixel
error becomes a *valid behavioral signal* — but only under bit-exact determinism, which is why
proving determinism (Spike 0) is the highest-risk dependency
(`world-models/docs/games-wmlbench-proposal.md`).

### FDS: how you score a world model (four axes)

The FDS harness (`world-models/tools/fds_harness.py`) measures four things:

1. **Visual fidelity** (PSNR/LPIPS) — *reported but NOT trusted* for behavior. This is the axis
   that lies.
2. **Behavioral** (trusted) — does the world follow the actions? Measured by **IDM round-trip**:
   re-infer the actions from the *generated* frames using an Inverse Dynamics Model, compare to
   the actions you fed in. Behavioral FDS = `1 - action_F1`.
3. **Drift over horizon** — the per-step error curve, and `h*` = the last step before drift
   exceeds tolerance.
4. **Action-sensitivity guard** — rollouts under *different* actions must actually diverge. This
   catches an action-agnostic model that "wins" by replaying a plausible-looking future.

### The generator side (delirium): what a real deployment looks like

Delirium is a fork of **TencentARC Rolling Forcing**, a real-time video-diffusion world model,
adapted to run on AWS and wrapped in a playable game (`delirium-world-models-poc/WORLD_MODELS.md`):

- **The model:** a causal video **DiT** (Diffusion Transformer) built on **Wan2.1-T2V-1.3B**
  (dim 2048, 32 layers, 16 latent channels, bf16), trained with **rectified flow / flow
  matching**.
- **Real-time trick (Rolling Forcing):** denoise a *rolling window* of frames together so
  blocks mutually refine and drift is suppressed; an **Attention Sink** (anchor block) preserves
  global context over thousands of frames; a streaming KV cache evicts the middle.
- **Few-step speed (DMD distillation):** Distribution Matching Distillation trains a fast
  5-step student against a frozen 14B teacher + a critic — *data-free*. Shipped as a T=5
  checkpoint; a T=4 runbook exists to push past 16 fps.
- **Action steering:** RF is text-only by design, so plain DMD ignores any added action input
  (measured 0.000 effect). Delirium grafts small **action modules** (button embedding + axes
  MLP) onto the DiT's cross-attention behind a **zero-init gate** (start as a no-op, learn to
  un-gate), and gives them a real gradient with a supervised next-frame flow-matching term on
  real (latent, action) pairs from the **CrossFPS** dataset. A LoRA-on-attention variant was
  *counterproductive* (degraded to "a grainy blob") and is disabled.
- **Measured performance:** ~14 fps at 480x640, 5 denoise steps, on Trainium2 with TP4xCP4 = 16
  NeuronCores (`delirium-world-models-poc/VERIFIED_14FPS_BASELINE.md`). It is
  **bandwidth/launch-bound, not FLOP-bound** (~4-6% MFU) - the only optimizations that moved fps
  were kernel-launch reductions, not precision changes.
- **Honest limits:** no true persistence — each clip subtly re-rolls the world; WASD steers, it
  doesn't move a rigid camera.

### How the two projects connect

delirium is the **generator** (it *makes* a steerable world). world-models is the **evaluator**
(it *scores* one). The current in-flight work in `world-models` (ticket 15) trains its own tiny
(~4.2M-param) action adapter on a frozen 1.3B base using delirium's recipe, then measures
controllability with the FDS harness — closing the loop between generate and measure.

---

## PART 2 — STUDY GUIDE

### Core concepts to master

1. **World model vs. video generator** — the difference is *action-conditioned, over-time
   steerability*, not image quality.
2. **The vivid-dream problem / ranking reversal** — why visual metrics alone are misleading, and
   why a behavioral axis is mandatory.
3. **Engine-as-oracle** — why games enable rigorous eval (deterministic ground truth) where
   robotics can't, and why bit-exact determinism is the load-bearing assumption.
4. **FDS four axes** — visual (untrusted), behavioral/IDM-round-trip (trusted), drift/`h*`,
   action-sensitivity guard.
5. **Causal video DiT + rectified flow** — the modern generator backbone (Wan2.1, DiT, flow
   matching).
6. **Rolling Forcing + Attention Sink + streaming KV cache** — how you get *real-time* autoregressive
   long-video without drift.
7. **DMD distillation** — data-free few-step distillation; convergence tracked by the gradient
   norm (`dmdnorm`), not the loss value.
8. **Action conditioning via gated modules** — why you graft a zero-init-gated pathway + a
   supervised term, and why LoRA-on-attention failed here.
9. **Accelerator economics** — RF is bandwidth/launch-bound; the fps win came from CP-query
   parallelism and launch-count reduction, not FLOPs.

### Self-test (explain-to-a-colleague format)

- A teammate says "our world model scored great on LPIPS, ship it." Explain why that's not
  enough and what you'd measure instead. *(Answer path: ranking reversal -> behavioral axis ->
  IDM round-trip -> action-sensitivity guard.)*
- Why can games benchmark world models more rigorously than robotics can? What single property
  makes it work, and what breaks if that property fails? *(Engine-as-oracle -> determinism ->
  pixel error becomes a valid behavioral signal only if bit-exact.)*
- A colleague added an action input to a DMD-distilled video model and it had zero effect. Why,
  and what's the fix? *(DMD is action-invariant/data-free -> need a supervised action term on real
  (latent,action) pairs + a gated module so it isn't ignored.)*
- Someone proposes shortening a T=5 distilled model's step list to T=4 for speed. Why won't that
  just work? *(A DMD student only predicts accurate x0 at the noise levels it was distilled on -
  you must re-distill, per the T4 runbook.)*
- Why is a world model that scores 0.000 behavioral F1 on *real* frames probably a bug, not a
  result? *(IDM needs >=128 frames; 32-frame clips give F1~0 even on real data; a hard 0.000 is
  usually a degenerate/driver/OOD condition - the gpu_health_guard exists for this.)*

### Glossary

- **World model** — AI that simulates an interactive, physics-aware environment, predicting
  future states from actions.
- **FDS (Fidelity Divergence Score)** — 0.0-1.0 divergence of a synthetic stream from a reality
  reference; 0.0 = perfect, default 0.2 retrain threshold.
- **Reality stream / engine oracle** — the deterministic engine re-running identical inputs;
  the ground truth a model is scored against.
- **Behavioral axis** — the trusted FDS component: action-following via IDM round-trip.
- **IDM (Inverse Dynamics Model)** — infers the action taken between two frames; used to
  re-infer actions from generated frames.
- **h\*** — maximum admissible horizon before drift exceeds tolerance.
- **Ranking reversal** — a model wins visual metrics while losing action-following.
- **Rolling Forcing (RF)** — TencentARC's rolling-window autoregressive video diffusion for
  real-time, low-drift streaming.
- **Attention Sink / anchor block** — a retained first KV block anchoring global context over
  long generations.
- **DiT (Diffusion Transformer)** — the transformer backbone that denoises video latents (here,
  Wan2.1-based).
- **Rectified flow / flow matching** — the training objective: predict a straight-line flow from
  noise to data.
- **DMD (Distribution Matching Distillation)** — data-free few-step distillation via
  `(fake_score - real_score)` from a frozen teacher + critic; tracked by `dmdnorm`.
- **Denoising step list / T** — the noise timesteps the student denoises through; fewer = faster
  (T=5 shipped, T=4 pushes fps).
- **Latent / VAE** — compressed representation the DiT operates on; VAE decodes latents -> pixels.
- **TP / SP / CP** — tensor / sequence / context parallelism; reference topology TP4xCP4 = 16
  ranks.
- **NKI (Neuron Kernel Interface)** — Amazon's low-level kernel language for Trainium.
- **MFU (Model FLOPs Utilization)** — RF sits at ~4-6% (launch/bandwidth-bound).
- **Trainium2 / trn2** — AWS training accelerator (Capacity-Block only, no on-demand SKU).
- **Matrix-Game 3.0 (MG3)** — Wan2.2-5B world model with native action control, 4xH100 FSDP,
  ~17 fps per-clip.
- **CrossFPS** — real (latent, action) gameplay dataset (Call-of-Duty) used for the supervised
  action term. Note: its real parquet schema uses raw gamepad columns, contradicting the dataset
  card — verify bytes, not docs.

### Source map (where to read deeper)

**world-models (the evaluator):**
- `docs/games-wmlbench-proposal.md` — the two-phase benchmark proposal, hypothesis, five FDS
  dimensions, risks. *Start here.*
- `docs/games-wmlbench-initial-test.md` — runnable methodology + dataset survey + data-shape spec.
- `tools/fds_harness.py` — the FDS metric implementation (the four axes + JSON contract).
- `tools/README.md` — spike-runner map + output-interpretation gotchas (the >=128-frame rule).
- `.memory/world-models-synthesis.md` — the six-way taxonomy + deployability tiers.
- `.memory/CONTEXT.md` — authoritative glossary.

**delirium-world-models-poc (the generator):**
- `WORLD_MODELS.md` — global architecture + current state. *Start here.*
- `VERIFIED_14FPS_BASELINE.md` — the measured performance recipe.
- `models/dit_model.py` / `models/dit_pipeline.py` — the DiT + rolling-window inference.
- `gpu/action_causal_model.py` — the grafted action modules + KV-sink logic.
- `training/model/action_dmd.py` / `training/model/dmd.py` — the action objective + DMD core.
- `docs/ROOFLINE_RF_1_3B.md` — the bandwidth-knee / MFU analysis.
- `docs/DISTILL_T4_RUNBOOK.md` — re-distilling to T=4.

---

## PART 3 — PRIOR ART & GAP-FILLING RESEARCH (2026-09-16)

Added from internal + web research to situate the repos' work in the wider field. Full
findings with per-claim `[L#:confidence]` source tags: `.scratch/research/gaps/world-model-eval-prior-art.md`
and `.scratch/research/gaps/realtime-worldmodel-serving.md`.

### FDS is not novel in kind — it's the repo's instantiation of an established family

The **IDM round-trip** (generate video from actions -> recover actions via an Inverse Dynamics
Model -> score agreement) is well-established prior art, not a new invention. Lineage:
Ha & Schmidhuber (2018) -> OpenAI **VPT** (2022, Minecraft; IDM keypress acc 90.6%, R^2 0.97) ->
DeepMind **Genie** latent-action model (2024) -> **MineWorld** (2025) -> Microsoft **RLIR**
(arXiv:2509.23958, Sep 2025) — the closest cousin, which uses IDM-recovered action-F1 as a
verifiable RL reward. RLIR's §6.1 is a strong external argument for FDS's core bet: **pixel-level
rewards are reward-hackable** (a model can "win" by darkening frames), so scoring in *action
space* is the right call.

**How to frame FDS in the study guide:** the repo's instantiation of the IDM-round-trip family,
*complementary to* (not a replacement for) visual metrics.

### The established metric stack (what FDS sits alongside)

- **FVD** (Fréchet Video Distance, Unterthiner 2018) — the field standard for video-gen quality,
  using I3D features. Its successor **CD-FVD** (CVPR 2024) shows plain FVD over-weights per-frame
  quality vs motion because I3D is content-biased; the fix is unsupervised VideoMAE features.
- **PSNR / SSIM / LPIPS** — reference-based per-frame supplements (exactly the "reported but not
  trusted" visual axis in the FDS harness).
- These measure *look*; FDS's behavioral axis measures *play*. Both are needed.

### Named benchmarks worth knowing

**VBench** / **VBench-2.0** (adds Controllability, Physics, Commonsense dimensions),
**WorldModelBench** (NeurIPS 2025 — instruction-following + physics-adherence, ships a 2B judger
model), **WorldBench** (physics-concept isolation), **RoboWM-Bench** (execution-grounded),
plus the **VPT/MineWorld** Minecraft action-following protocol. If the FDS proposal needs external
validation or a comparison baseline, these are the reference points.

### Internal Amazon prior art — a negative result worth stating

No proprietary Amazon world-model eval metric and no internal "FDS" predecessor were found
(searched ALL/WIKI/SAGE_HORDE). The internal footprint is *awareness only* (arxiv-scan digests,
a video-gen metric catalogue in a CreativeAgent page, the Model Quality Builders Guide). Practical
implication: FDS has no internal artifact to reconcile against — it's greenfield internally. (A
targeted `code.amazon.com`/Quip search would be needed to claim this *definitively*.)

### Real-time world-model serving — Decart is the internal delirium analog

The delirium serving pattern (real-time video/world model on Trainium, frame-by-frame) has a
direct internal precedent: **Decart** — an AWS customer running exactly this workload. Internal
broadcast talks report they went ~2s/frame -> 25 fps (~20x) via **hand-written NKI "mega-kernels"**
(bypassing the compiler), and powered a re:Invent 2025 keynote live-restyle demo on Trainium3.
Their public models **Oasis** (action-conditioned DiT world model, open 500M weights) and
**Mirage/Lucy** (causal-AR live video-to-video, <=40 ms, 24 fps, WebRTC) are the closest open
references. **Reactor** is a second internal Trn3 world-model platform.

**The reference serving stack (4 layers):**
1. **Paradigm** — a bidirectional teacher distilled to a **causal autoregressive student** that
   generates one latent frame/chunk at a time with a KV cache, trained via **Self Forcing**
   (roll out on its own outputs) to kill drift. This is exactly delirium's Rolling Forcing lineage.
2. **Latency** — distill to **1-4 denoising steps** via DMD/DMD2/CausVid (CausVid: 50-step -> 4-step,
   ~9.4 fps). delirium's T=5 -> T=4 runbook is the same lever.
3. **Serving** — **WebRTC** is the default for interactive video (sub-500 ms); WebSocket/SSE are
   the alternatives (delirium uses SSE). Rolling/sliding-window KV cache + attention sinks bound
   memory over unbounded streams.
4. **Hardware** — Neuron **NKI** kernels are the performance lever (keep the tensor engine near
   100% utilized, minimize DMA); **context parallelism** (sequence-dim sharding) is the right
   axis for long video-DiT sequences. Matches delirium's TP4xCP4 topology and NKI kernels exactly.

**fps calibration** (where delirium's 14 fps sits): CausVid 9.4, RELIC 16, delirium 14,
Matrix-Game 2.0 / OmniForcing / WorldPlay ~24-25, Matrix-Game 3.0 40, Mirage 24 @ 40 ms.
delirium is at the low-normal end for a 1.3B model on Trainium — consistent with its
bandwidth/launch-bound roofline.

### Open questions this research surfaced

- Confirm FDS's exact mathematical definition against the repo source (is it a Fréchet distance
  in action/IDM-embedding space, or an RLIR-style per-frame action-F1 aggregation?) — the guide
  currently describes it as `1 - action_F1`, which should be verified.
- delirium's model lineage and Trn2-vs-GPU parity + the NKI kernel path vs the Decart mega-kernel
  approach are worth a deeper internal comparison.
