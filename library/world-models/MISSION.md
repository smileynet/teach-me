# Mission: Understand world models — building and evaluating them

## Why

A world model is an AI system that *simulates an interactive environment* — predict the next frame
given the current state and an action — instead of rendering from a hand-coded engine. Two real
efforts are the whole arc: a benchmark that scores whether a world model actually *plays* correctly
(the FDS evaluation harness) and a browser-playable real-time video-diffusion generator on AWS
Trainium (the delirium PoC). The field's central trap is the "vivid dream": a model that looks
photoreal while ignoring the player's actions. This track teaches what world models are, how a
real-time one is built and served, and — the part everyone gets wrong — how you tell a good one
from a convincing hallucination.

## Success looks like

- Can explain a world model vs. a video generator vs. a game engine (the difference is
  action-conditioned, over-time steerability — not image quality)
- Can explain the "ranking reversal" and why a behavioral metric is mandatory, and describe the
  FDS harness's four axes (visual untrusted; behavioral / IDM-round-trip trusted; drift/`h*`;
  action-sensitivity guard)
- Can sketch how a real-time video-diffusion world model works — causal DiT + rectified flow,
  Rolling Forcing + attention sink + streaming KV cache, DMD distillation to few steps
- Can explain action conditioning (why DMD is action-invariant; gated modules + a supervised term;
  why LoRA-on-attention failed) and the accelerator reality (Trainium/Neuron, TP/CP, the
  bandwidth/launch-bound roofline)

## Constraints

- Conceptual/architecture track — no runtime code harness; validation is source-verification +
  `mise run verify` (links/lint/SVG/glossary)
- Every load-bearing claim cites a source: a repo file path (world-models, delirium) or an
  `[L#:confidence]`-tagged external/internal source — no parametric memory
- **Verified facts to hold exactly** (from the 2026-09-17 source-verification pass): behavioral FDS
  is literally `1 - action_F1` (a project-coined score, NOT a Fréchet distance, NOT FVD; camera_L1
  is reported separately and not folded into the scalar); the "~14 fps" figure is the RF-1.3B
  (Wan2.1-T2V-1.3B) offline benchmark on Trainium2 (TP4×CP4=16 cores, 480×640, 5 denoise steps) —
  distinct from Matrix-Game-3.0 (Wan2.2-5B, ~17 fps, 4×H100) and from the interactive demo; no
  Trn2-vs-GPU parity is claimed in the source
- `leads_to: generative-media-pipelines` — serving a world model is an instance of that domain
