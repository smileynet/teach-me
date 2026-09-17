# Ticket 366 — Source verification for the world-models teaching domain

Verified by reading the ACTUAL repo files under `.references/` (not the existing findings docs).
Every claim below cites `file:line`. Symlink targets resolve to:
`world-models/` → `/local/home/sabiggin/code/world-models/`,
`delirium-world-models-poc/` → the Delirium PoC repo.

---

## FDS exact definition

**Verdict:** The behavioral FDS is **literally `1 - action_F1`**, where `action_F1` is a
**macro-F1 over discrete action channels from an IDM round-trip** (re-infer actions from the
generated frames, compare to the input actions). It is **NOT** a Fréchet distance, and there is
**no IDM-embedding-space distance** anywhere in the computation. "FDS" here is a project-coined
"Fidelity/Divergence Score" on a `0.0=perfect → 1.0=divergent` scale — it is not the classical
Fréchet Distance / FVD, despite the name's resemblance.

**Quoted evidence (the trusted scalar):**
`.references/world-models/tools/fds_harness.py:202-203`
```python
    # Behavioral FDS (TRUSTED): 1 - action-following F1 (0 perfect follow .. 1 no follow).
    fds_beh = float(np.clip(1.0 - beh.action_f1, 0.0, 1.0))
```

**Where `action_f1` comes from — IDM round-trip macro-F1, not an embedding distance:**
`.references/world-models/tools/fds_harness.py:113-133` (`behavioral_axis`)
```python
    """IDM round-trip: re-infer actions from generated frames, compare to input actions.
    ...
    inferred = idm(gen_frames)                # (T-1, A)
    ...
    disc_gt = (gt[:, :n_discrete] > 0.5).astype(int)
    disc_pr = (pr[:, :n_discrete] > 0.5).astype(int)
    f1 = _macro_f1_multihot(disc_gt, disc_pr)
    cam_l1 = None
    if gt.shape[1] > n_discrete:
        cam_l1 = float(np.mean(np.abs(gt[:, n_discrete:] - pr[:, n_discrete:])))
    return BehavioralScores(action_f1=f1, camera_l1=cam_l1)
```

**The F1 itself is a plain per-channel binary macro-F1 (multi-hot buttons):**
`.references/world-models/tools/fds_harness.py:94-107` (`_macro_f1_multihot`) — computes per-channel
TP/FP/FN → precision/recall → F1, then `np.mean` across channels. No feature extractor, no covariance,
no Gaussian fit — none of the machinery a Fréchet distance would require.

**Visual axis is separate and explicitly NOT trusted for behavior** (so the "Frechet-like" intuition
does not sneak in via the visual side either): `fds_harness.py:9` (`visual-fidelity axis — PSNR / LPIPS
per frame — REPORTED, NOT trusted for behavior`) and the visual FDS is just mean drift error,
`fds_harness.py:204` (`fds_vis = float(np.mean(curve))`), where the drift curve is a PSNR-derived
per-step error (`drift_over_horizon`, `fds_harness.py:139-155`).

**Corroborating prose (same repo, describes FDS the same way — no embedding Fréchet):**
- `.references/world-models/tools/README.md:16` — "behavioral axis (**IDM round-trip macro-F1**, *trusted*)".
- `.references/world-models/docs/games-wmlbench-proposal.md:65` — "**FDS (games) = oracle-referenced
  rollout divergence** ... FDS keeps the `0.0` = perfect → `1.0` = divergence scale and the default
  `0.2` retrain threshold."
- `.references/world-models/docs/games-wmlbench-proposal.md:73` — action-following is "via **IDM
  round-trip** (re-infer action from generated frames, compare to input)."

**One nuance worth teaching accurately:** `action_F1` in the harness is a *macro-F1 of button
presses*, i.e. an accuracy-style score in `[0,1]` — so `1 - action_F1` is a divergence in `[0,1]`.
Continuous camera error (`camera_l1`) is computed and reported but is **not** folded into the trusted
`fds_behavioral` scalar (`fds_harness.py:203` uses only `action_f1`). A guide should not imply camera_L1
is part of the FDS number.

---

## Delirium lineage & fps

**Verdict:** Confirmed. The Delirium PoC exposes **two distinct models** — do not conflate them:

1. **Rolling Forcing = Wan2.1-1.3B** (text-to-video), the ~4 fps interactive path.
2. **Matrix-Game 3.0 = Wan2.2-5B** (native action control), the ~17 fps path.

The **"~14 fps" number is a *separate, offline* Rolling-Forcing benchmark** (block-1 steady-state at
TP4×CP4), **not** the interactive frontend fps and **not** Matrix-Game. Mixing these up is the main
risk for the guide.

**Base-model lineage — quoted:**
`.references/delirium-world-models-poc/WORLD_MODELS.md` (Section 2, "Two selectable models"):
```
- **Rolling Forcing (Wan2.1-1.3B)** — text-to-video, ~4 fps, WASD → prompt-deltas
  + a trained action-conditioning pathway. Runs on Trainium *or* NVIDIA GPU.
- **Matrix-Game 3.0 (Wan2.2-5B)** — native trained-in action control, ~17 fps,
  720p, on-frame HUD, image-conditioned (seed frame per scenario). 4×H100 FSDP.
```
The repo also states it is "a **fork of TencentARC RollingForcing**" (WORLD_MODELS.md header), and RF's
checkpoint is the shipped DMD checkpoint (below). So: **RF's base model is Wan2.1-T2V-1.3B** — the
ticket's "Wan2.1-T2V-1.3B?" is **correct** for the Rolling Forcing path.

**The ~14 fps recipe — quoted (all fields verified against `VERIFIED_14FPS_BASELINE.md`):**
> "**~14 fps** = block-1 steady-state at **TP4×CP4, 480×640, frame_seq_length 1200, 5 denoise steps**."
(`VERIFIED_14FPS_BASELINE.md`, "THE NUMBER")

Recipe table (`VERIFIED_14FPS_BASELINE.md`, "THE RECIPE"):
| field | value |
|-------|-------|
| topology | **TP4 × CP4 = 16 ranks** (`--tp_degree 4`, NPROC=16) |
| resolution | **480×640** (`--latent_w 80`) → **frame_seq_length 1200** |
| denoise steps | **5** — `denoising_step_list [1000,800,600,400,200]` |
| checkpoint | **checkpoints/rolling_forcing_dmd.pt** (shipped T=5 DMD, 16G) |
| ring | `RF_RING=1` (optional — CP-query path already gives ~14) |
| frames | `--num_output_frames 21 --chunk-size 3 --fps 16 --use_ema` |
| accelerator/claim | **m-lnc1-trn2 (16 NeuronCores, LNC1)** — i.e. **Trainium2** |

Measured detail: two runs, block-1 median **13.92** / **13.89**, max **14.16** / **14.03**; the
"14.1" people quote is the **block-1 peak** (fresh KV window); full 6-block rolling median tapers to
**13.2** as the KV window fills (`VERIFIED_14FPS_BASELINE.md`, "THE NUMBER"). So "~14 fps" = block-1
peak, "~13.2 fps" = sustained rolling — both from the same run.

**Accelerator:** the 14 fps recipe runs on **Trainium2** (16 NeuronCores, LNC1 claim `m-lnc1-trn2`).
Topology is **TP4×CP4** (context-parallel), and the 14 fps is the **CP-query path**, with `RF_RING`
being an optional fast path that lands within noise (`VERIFIED_14FPS_BASELINE.md`, "RING IS OPTIONAL").

**Trn2-vs-GPU parity — quoted / verdict:**
- **No numeric Trn2-vs-GPU parity is stated.** `VERIFIED_14FPS_BASELINE.md` reports **only Trainium2**
  numbers; it never gives a matching NVIDIA-GPU fps to compare against, so there is **no parity claim**.
- `WORLD_MODELS.md` (Section 2) says RF "**Runs on Trainium *or* NVIDIA GPU**" and (Section 4) that "RF
  on Trainium2 — proven end-to-end (LNC2 fix); gated only on scarce trn2.48xl Spot capacity," while the
  RF NVIDIA GPU backend is "generating, action pathway wired." That establishes RF runs on both
  accelerators, but **does not assert equal fps / output parity** between them. Treat any "Trn2 == GPU"
  claim as unsupported by these two files.

---

## Corrections needed to the guide

Apply these only where the guide currently says otherwise (verify against the guide text before editing):

1. **FDS behavioral definition — keep `1 - action_F1`; do NOT call it a Fréchet distance.**
   If the guide describes behavioral FDS as "a Fréchet distance in an IDM-embedding space" (or any
   embedding/feature-distance framing), that is **wrong**. The source computes
   `fds_behavioral = clip(1 - action_F1, 0, 1)` where `action_F1` is a macro-F1 of IDM-round-trip
   button predictions (`fds_harness.py:203`, `:126`, `:94-107`). Correct wording:
   *"Behavioral FDS = 1 − (macro-F1 of the IDM round-trip on discrete actions), on a 0=perfect→1=divergent
   scale."* If the guide already says `1 - action_F1`, it is **correct — leave it**.

2. **Don't imply camera_L1 is inside the FDS scalar.** The trusted `fds_behavioral` uses `action_f1`
   only; `camera_l1` is reported separately (`fds_harness.py:203` vs `:131-133`). Fix any guide text
   that sums or averages camera error into the FDS number.

3. **Clarify the FVD/Fréchet distinction (anti-confusion note).** The name "FDS" invites confusion with
   FVD (Fréchet Video Distance). This project's FDS is *not* FVD — the proposal even contrasts them:
   a model "can win visual-quality metrics (FVD/CD-FVD) while losing every action-following metric"
   (`games-wmlbench-proposal.md:30`). If the guide equates FDS with FVD/Fréchet, correct it.

4. **fps claims — attribute each number to the right model + regime:**
   - "~14 fps" (peak) / "~13.2 fps" (sustained) belongs to **Rolling Forcing on Trainium2**,
     offline benchmark at **TP4×CP4, 480×640, seq-len 1200, 5 denoise steps** — NOT the interactive
     browser fps and NOT Matrix-Game. If the guide attributes "14 fps" to the live demo or to MG3, fix it.
   - Interactive Rolling Forcing is **~4 fps**; **Matrix-Game 3.0 (Wan2.2-5B) is ~17 fps, 720p**
     (`WORLD_MODELS.md` Section 2). Keep RF (Wan2.1-1.3B) and MG3 (Wan2.2-5B) as two separate models.

5. **Base model — "Wan2.1-T2V-1.3B" is correct for Rolling Forcing.** If the guide says RF is built on
   Wan2.1-T2V-1.3B, that matches the source (`WORLD_MODELS.md` Section 2). Do not attribute the 5B
   (that's Matrix-Game 3.0 / Wan2.2-5B).

6. **Do NOT claim Trn2-vs-GPU parity.** These two files state RF runs on both accelerators but give no
   comparative fps. If the guide asserts Trainium2 matches GPU throughput, mark it unverified / remove it.

---

## Open

- **GPU-side fps for Rolling Forcing is not quantified** in the two Delirium files read. The 14 fps
  ledger is Trainium2-only; establishing Trn2-vs-GPU parity (or the gap) would need the GPU serving
  logs / `gpu/serve_gpu.py` benchmarks, not covered here.
- **`0.2` retrain threshold provenance:** the proposal states FDS keeps a default `0.2` retrain
  threshold (`games-wmlbench-proposal.md:65`), but `fds_harness.py` does not encode a threshold — it
  only emits the scalar. If the guide teaches a threshold, cite the proposal, not the harness.
- **Recorded-ceiling context for F1:** `tools/README.md:27` notes real-data F1 ceilings (~0.457 dense /
  ~0.196 sparse) and that 32-frame clips give F1≈0 (needs ≥128 frames). Relevant if the guide teaches
  "what a good FDS number looks like" — a low F1 (high FDS) can be architectural/context-limited, not
  necessarily poor action-following (`tools/README.md:25-28`). Not a correction, but worth folding in.
- **"FDS" acronym expansion** is not spelled out verbatim in the files read (used as a coined term).
  If the guide expands it, flag as inferred rather than sourced.
