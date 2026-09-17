# World Models & Generative Media Pipelines — Research Corpus

Promoted from `.scratch/` on 2026-09-17. Durable synthesis backing two proposed teaching domains
(`world-models`, `generative-media-pipelines`). Source repos were explored via `.references/`
symlinks (`world-models`, `delirium-world-models-poc`, `studio-model-service`, `ArtSmoker`,
`riot-comfy-ui-platform`).

## Contents

- `00-index.md` / `01-world-models.md` / `02-generative-media-pipelines.md` — the two
  briefing+study guides (each: Briefing half, Study half, Part 3 prior-art/gap research). **These
  are the design source for the lesson-domain tickets.**
- `repo-findings/` — per-repo exploration findings, every claim cited to a file path in that repo.
- `gap-research/` — internal + web research filling gaps the repo synthesis surfaced (TTS/speech,
  LoRA training tier, scale-to-zero GPU serving, ComfyUI-at-scale, image→3D, world-model eval
  prior art, real-time world-model serving). Claims carry `[L#:confidence]` source tags.

## Two verification TODOs before authoring lessons

1. **FDS's exact math** — the world-models guide states behavioral FDS = `1 - action_F1`; confirm
   against `world-models/tools/fds_harness.py` (could be a Fréchet distance in IDM-embedding space).
2. **`riot-comfy-ui-platform` package identity** — it didn't surface in InternalSearch (likely a
   private GitFarm package); the AWS reference-sample comparison in the gap research is prior art,
   not a claim about that specific repo.

## Lineage

Repo findings and gap research were gathered by dispatched subagents citing sources; load-bearing
claims for any external briefing should be re-verified against the cited source.
