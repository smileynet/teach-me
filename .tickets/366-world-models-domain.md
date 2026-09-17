---
id: "366"
title: "Set up world-models domain (MAP + study-guide-backed topics + source-verification gate)"
status: in_progress
blocked_by: []
priority: medium
validation_criteria:
  - "world-models.MAP.md exists with the topic spine + prereq edges (passes check-maps-forest)"
  - "Source-verification gate defined (every lesson claim traces to a cited repo file or [L#]-tagged external source; two known TODOs resolved)"
  - "Provenance recorded; standalone depth-0; no lessons generated until sign-off"
tags: ["content"]
---

# Set up world-models domain (MAP + study-guide-backed topics + source-verification gate)

Stand up the standalone **`world-models`** teaching domain — what an interactive, action-steered
world model is, how you build one (real-time video-diffusion), and how you tell a good one from a
"vivid dream" (evaluation). Conceptual/architecture track, not a code-heavy runtime track.

**Setup/scaffold + proposal only — NO lessons generated.** Design source (already written +
promoted): `.memory/research/world-models-and-genmedia/01-world-models.md` (briefing + study
guide + prior-art research). Backing findings: `repo-findings/{world-models,delirium-world-models-poc}.md`
and `gap-research/{world-model-eval-prior-art,realtime-worldmodel-serving}.md`.

## Why this domain

Two explored repos are the whole arc: `world-models` (the FDS evaluation benchmark) and
`delirium-world-models-poc` (a real-time RF/Wan2.1 generator on Trainium). The study guide already
has the concepts, glossary, explain-to-a-colleague self-tests, and situated prior art (IDM
round-trip lineage, FVD/CD-FVD, Decart as the internal serving analog). This ticket turns that into
a MAP + validation gate.

## Domain shape (proposed)

```yaml
domain: world-models
description: "Interactive, action-steered environment simulation: what world models are, how real-time video-diffusion world models are built and served, and how you evaluate them (behavioral vs visual)."
depth: 0
parent: null
leads_to: [generative-media-pipelines]   # serving a world model is a gen-media-pipeline problem
```

Standalone depth-0. `leads_to` the sibling domain (#367) because the delirium serving path
(Trainium, SSE frame streaming, scale-from-zero) is a generative-media-pipeline concern.

## Proposed topic spine (from the study guide's concept list — refine at scaffold time)

| # | slug | core idea | prereqs |
|---|------|-----------|---------|
| 1 | `what-is-a-world-model` | interactive/action-conditioned simulation vs a fixed engine vs a video generator; the "vivid dream" problem | [] |
| 2 | `the-landscape` | six-way architecture taxonomy + AWS-deployability tiers (self-host/walled/API-only) | [1] |
| 3 | `evaluation-and-fds` | ranking reversal; engine-as-oracle; FDS four axes (visual untrusted, behavioral/IDM round-trip trusted, drift/h*, action-sensitivity); situated against FVD/CD-FVD + IDM prior art | [1] |
| 4 | `building-a-real-time-world-model` | causal video DiT + rectified flow; Rolling Forcing + attention sink + streaming KV cache; DMD distillation to few steps | [1] |
| 5 | `action-conditioning` | why DMD is action-invariant; gated action modules + supervised term; why LoRA-on-attention failed; coarse temporal granularity | [4] |
| 6 | `serving-and-accelerators` | Trainium/Neuron + NKI, TP/CP topology, bandwidth/launch-bound roofline, fps operating points; Decart internal analog; WebRTC/SSE streaming | [4] (soft [5]) |

Prereq edges: `1→2`, `1→3`, `1→4→5`, `4→6`. All within-map. (6 topics; trim/merge at scaffold —
2+3 are the conceptual core, 4–6 the build/serve arc.)

## Validation gate (source-verification, not a code harness)

This is a conceptual domain — no Godot/ink runtime artifact. The gate is **claim traceability**:

- Every load-bearing lesson claim traces to a cited **repo file path** (from `repo-findings/`) or a
  **`[L#:confidence]` external source** (from `gap-research/`). Lessons cite sources per
  `source-authority` steering — no teaching from parametric memory.
- Standard `mise run verify` applies (links + lint + SVG theming + glossary coverage).
- Numbers get cited or framed as general (per AGENTS.md) — e.g. "~14 fps at 480×640 on TP4×CP4"
  cites `VERIFIED_14FPS_BASELINE.md`, not a remembered figure.

## Two source-TODOs to resolve BEFORE authoring topic 3 / topic 4-6

1. **FDS exact math** — the guide says behavioral FDS = `1 - action_F1`; confirm against
   `world-models/tools/fds_harness.py` (may be a Fréchet distance in IDM-embedding space). Topic 3
   depends on this.
2. **delirium model lineage / Trn2-vs-GPU parity** — confirm against
   `delirium-world-models-poc/WORLD_MODELS.md` + `VERIFIED_14FPS_BASELINE.md` before topic 6.

## Acceptance criteria

- [x] `world-models.MAP.md` at `library/world-models/maps/` with the topic spine + prereq edges; ULIDs via `tools/migrate_map_ids.py --apply`; passes `tools/check-maps-forest.py`
- [x] Source-verification gate recorded (claim→cited-source contract; the two source-TODOs above **resolved** — see scaffold note) — MISSION.md Constraints + RESOURCES.md
- [x] Standalone depth-0 confirmed; `leads_to: [generative-media-pipelines]` edge recorded (validated in forest — that domain now exists, #367)
- [x] Provenance recorded (design source = the promoted guide; backing = repo-findings + gap-research) — RESOURCES.md
- [ ] Topic spine reviewed/trimmed (6 → final count) with the user before topic tickets — **AWAITING USER REVIEW** (see scaffold note)
- [ ] NO lessons generated — topic tickets created after this is signed off

## Scaffold status (2026-09-17) — PROPOSAL COMPLETE, awaiting sign-off

Scaffold placed and validated (proposal-only, no lessons):
`library/world-models/{MISSION.md, RESOURCES.md, maps/world-models.MAP.md}` — 6 topics.

**Both source-TODOs resolved** (review pass, `gap-research/366-source-verification.md`):
1. **FDS math CONFIRMED** = literally `1 - action_F1` (`fds_harness.py:202-203`), macro-F1 over
   discrete action channels via IDM round-trip. NOT a Fréchet distance, NOT FVD; `camera_l1` is
   reported but not folded into the scalar. The guide was correct — baked into topic 3's framing.
2. **delirium lineage CONFIRMED**: RF = Wan2.1-T2V-1.3B (~4 fps interactive); MG3 = Wan2.2-5B
   (~17 fps, 4×H100). The "~14 fps" = RF **offline on Trainium2**, TP4×CP4=16, 480×640, 5 steps —
   distinct from the demo and from MG3. **Trn2-vs-GPU parity is NOT stated** — the MAP/MISSION
   explicitly avoid claiming it.

**AWS-doc anchors woven into topic 6** (the SageMaker-Async analog for this domain,
`gap-research/366-aws-doc-anchors.md`): **NxD Inference** + **NKI** guide (accelerator serving) and
**SageMaker real-time + `InvokeEndpointWithResponseStream`** (frame delivery). Honest gap recorded:
no first-party AWS doc for real-time *video generation* exists — topic 6 frames it as extrapolation
from DiT image serving + streaming, not a documented workflow.

6 topics: (1) what-is-a-world-model → (2) the-landscape, (3) evaluation-and-fds,
(4) building-a-real-time-world-model → (5) action-conditioning, (6) serving-and-accelerators.
Prereq edges: `1→{2,3,4}`, `4→{5,6}`. `leads_to: [generative-media-pipelines]` (frontmatter +
topic 6). **Verification:** forest check clean (all 9 domains); `map:generate` → 6 topics;
`check-index-drift` → 10 index pages in sync.

**Decision for you before topic tickets:** approve the 6-topic spine as-is, or adjust (e.g. split
serving vs accelerators, or merge landscape into topic 1). On your go, I cut the 6 topic tickets.

## Notes

- Design source + backing research already written and committed under
  `.memory/research/world-models-and-genmedia/`.
- Pairs with #367 (generative-media-pipelines). The two domains share the delirium serving seam;
  #366 `leads_to` #367.
