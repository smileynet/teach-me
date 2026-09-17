# Delirium — World Models for Games (PoC) — Research Findings

Repo explored via symlink → `/local/home/sabiggin/code/delirium-world-models-poc`.
All claims cite file paths within that repo.

## Purpose

Delirium is an internal AWS proof-of-concept that turns real-time **video-diffusion
"world models"** into a browser-playable, action-steered game: the player picks a
scenario (Wizard of Oz / Rainbow Six Siege / Cyberpunk City / Alien Jungle) and a
renderer, then drives the world live with WASD + action keys while a video model
generates the frames (`README.md`, `WORLD_MODELS.md` §1). It is a **fork of TencentARC
RollingForcing** adapted to run the renderer on **AWS Trainium2 (Neuron) or NVIDIA
GPU**, with an added game layer (ink narrative engine + Bedrock-vision observer) that
overlays real quests/HUD/30-minute arc on top of the render-only demo
(`README.md`, `DELIRIUM.md`, `gameplay/INK_CONTRACT.md`).

## Architecture & Components

Global picture in `WORLD_MODELS.md` §2 (ASCII diagram) and `DELIRIUM.md`:

- **Browser frontend** — a single self-contained HTML doc served by nginx via a k8s
  ConfigMap (`infra/k8s/rf-frontend-behind-alb.yaml`); scenario select, model select
  (RF | MG3), WASD/action keys, DOM HUD overlay, canvas video player, inline JS (no
  bundler) (`WORLD_MODELS.md` §3).
- **Cognito-gated ALB (HTTPS/OIDC)** on EKS with path routing:
  `/` → frontend, `/generate,/health` → RF on Trainium, `/gpu/*` → RF on NVIDIA GPU,
  `/mg3/*` → Matrix-Game 3.0, `/status` → capacity probe, `/observe` → Bedrock vision
  (`WORLD_MODELS.md` §2).
- **Two selectable renderers, kept deliberately distinct (do not merge):**
  - **Rolling Forcing (RF)** — Wan2.1-T2V-1.3B, text-to-video (~4–14 fps depending on
    stack), WASD → prompt-deltas + a trained action-conditioning pathway; runs on
    Trainium *or* NVIDIA GPU (`WORLD_MODELS.md` §2, `gpu/README.md`).
  - **Matrix-Game 3.0 (MG3)** — Wan2.2-5B, native trained-in action control, ~17 fps,
    720p, image-conditioned with a per-scenario seed frame; served lockstep across
    4×H100 with FSDP (`WORLD_MODELS.md` §2, `gpu/README.md`, `gpu/serve_mg3.py`).
- **Gameplay engine — three decoupled loops** (`gameplay/INK_CONTRACT.md`,
  `WORLD_MODELS.md` §2):
  1. **Render loop** — selected model generates video from current prompt + seed +
     actions.
  2. **Observer loop** (~every 3s, async) — samples a rendered frame, asks a Bedrock
     vision model (Nova/Claude) a coarse question, feeds a scene tag/event back to ink
     (soft signal only).
  3. **Story loop** — `inkjs` runs a per-scene `.ink` quest; ink is the **single source
     of truth** for game state, drives HUD/objective and the next scene prompt, and can
     trigger new scenes/levels.
- **Infra (AWS CDK, `infra/`)** — CDK app (`infra/app.py`, `infra/stacks/`:
  network/data/cluster/frontend stacks) provisions VPC, data stores, an EKS cluster,
  ACM cert, Cognito user pool, and the ALB; `infra/k8s/` holds serving/observer/ingress
  manifests; nodegroups ship at `desired=0` for near-zero idle cost
  (`README.md` deploy section, `infra/README.md`, `infra/stacks/cluster_stack.py`).
- **Ownership split** (`DELIRIUM.md`): Delirium-owned = `gameplay/`, `gpu/`, `infra/`,
  `npc/`, `WORLD_MODELS.md`, plus edits to `README.md` and `training/` (Track-2 action
  conditioning). Everything else at repo root (`configs/`, `models/`, `kernels/`,
  `train.py`, `rf-*.yaml`, `verify_*.py`, `docs/`, `*_latents.py`) is **upstream
  RollingForcing research code** kept as-is; `sync-upstream.sh` pulls upstream without
  clobbering Delirium files.

## World Model Concepts

**The model.** The RF renderer is a **causal video DiT** (Diffusion Transformer) built
on Wan2.1-T2V-1.3B. Shapes from `models/dit_model.py` (`CausalWanModel`): hidden
dim=2048, ffn_dim=8192, 32 layers, 16 heads (head_dim=128), patch_size (1,2,2), 16
latent channels in/out, text_len=512, bf16. It is text-to-video (`model_type='t2v'`),
uses **RoPE** rotary position embeddings (`_init_rope_freqs`, `kernels/rope.py`) and a
**FlowMatchScheduler** with timestep_shift (`WanDiffusionWrapper`, `models/dit_model.py`).

**Rectified-flow / flow matching.** Training and inference use a flow objective: the
model predicts a flow that is converted to x0 (`convert_flow_pred_to_x0`,
`models/dit_layers.py`; `FlowMatchScheduler` in `models/dit_model.py`). Noise is added
as `x_t = (1-sigma)*x + sigma*noise` with flow target `noise - x`
(`training/model/action_dmd.py` `supervised_action_loss`, `models/dit_pipeline.py`
`add_noise`).

**Distillation (DMD).** The few-step real-time student is produced by **Distribution
Matching Distillation** — three co-trained models: generator/student (Wan2.1-1.3B
causal), a **frozen teacher** (Wan2.1-T2V-**14B**), and a critic/fake_score (1.3B). The
DMD gradient is `(fake_score − real_score)` normalized (DMD paper eq. 7/8), and it is
**data-free**: the student rolls out its own samples and teacher+critic score them
(`training/model/dmd.py` `_compute_kl_grad`; `docs/PAPER_parallelism_neuron_training.md`
§0–1). The shipped checkpoint is a **T=5 DMD** student (`denoising_step_list =
[1000,800,600,400,200]`, `configs/rolling_forcing_dmd.yaml`). `docs/DISTILL_T4_RUNBOOK.md`
covers re-distilling to **T=4** to push past 16 fps (DiT cost scales ~(T+1); you cannot
just shorten the step list on a T=5 checkpoint — the DMD student only predicts accurate
x0 at the noise levels it was distilled on).

**Rolling Forcing (the real-time trick).** Autoregressive long-video diffusion: frames
are denoised together in a **rolling window** (window length = number of denoising
steps) so blocks mutually refine, breaking error-accumulation drift (`README.md`
upstream TL;DR; `models/dit_pipeline.py` `_run`, which builds `window_start/end_blocks`
and a per-phase renoise plan). A novel **Attention Sink** (anchor block) preserves
global context over thousands of frames. The self-attention KV cache keeps a **sink
(anchor) block** + a rolling **working cache** and evicts the middle
(`gpu/action_causal_model.py` `CausalWanSelfAttention.forward`: `sink_tokens`,
eviction/roll logic, anchor re-RoPE). Generation is **causal with a streaming KV cache**
per transformer block (`models/dit_pipeline.py` `_initialize_kv_cache` /
`_initialize_crossattn_cache`).

**Latents & the pipeline.** Standard latent video diffusion: T5/UMT5-XXL encodes the
prompt (`encode_prompt.py`, `models/t5.py`), the DiT denoises 16-channel latents, and a
**VAE** decodes latents → pixels, streamed in chunks (`decode_latents.py`, `models/vae.py`,
`generate_latents.py`). Full path in `e2e_pipeline.py`: encode prompt → rolling-forcing
DiT stream → VAE chunk-decode → mp4, with true frame streaming
(`inference_rolling_forcing_stream`, `models/dit_pipeline.py`).

**Action conditioning (Delirium Track-2).** RF is text-only by construction, so DMD
alone leaves any added action pathway ignored (measured 0.000-effect). Delirium grafts
**action modules** onto the DiT — a button embedding + an axes MLP whose tokens append
to the cross-attention context, multiplied by a **zero-init scalar gate** so they start
as a no-op and learn to "un-gate" (`gpu/action_causal_model.py`:
`action_button_embedding` = `nn.Embedding(num_action_buttons, dim)`, `action_axes_mlp`,
`action_gate = nn.Parameter(torch.zeros(1))`, returning `action_gate * cat(toks)` —
6 buttons / 4 axes). To give the action embedding a real gradient, `ActionDMD` adds a
**supervised next-frame flow-matching term** on real (latent, action) pairs from the
**CrossFPS** dataset, keeping DMD as a small-weight regularizer:
`L = λ_sup·L_supervised(action) + λ_dmd·L_dmd` (`training/model/action_dmd.py`;
dataset in `training/utils/crossfps_dataset.py`). At serve time the LoRA is skipped by
default (`SKIP_ACTION_LORA=1` — it degraded quality); the action modules + gate carry
steering (`gpu/README.md`, `gpu/action_causal_model.py`).

**FPS baseline (measured, not remembered).** `VERIFIED_14FPS_BASELINE.md`: **~14 fps** =
block-1 steady-state at **TP4×CP4 = 16 NeuronCores**, 480×640, `frame_seq_length` 1200,
5 denoise steps, on trn2 (two independent runs: 13.92 / 13.89 block-1 median; full
rolling-window median ~13.2 as the KV window fills — the "14.1" people quote is the
fresh-window block-1 peak). Ring attention is **optional** — the 14 fps comes from the
**CP-query path** (gather Q over attn-tp ranks, RoPE only this rank's shard), which
ships unconditionally for world_size>1; `RF_RING=1` gives the same ~14 ("ring plumbing
is free when not sharding"). The older **SP path** (all-gather Q over all 16, RoPE full,
discard 3/4) is what pre-CP commits used and only did ~13.2 (16r) / 9 (8r). MG3's
"real-time" is ~17 fps but **per-clip** (~5s generation, first frame ~11s), not
frame-level twitch (`WORLD_MODELS.md` §4).

**Honest known limits** (`WORLD_MODELS.md` §4): RF is text-to-video with no true
persistence — each clip subtly re-rolls the world; WASD steers, it doesn't move a rigid
camera. The `initial_latent` continuity path in upstream RF is **dead code** — do not
re-attempt (also noted in `training/model/action_dmd.py`).

## Generative Media Pipeline Aspects

- **Accelerators / serving infra.** Two backends. **RF on Trainium2** via `serve.py`
  (16 NeuronCores, TP4×SP4, NKI kernels — gated on scarce trn2 Spot capacity). **RF on
  NVIDIA GPU** via `gpu/serve_gpu.py` (FastAPI + SSE wrapping upstream
  `CausalInferencePipeline`, batch `/gpu/generate/stream` + true-streaming
  `/gpu/generate/stream_rt`, loads the trained action checkpoint). **MG3** via
  `gpu/serve_mg3.py` (FastAPI + SSE, lockstep 4-rank FSDP `generate()` — all ranks call
  main-thread, rank 0 serves uvicorn on a bg thread + broadcasts params; wraps
  `process_video` to push each clip's frames as decoded; per-scenario seed images from
  a PVC) (`gpu/README.md`, `WORLD_MODELS.md` §2).
- **Tensor / context / sequence parallelism.** `models/dit_pipeline.py`
  `init_parallel_groups(sp_degree, tp_degree)` registers three process groups: `world`,
  `attn-tp` (tensor-parallel over heads), `attn-sp` (sequence/context parallel over the
  token sequence); `sp_degree * tp_degree == world_size`. Reference topology is
  **TP4×CP4 = 16 ranks** (`VERIFIED_14FPS_BASELINE.md`, `docs/ROOFLINE_RF_1_3B.md`).
  Neuron supports collectives (broadcast/all-reduce/all-gather) but **not P2P
  send/recv**, which drives a broadcast-based cross-group design
  (`docs/PAPER_parallelism_neuron_training.md` §2). `frame_seq_length` must be
  divisible by world_size (1200/1440/1680 legal at 16 ranks; 1560 fails —
  `configs/rolling_forcing_dmd.yaml` comments, `models/dit_pipeline.py` asserts).
- **Roofline / bottleneck.** RF 1.3B runs at only **~4–6% MFU** on trn2 — it is
  **per-rank bandwidth- and kernel-launch-bound, not FLOP-bound** (window-limited
  attention, small D). fps is flat below a per-rank "bandwidth knee" then rolls off ∝
  sequence length; LNC2 (24 GB/rank) pushes the knee one seq-len rung above LNC1
  (12 GB/rank). The only optimizations that moved fps were **launch-count reductions**
  (RoPE batching), not FLOP/precision (`docs/ROOFLINE_RF_1_3B.md` §0–5).
- **Kernels (Neuron NKI).** `kernels/` holds hand-written **NKI** (Neuron Kernel
  Interface) kernels: `self_attention.py` / `self_attention_nst.py` (fused flash
  attention), `cross_attention.py`, `rope.py` (batched even/odd swap + free-dim
  broadcast to cut the gpsimd hotspot), `kv_cache_copy.py`, `causal_conv3d_cache.py`,
  plus nkilib helpers (`nkilib_tensor_view.py`, `nkilib_modular_allocator.py`). The
  compile strategy (`docs/compilation_pattern.md`): **compile stateless compute
  (Linear/FFN/norms/embeddings) with `torch.compile(backend='neuron')`; leave stateful
  logic + attention as NKI kernels in eager** to avoid Dynamo graph breaks and
  NEFF fragmentation. `verify_*.py` at repo root validate the ring-attention / RoPE-QK
  fuse / KV-cache kernel math.
- **Deployment jobs.** `rf-*.yaml` and `rolling-forcing-*.yaml` are k8s Jobs for
  training/distillation/benchmark on Trainium: `rf-distill-*.yaml` (DMD distillation at
  various TP: tp20/24/32/64, 14B teacher variants), `rf-rope-qk-fuse-*.yaml` (kernel
  benchmark sweeps by seq-len 1200/1440/1680), `rf-job*.yaml` / `iter1000-job.yaml`
  (fps benchmark runs), `rf-render-*.yaml`, `rf-prompt-probe-job.yaml` (ranks prompts by
  distillation convergence — `docs/PROMPT_DIFFICULTY_PROBE.md`), `rf-validate-*.yaml`
  (CPU/Neuron validation), `rf-gradio-*.yaml` / `rf-deploy.yaml` (serving). k8s serving
  manifests in `infra/k8s/` (`rf-serve-deploy-{gpu,trn1,trn2}.yaml`,
  `rf-serve-mg3.yaml`, `rf-status-service.yaml`, `rf-observe-service.yaml`,
  `rf-serve-ingress-trn2.yaml`, `rf-frontend-behind-alb.yaml`). MG3 image built in-cluster
  via Kaniko (`infra/k8s/mg3-image-build.yaml` + `infra/docker/mg3.Dockerfile`); pinned
  by `@sha256:` digest with `imagePullPolicy: Always` (mutable tag + IfNotPresent
  silently serves a stale cached digest — `WORLD_MODELS.md` §5).
- **Distillation training pipeline (Neuron).** `training/`: `train.py` entry,
  `training/pipeline/rolling_forcing_training.py` + `rolling_forcing_inference.py`,
  trainers (`training/trainer/distillation.py`, `distillation_3group.py`, `gan.py`,
  `ode.py`), models (`training/model/{dmd,action_dmd,causvid,gan,sid}.py`), CrossFPS
  data (`training/utils/crossfps_dataset.py`, `training/tools/fetch_crossfps_*.py`),
  T5 precompute on CPU to free HBM (`training/precompute_embeds.py`). Convergence is
  watched via `dmdtrain_gradient_norm` (the surrogate `generator_loss` is flat by
  construction) with visual A/B as ground truth (`docs/DISTILL_T4_RUNBOOK.md`).

## Key Terms & Jargon

- **World model** — a generative model that renders an explorable environment frame-by-
  frame in response to actions, instead of a fixed game engine (`WORLD_MODELS.md` §1).
- **Rolling Forcing (RF)** — TencentARC's autoregressive long-video diffusion method:
  denoise frames in a rolling window for real-time streaming with reduced drift
  (`README.md` upstream TL;DR).
- **Attention Sink / anchor block** — a retained first KV block that anchors global
  context over thousands of frames (`README.md`; `gpu/action_causal_model.py` sink
  logic).
- **DiT (Diffusion Transformer)** — the transformer backbone that denoises video latents
  (`models/dit_model.py` `CausalWanModel`).
- **DMD (Distribution Matching Distillation)** — data-free distillation training a
  few-step student via `(fake_score − real_score)` from a frozen teacher + critic
  (`training/model/dmd.py`).
- **Rectified flow / flow matching** — the training objective: predict a straight-line
  flow between noise and data (`FlowMatchScheduler`, `models/dit_model.py`).
- **Denoising step list / T** — the discrete noise timesteps the student denoises
  through; T=5 shipped, T=4 pushes fps (`configs/rolling_forcing_dmd.yaml`,
  `docs/DISTILL_T4_RUNBOOK.md`).
- **Latent / VAE** — compressed 16-channel representation the DiT operates on; VAE
  decodes latents → pixels, streamed in chunks (`models/vae.py`, `decode_latents.py`).
- **frame_seq_length** — patched tokens per latent frame ((h/2)·(w/2)); must be
  divisible by world_size (`configs/rolling_forcing_dmd.yaml`, `models/dit_pipeline.py`).
- **KV cache** — cached keys/values for causal attention; RF keeps a sink block + a
  rolling working cache with eviction (`models/dit_pipeline.py`,
  `gpu/action_causal_model.py`).
- **TP / SP / CP** — tensor / sequence / context parallelism degrees; reference topology
  TP4×CP4=16 ranks (`models/dit_pipeline.py`, `VERIFIED_14FPS_BASELINE.md`).
- **NKI (Neuron Kernel Interface)** — Amazon's low-level kernel language for Trainium;
  used for attention/RoPE/KV-cache kernels (`kernels/`, `kernels/rope.py`).
- **NEFF / NTFF** — Neuron Executable File Format / trace file; compiled kernel units
  profiled for overhead (`docs/compilation_pattern.md`, `e2e_pipeline.py` profiler).
- **LNC (Logical NeuronCore)** — LNC2 fuses 2 physical cores (≈24 GB/rank, ~2× BW) vs
  LNC1 (~12 GB/rank); shifts the bandwidth knee (`docs/ROOFLINE_RF_1_3B.md` §2).
- **MFU** — Model FLOPs Utilization; RF sits at ~4–6% (launch/bandwidth-bound)
  (`docs/ROOFLINE_RF_1_3B.md` §5).
- **Trainium2 / trn2** — AWS training accelerator; trn2.48xlarge is Capacity-Block only,
  no on-demand SKU (`AGENTS.md` constraints, `docs/PAPER_parallelism_neuron_training.md`).
- **Matrix-Game 3.0 (MG3)** — Wan2.2-5B world model with native action control, 4×H100
  FSDP, per-clip streaming (`gpu/serve_mg3.py`, `gpu/README.md`).
- **CrossFPS** — the real (latent, action) dataset used for the supervised action term
  (`training/utils/crossfps_dataset.py`, `training/model/action_dmd.py`).
- **ink / inkjs** — narrative scripting language + JS runtime holding game state/quests
  (`gameplay/*.ink`, `gameplay/INK_CONTRACT.md`).
- **Observer loop** — Bedrock vision model sampling rendered frames for coarse scene
  tags fed back to ink as a soft signal (`gameplay/INK_CONTRACT.md`).
- **dmdnorm / dmdtrain_gradient_norm** — magnitude of the DMD update = distance from the
  teacher distribution; the primary convergence signal (`docs/PROMPT_DIFFICULTY_PROBE.md`,
  `docs/DISTILL_T4_RUNBOOK.md`).

## Notable Files

- `WORLD_MODELS.md` — global architecture, current dev state, onboarding (read first).
- `README.md` — Delirium intro + "deploy your own" + full upstream RollingForcing README.
- `DELIRIUM.md` — repository map (Delirium-owned vs upstream).
- `VERIFIED_14FPS_BASELINE.md` — the measured 14 fps recipe + run-id ledger.
- `models/dit_model.py` — `CausalWanModel` (the DiT) + `WanDiffusionWrapper`.
- `models/dit_pipeline.py` — `CausalInferencePipeline`: rolling-window scheduling, KV
  cache alloc, parallel-group init, checkpoint sharding.
- `gpu/action_causal_model.py` — RF DiT with grafted zero-gated action modules + the
  sink/working-cache KV logic.
- `training/model/action_dmd.py` — hybrid supervised-action + DMD-regularizer objective.
- `training/model/dmd.py` — core DMD distillation (`_compute_kl_grad`).
- `e2e_pipeline.py` — end-to-end T2V streaming pipeline (encode → DiT stream → VAE →
  mp4) with FLOPs/TFLOPS metering.
- `decode_latents.py` / `encode_prompt.py` / `generate_latents.py` — pipeline stages.
- `configs/rolling_forcing_dmd.yaml` — the shipped T=5 DMD config (with the
  frame_seq_length divisibility notes).
- `docs/ROOFLINE_RF_1_3B.md` — the measured roofline / bandwidth-knee analysis.
- `docs/DISTILL_T4_RUNBOOK.md` — re-distill to T=4 for >16 fps; convergence signals.
- `docs/PROMPT_DIFFICULTY_PROBE.md` — cheapest-prompt-to-distill probe methodology.
- `docs/PAPER_parallelism_neuron_training.md` — 3-model DMD co-residency on one trn2
  node; Neuron parallelism constraints.
- `docs/compilation_pattern.md` — stateless-compile + NKI-eager Neuron compile pattern.
- `kernels/` — NKI attention/RoPE/KV-cache kernels; `verify_*.py` at root validate them.
- `gpu/serve_gpu.py` / `gpu/serve_mg3.py` — the two serving backends.
- `gameplay/INK_CONTRACT.md` + `gameplay/{oz,r6s,cyber,alien}.ink` — the game layer.
- `infra/` — CDK app (`app.py`, `stacks/`) + `infra/k8s/` manifests + `infra/docker/`.
- `rf-*.yaml` / `rolling-forcing-*.yaml` / `iter1000-job.yaml` — Trainium train/distill/
  benchmark k8s Jobs.
