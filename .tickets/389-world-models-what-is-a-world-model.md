---
id: "389"
title: "world-models topic 1: what-is-a-world-model"
status: open
blocked_by: ["366"]
priority: medium
validation_criteria:
  - "Lesson library/world-models/lessons/01-what-is-a-world-model.html generated via generate-topic; passes mise run verify (links/lint/SVG/glossary)"
  - "Every load-bearing claim cites a repo file path or [L#]-tagged source (source-verification gate); no parametric memory"
tags: ["content"]
---

# world-models topic 1: what-is-a-world-model

Author the first lesson of the **world-models** domain (setup: #366). Establishes the core
distinction the whole track rests on.

## What to build

Lesson `library/world-models/lessons/01-what-is-a-world-model.html` via the `generate-topic`
pipeline. Teaches: a world model is *action-conditioned, over-time steerable* environment
simulation — **not** a video generator (fixed clip) and **not** a hand-coded engine. Vocabulary:
state, action, rollout, drift. Names the **"vivid dream"** failure (looks real, ignores the player)
that topics 3+ exist to detect and fix.

- **scope:** substantial · **prereqs:** [] (first topic) · **lesson_file:** 01-what-is-a-world-model.html

## Sources (design + backing)

- Design: `.memory/research/world-models-and-genmedia/01-world-models.md` (Part 1 orientation +
  Part 2 concept 1).
- Backing: `repo-findings/world-models.md` (`.memory/CONTEXT.md` glossary), the "vivid dream" framing
  in `world-models/docs/games-wmlbench-proposal.md`.

## Acceptance criteria

- [ ] Lesson HTML generated at the path above; `mise run verify` passes
- [ ] Source-verification gate: every load-bearing claim cites a repo file path or `[L#]` source
- [ ] In-lesson exercise tests the world-model vs. video-generator vs. engine distinction (the Win)
- [ ] Glossary terms annotated (jargon pass); SR cards produced
