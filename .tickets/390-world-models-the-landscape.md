---
id: "390"
title: "world-models topic 2: the-landscape"
status: open
blocked_by: ["366", "389"]
priority: medium
validation_criteria:
  - "Lesson library/world-models/lessons/02-the-landscape.html generated via generate-topic; passes mise run verify"
  - "Every claim cites a repo file path or [L#]-tagged source; the six-way taxonomy + deployability tiers are cited"
tags: ["content"]
---

# world-models topic 2: the-landscape

Author lesson 2 of the **world-models** domain (setup: #366; prereq: #389).

## What to build

Lesson `library/world-models/lessons/02-the-landscape.html` via `generate-topic`. Situates the
field so a learner can place any new model:
- The **six-way architecture taxonomy**: video-latent, 3D-native, hybrid engine+model,
  latent-dynamics RL, JEPA, action-foundation — with named examples (Genie, Cosmos, Oasis,
  Dreamer, V-JEPA).
- The **AWS-deployability tiers**: self-hostable today / walled / API-only.

- **scope:** substantial · **prereqs:** [what-is-a-world-model] · **lesson_file:** 02-the-landscape.html

## Sources

- Design: research notes, non-public (Part 1 "The landscape").
- Backing: the per-platform findings (non-public) (`.memory/world-models-synthesis.md` taxonomy +
  deployability tiers). Situate against prior art in the gap research (non-public).

## Acceptance criteria

- [ ] Lesson HTML generated; `mise run verify` passes
- [ ] Source-verification gate satisfied (taxonomy + tiers cited)
- [ ] Exercise: given a model description, classify it into the taxonomy + name its deployability tier
- [ ] Glossary + SR cards produced
