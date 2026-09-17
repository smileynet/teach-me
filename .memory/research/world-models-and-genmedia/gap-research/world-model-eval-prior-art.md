# World-Model Evaluation: Prior Art (external + internal)

Research pass for situating the world-models repo's home-grown **FDS** metric against the
established field. Compiled 2026-09-16.

## Summary

World-model / video-generation evaluation has converged on **three orthogonal axes**, and no
single metric covers all three:

1. **Distributional visual quality** — does the generated video look like real video?
   Dominated by **FVD** (Fréchet Video Distance) and its content-debiased successor **CD-FVD**,
   with per-frame **PSNR / SSIM / LPIPS** as reference-based supplements. [L4:established]
2. **Action-following / controllability** — did the world actually respond to the *commanded
   action*? This is the axis a world model lives or dies on, and the field's answer has
   converged on the **Inverse Dynamics Model (IDM) round-trip**: generate video from actions,
   then recover actions from the video and measure agreement (F1/precision/recall or MSE).
   [L2:established]
3. **Physics / commonsense plausibility** — does the rollout obey conservation laws, object
   permanence, causality? Covered by benchmark suites (**WorldModelBench**, **VBench-2.0**,
   **WorldBench**, **PAWBench**) rather than a single scalar. [L4:established]

The world-models repo's **FDS** metric sits in axis (2): the IDM round-trip is *not novel to
the repo* — it is the established action-following evaluation idea (VPT 2022 → MineWorld 2025 →
RLIR Sep 2025 → EVA/RoboWM-Bench 2026). What a repo-specific FDS can legitimately contribute is
a *specific packaging* (e.g., a Fréchet-style distance computed in IDM/action-embedding space
rather than I3D visual-feature space, or a single-number aggregation of the round-trip). The
study guide should frame FDS as "our instantiation of the IDM-round-trip family," not as a
brand-new idea. [L3:inferred]

Internally, Amazon has **no published proprietary world-model eval metric** that surfaced in
this search. The internal footprint is (a) literature tracking (varada's "v-bot" daily arxiv
scans, the "All Things AI" newsletter), (b) a metric glossary in the WW-Ops-Privacy *Model
Quality Builders Guide*, and (c) a *CreativeAgent* related-work page cataloguing video-gen
metrics (FID-vid, FVD, TGVE). No "FDS"/"Fréchet Distances" internal artifact was found. [L1:verified — negative result]

---

## Established metrics

### Distributional visual quality

- **FVD (Fréchet Video Distance)** — Unterthiner et al., "Towards Accurate Generative Models of
  Video: A New Metric & Challenges," arXiv:1812.01717 (2018) / OpenReview rylgEULtdN. The video
  analogue of FID: embeds real and generated clips with an **I3D** network (Inflated 3D ConvNet,
  Kinetics-trained) and computes the Fréchet distance between the two Gaussians. Captures spatial
  *and* temporal coherence; validated against a large human study. Lower is better. This is the
  canonical name a "Fréchet ... Distance" metric echoes. [L4:established]
- **CD-FVD (Content-Debiased FVD)** — Ge et al., "On the Content Bias in Fréchet Video Distance,"
  CVPR 2024 (arXiv:2404.12391; project site content-debiased-fvd.github.io; `pip install cd-fvd`).
  Shows FVD is **biased toward per-frame image quality over temporal/motion realism**, because the
  I3D features come from a supervised, content-biased classifier. Fix: swap I3D for features from a
  large **unsupervised** video model (VideoMAE), which de-biases the metric. Directly relevant: a
  home-grown Fréchet metric inherits this bias unless the backbone is chosen carefully. [L1:verified]
- **PSNR** (Peak Signal-to-Noise Ratio) and **SSIM** (Structural Similarity) — classic
  reference-based, per-frame fidelity metrics; PSNR rewards pixel-MSE, SSIM adds luminance/
  contrast/structure. Both need aligned ground truth, so they only work for *reconstruction*-style
  eval (given the true next frames). Hore & Ziou, "Image quality metrics: PSNR vs. SSIM," ICPR 2010.
  [L4:established]
- **LPIPS** (Learned Perceptual Image Patch Similarity) — deep-feature perceptual distance; used
  as a reference-based frame metric and, in RLVR-World, as a *reward* signal (L1+LPIPS to ground
  truth). [L2:established]
- Consensus critique (repeated across sources): "SSIM and PSNR reward pixel fidelity over semantic
  correctness, while FVD favors distributional textures over physical plausibility"
  (arXiv:2605.03475, "An End-to-End Multi-Dimensional Benchmark for Generative Video Models").
  This is the standard motivation for *adding* an action-following axis — i.e., for FDS to exist.
  [L4:established]

### Action-following / controllability metrics

- The dominant approach is the **IDM round-trip** (see next section) reported as
  **F1 / precision / recall** over discretized action classes (MineWorld / RLIR protocol) or as
  **action MSE / SE(3) trajectory error** in robotics (WorldEcho, EVA). [L2:established]
- **Velocity / acceleration / jerk** smoothness and **embodiment-constraint violation** counts —
  EVA (arXiv:2603.17808) turns the IDM into a reward that penalizes physically implausible induced
  actions. [L2:reported]
- **VBench** action/controllability dimensions and **MLLM-as-judge** scores for
  instruction-following (WorldModelBench, Omni-WorldBench). [L4:established]

---

## Named benchmarks

- **VBench** — Huang et al., CVPR 2024 (arXiv:2311.17982). 16 fine-grained dimensions (subject
  consistency, motion smoothness, temporal flickering, spatial relationship, imaging quality via
  the MUSIQ predictor, etc.). **VBench-2.0** (arXiv:2503.21755) adds five higher-order axes: Human
  Fidelity, **Controllability**, Creativity, **Physics**, **Commonsense**. The de-facto standard
  for general text/image-to-video quality. [L4:established]
- **WorldModelBench** — Li et al., "Judging Video Generation Models As World Models," NeurIPS 2025
  Datasets & Benchmarks (arXiv:2502.20694; worldmodelbench-team.github.io). Evaluates video
  generators *specifically as world models* across application domains (autonomous driving,
  robotics, gaming, natural). Two dimensions beyond visual quality: **instruction-following** and
  **physics-adherence** (catches e.g. mass-conservation violations like object size drifting).
  Ships human labels + a fine-tuned 2B **judger** model (8.6% higher accuracy than GPT-4o at
  predicting world-model violations). [L4:established]
- **WorldBench** — "Disambiguating Physics for Diagnostic Evaluation of World Models"
  (arXiv:2601.21282). Isolates individual **physics concepts**; finds *all* tested SOTA video world
  models lack the physical consistency needed for reliable interaction. Has an intuitive-physics
  subset and a physical-parameter-estimation subset. [L4:established]
- **WorldMark / "A Unified Benchmark Suite for Interactive Video World Models"**
  (arXiv:2604.21686) — motivated by the fact that *interactive* models (Genie, YUME, HY-World,
  Matrix-Game) are each evaluated on private scenes/trajectories, making cross-model comparison
  impossible. Provides a common I2V playing field with action-following, visual quality, memory,
  and interaction-physics axes. (Earlier drafts titled WorldOdysseyBench / WorldRoamBench.)
  [L4:reported]
- **RoboWM-Bench** — "A Benchmark for Evaluating World Models in Robotic Manipulation"
  (arXiv:2604.19092). Converts generated manipulation videos into **embodied action sequences**
  and validates them by **execution in a physics sim** — an execution-grounded action-following
  test, not just a visual score. [L4:reported]
- **PAWBench / PAWEval** — "How Far Are We from Probabilistically Aligned World Modeling?"
  (arXiv:2608.27345). Reframes eval from single-trajectory plausibility to **distributional**
  correctness: repeated rollouts under the same (obs, action) should recover the *distribution* of
  valid physical outcomes. 50 scenarios, 11 systems; no model matches reference probabilities.
  [L4:reported] (surfaced internally via AllThingsAI 2026-09-04)
- **Omni-WorldBench / Omni-Metrics** — interaction-centric 4D (space+time) eval; quantifies the
  *causal impact* of interaction actions on outcomes and intermediate state trajectories, 18 models
  (arXiv:2603.22212). [L4:reported] (surfaced internally via AllThingsAI 2026-03-30)
- **Genie / Genie 2 / Genie 3** (DeepMind) — the reference "generative interactive environment"
  line. Genie (arXiv:2402.15391, ICML 2024) trains a **latent action model (LAM)** unsupervised
  from unlabelled internet video; its *controllability* is evaluated by whether the learned latent
  actions produce consistent, distinguishable state changes. Genie 2/3 are foundation world models
  for training/evaluating embodied agents. Each was evaluated on its own protocol — the gap
  WorldMark calls out. [L4:established]
- **Minecraft / VPT-based eval** — the VPT paper (Baker et al., "Video PreTraining: Learning to
  Act by Watching Unlabeled Online Videos," NeurIPS 2022) trained the **IDM that has become the
  standard Minecraft action-following judge**: 90.6% keypress-prediction accuracy, R²=0.97 on
  mouse-movement regression, from ~2,000 h of contractor-labeled gameplay. MineWorld
  (arXiv:2504.08388) defines the Minecraft action-following eval protocol (99 action classes: 77
  discrete + 22 camera bins) that RLIR reuses. This VPT→MineWorld lineage is the closest public
  analogue to a game-domain FDS. [L1:verified]

---

## IDM / action-following prior art

The **Inverse Dynamics Model round-trip** is the core idea behind action-following eval, and it is
well-established prior art — a repo's FDS is one instantiation of it.

- **Definition** — an IDM estimates the action that transitions observation `o_t → o_{t+1}`, i.e.
  it models `p_IDM(a_t | o_t, o_{t+1})`. Because the action space is far lower-dimensional than raw
  video, an IDM can be trained accurately from limited labeled data and is *highly sensitive to
  subtle visual artifacts and action-magnitude differences* (RLIR Fig. 1 shows it distinguishing
  "forward" vs "sprint" and flagging a missing crack as a wrong action). [L1:verified]
- **The round-trip / cycle-consistency idea** — generate video conditioned on ground-truth actions
  → run the IDM to recover actions from the generated video → score agreement. Recovered ≈ commanded
  ⇒ the world followed the action. Appears as:
  - **RLIR** — "Reinforcement Learning with Inverse Rewards for World Model Post-training,"
    Microsoft Research, arXiv:2509.23958 (Sep 2025). Uses IDM-recovered action accuracy as a
    *verifiable reward* (per-frame 0/1 match, averaged) for GRPO post-training of MineWorld
    (autoregressive) and NFD (diffusion) world models. Reports action-following as **F1/precision/
    recall** and quality as **FVD, PSNR, VBench imaging quality**. Explicitly argues the IDM signal
    is "objective, scalable, low-bias" vs. human-preference or pixel-level (L1+LPIPS) rewards, and
    is bounded above by IDM accuracy. This is the closest published cousin to an FDS-style metric.
    [L1:verified]
  - **"Evaluating Robot Foundation Models via Self-Consistent Video Generation,"**
    arXiv:2606.18610 — "forward-inverse dynamics consistency": jointly predict frames from actions
    and recover actions from frames to anchor rollouts to a plausible action manifold and penalize
    drift a forward-only model can't see. [L4:reported]
  - **EVA** — "Aligning Video World Models with Executable Robot Actions via Inverse Dynamics
    Rewards," arXiv:2603.17808. IDM trained on real robot trajectories, repurposed as a reward that
    scores generated videos through the actions they induce. [L4:reported]
  - **ACID** — "Action Consistency via Inverse Dynamics for Planning with World Models,"
    arXiv:2607.02403 — cycle action-consistency constraint at decision time. [L4:reported]
  - **"Turning Video Models into Generalist Robot Policies,"** arXiv:2605.27817 — decouples an
    embodiment-specific IDM (Jacobian-based) from an action-free video planner. [L4:reported]
  - **RLVR-World** (arXiv:2505.13934) — the *alternative* to the IDM round-trip: pixel-level
    verifiable reward (L1+LPIPS to ground truth). RLIR §6.1 shows this **fails** (correlated with
    pretraining loss, uniform pixel weighting, conflicts with novel-content generation, and
    reward-hackable by globally darkening frames) — a strong argument for action-space (FDS-style)
    scoring over pixel-space. [L1:verified]
- **Lineage / provenance for a study guide**: Ha & Schmidhuber "World Models" (2018, arXiv:1803.10122)
  → VPT IDM (2022) → Genie LAM (2024) → MineWorld action protocol (2025) → RLIR IDM-reward (2025) →
  EVA/ACID/RoboWM-Bench/WorldEcho (2026). [L3:inferred lineage, individual nodes L1/L4]
- **Known failure mode to cite**: WorldEcho ("Do Robotic World Models Really Follow Actions?",
  arXiv:2608.24885) finds world models often *ignore commanded actions* or produce visually invalid
  rollouts once actions leave the expert distribution — exactly what an action-following/FDS metric
  is designed to catch, and a caution that FDS should be tested on **off-expert** actions.
  [L4:reported]

---

## Internal prior art (cite URLs)

No proprietary Amazon world-model eval *metric* (no "FDS" / "Fréchet Distances") was found. The
internal footprint is literature curation + a metrics glossary:

- **Model Quality — Builders Guide** (WW Ops Privacy / AI Compliance):
  https://w.amazon.com/bin/view/WW_Ops_Privacy/AI_Compliance/Model_Quality/ — internal glossary
  defining **FVD, FID, PSNR, SSIM, Inception Score, Reconstruction Error** (FVD = "FID but for
  video," I3D features, lower is better). Useful as an internal citation for the standard metrics.
  [L4:verified]
- **CreativeAgent — Related Work** (Yashal team):
  https://w.amazon.com/bin/view/Yashal/Docs/CreativeAgent/v1/RelatedWork/ — internal catalogue of
  **video-generation metrics** (FID-vid, FVD with the TATS FVD implementation link, TGVE protocol,
  CLIP-score, PickScore) and I2V/V2V eval datasets. Closest internal doc that actually tabulates
  the metric landscape. [L4:verified]
- **"v-bot" daily arxiv scans** (varada) — a running internal literature tracker with dedicated
  **World Models** sections capturing the exact eval papers above. Examples:
  - https://w.amazon.com/bin/view/Users/varada/v-bot/Literature/Daily-Scans/Must-Track-2026-08-27/
    — WorldEcho action-following diagnosis; DreamLedger reliability records.
  - https://w.amazon.com/bin/view/Users/varada/v-bot/Literature/Daily-Scans/Arxiv-2026-07-05/ —
    ACID (inverse-dynamics cycle consistency), RoboWorld (video WM + VLM scoring, Pearson r=0.989
    with real-world policy ranking).
  - https://w.amazon.com/bin/view/Users/varada/v-bot/Literature/Daily-Scans/Must-Track-2026-09-03/
    — "Do Better Imagined Rollouts Mean Better Robot Control?" (open-loop rollout accuracy is a poor
    proxy for closed-loop control — a direct caution about single-number rollout metrics like FDS).
  [L5:verified as internal tracking, primary claims trace to arXiv L4]
- **"All Things AI" newsletter** (gopalkmr, 8-agent pipeline) — surfaces world-model eval work with
  Amazon-relevance framing:
  - https://w.amazon.com/bin/view/AllThingsAI/2026_09_04/ — **PAWBench/PAWEval** (distributional
    world-model eval).
  - https://w.amazon.com/bin/view/AllThingsAI/2026_03_30/ — **Omni-WorldBench** (interaction-centric
    4D eval).
  - https://w.amazon.com/bin/view/AllThingsAI/2025_12_23/ — MMGR (reasoning taxonomy "beyond FVD").
  - https://w.amazon.com/bin/view/AllThingsAI/2026_02_10/ — Waymo using DeepMind **Genie 3** as a
    driving world simulator; Google **Veo** world simulator ranking policy checkpoints (1,600+
    rollouts) — an internal note on generative video used for policy *evaluation*.
  [L5:verified as internal commentary]

**Gap to flag for the study guide**: the internal record is *awareness*, not a competing internal
metric. If the world-models repo's FDS is an Amazon-original packaging of the IDM round-trip, it has
no internal predecessor to reconcile against — its novelty claim is purely against the *external*
IDM-round-trip family above. [L1:verified — negative result]

---

## How FDS compares

(FDS = the world-models repo's home-grown metric; interpreting "Fréchet Distances" / action-space
distance in the IDM round-trip family. Confirm exact definition against the repo before finalizing.)

| Property | FVD | CD-FVD | PSNR/SSIM/LPIPS | IDM round-trip (RLIR/EVA) | **FDS (repo)** |
|---|---|---|---|---|---|
| Axis measured | visual dist. | visual dist. (de-biased) | per-frame fidelity | action-following | action-following (likely) |
| Needs ground-truth frames | no (dist. only) | no | **yes** | no (needs GT actions) | no (needs GT actions) |
| Feature space | I3D visual | VideoMAE visual | pixels/deep | action | action / IDM-embedding |
| Catches "ignored the action" | ✗ | ✗ | ✗ | ✓ | ✓ |
| Catches physics violations | weak | weak | ✗ | partial | partial |
| Reward-hackable | — | — | yes (darken frames) | resistant | resistant (if action-space) |

**Positioning statements the study guide can make (verify against repo FDS definition):**

1. **FDS is not a new idea; it is a new packaging.** The IDM round-trip (generate-from-action →
   recover-action → score) is established prior art (VPT 2022, MineWorld/RLIR 2025). FDS's
   contribution is *how* it aggregates that signal — e.g., a Fréchet-style distance in
   action/IDM-embedding space rather than RLIR's per-frame F1, or a single scalar for ranking.
   [L3:inferred]
2. **FDS complements FVD; it does not replace it.** FVD/CD-FVD answer "does it look real?"; FDS
   answers "did it obey the action?" A world model can score well on FVD while ignoring commanded
   actions (WorldEcho). Report both. [L2:established]
3. **If FDS uses I3D-style features, cite the CD-FVD content-bias warning.** A Fréchet distance
   over a supervised-classifier backbone over-weights per-frame quality vs. motion; prefer
   unsupervised video features. If FDS operates in *action* space it sidesteps this — state which.
   [L1:verified]
4. **FDS should be tested on off-expert actions.** WorldEcho shows action-following collapses
   outside the expert manifold; an FDS validated only on in-distribution rollouts can be
   vacuously high. [L4:reported]
5. **Upper-bounded by IDM accuracy.** Like RLIR's reward, any IDM-based metric is capped by the
   IDM's own accuracy (RLIR reports GT-video F1 as the ceiling). The study guide should report the
   IDM's standalone accuracy as the FDS ceiling. [L1:verified]

---

## Sources (URLs + [L#:confidence])

External — metrics:
- FVD: https://arxiv.org/abs/1812.01717 · https://openreview.net/pdf?id=rylgEULtdN [L4:established]
- CD-FVD: https://arxiv.org/html/2404.12391v1 · https://content-debiased-fvd.github.io/ ·
  https://github.com/songweige/content-debiased-fvd · https://pypi.org/project/cd-fvd/ [L1:verified]
- "Beyond FVD: Enhanced Evaluation Metrics for Video Generation Quality":
  https://arxiv.org/html/2410.05203v2 [L4:reported]
- PSNR vs SSIM: Hore & Ziou ICPR 2010 (cited in RLIR refs) [L4:established]
- Multi-dim critique of SSIM/PSNR/FVD: https://arxiv.org/html/2605.03475v1 [L4:reported]

External — benchmarks:
- VBench: https://arxiv.org/abs/2311.17982 ·
  https://openaccess.thecvf.com/content/CVPR2024/papers/Huang_VBench_..._paper.pdf [L4:established]
- VBench-2.0: https://arxiv.org/html/2503.21755v1 [L4:established]
- WorldModelBench: https://arxiv.org/abs/2502.20694 · https://worldmodelbench-team.github.io/ ·
  https://proceedings.neurips.cc/paper_files/paper/2025/hash/4ec03ed08a3fcb59e1c815b5598beff1-Abstract-Datasets_and_Benchmarks_Track.html [L4:established]
- WorldBench (physics): https://arxiv.org/pdf/2601.21282v2 [L4:established]
- WorldMark / Unified Interactive WM benchmark: https://arxiv.org/abs/2604.21686v1 [L4:reported]
- RoboWM-Bench: https://arxiv.org/html/2604.19092 [L4:reported]
- PAWBench: https://arxiv.org/abs/2608.27345 (v3) [L4:reported]
- Omni-WorldBench: https://arxiv.org/abs/2603.22212 [L4:reported]
- Genie: https://arxiv.org/html/2402.15391v1 · https://openreview.net/pdf?id=bJbSbJskOS ;
  Genie 2: https://deepmind.google/blog/genie-2-a-large-scale-foundation-world-model/ ;
  Genie 3: https://deepmind.google/blog/genie-3-a-new-frontier-for-world-models/ [L4:established]

External — IDM / action-following:
- RLIR: https://arxiv.org/html/2509.23958 [L1:verified — full text read]
- VPT: Baker et al. NeurIPS 2022 (90.6% keypress acc, R²=0.97) — via RLIR refs [L1:verified via RLIR]
- MineWorld: https://arxiv.org/abs/2504.08388 [L4:reported]
- Self-Consistent Video Generation: https://arxiv.org/html/2606.18610v3 [L4:reported]
- EVA: https://arxiv.org/pdf/2603.17808v1 [L4:reported]
- ACID: https://arxiv.org/abs/2607.02403 [L4:reported]
- Turning Video Models into Generalist Robot Policies: https://arxiv.org/html/2605.27817 [L4:reported]
- RLVR-World: https://arxiv.org/abs/2505.13934 (via RLIR §6.1) [L1:verified via RLIR]
- WorldEcho: https://arxiv.org/abs/2608.24885 [L4:reported]

Internal:
- Model Quality Builders Guide: https://w.amazon.com/bin/view/WW_Ops_Privacy/AI_Compliance/Model_Quality/ [L4:verified]
- CreativeAgent Related Work: https://w.amazon.com/bin/view/Yashal/Docs/CreativeAgent/v1/RelatedWork/ [L4:verified]
- v-bot arxiv scans (varada): https://w.amazon.com/bin/view/Users/varada/v-bot/Literature/Daily-Scans/ [L5:verified]
- All Things AI newsletter: https://w.amazon.com/bin/view/AllThingsAI/ (2026_09_04, 2026_03_30, 2025_12_23, 2026_02_10) [L5:verified]

---

## Open questions

1. **What exactly is the repo's FDS?** Confirm against the world-models source: (a) is it a
   Fréchet distance computed in IDM/action-embedding space, or a scalar aggregation of per-frame
   IDM action-agreement (like RLIR's F1)? (b) What IDM backbone / action space does it use?
   The positioning statements above assume the action-space interpretation — verify before writing
   the study guide.
2. **Does FDS use a supervised or unsupervised feature backbone?** Determines whether the CD-FVD
   content-bias caveat applies. [needs repo inspection]
3. **What is the repo IDM's standalone accuracy?** That is the FDS ceiling — needed to interpret
   any FDS number honestly.
4. **Is FDS validated on off-expert actions?** If only in-distribution, cite WorldEcho as a
   limitation.
5. **Any *newer* internal metric?** This search covered ALL / WIKI / SAGE_HORDE. A proprietary
   metric could live in a code package (code.amazon.com), a Quip/PRFAQ, or an org wiki not indexed
   here — worth a targeted repo/Quip search if the study guide needs to claim "no internal
   predecessor" definitively.
6. **FVD vs CD-FVD adoption in the repo's domain** — if the world-models repo also reports a
   Fréchet *visual* metric, confirm whether it's plain FVD (I3D) or CD-FVD, since the field has
   moved toward CD-FVD since CVPR 2024.
