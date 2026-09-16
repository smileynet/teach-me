---
id: "357"
title: "Track source lineage for committed binary and visual assets"
status: open
priority: medium
type: feature
blocked_by: ["356"]
tags: ["arch-review", "provenance", "assets"]
validation_criteria:
  - "A committed visual or binary asset can be traced to its source and transformation"
---

# Track source lineage for committed binary and visual assets

## Intent

Record practical provenance for committed binary and visual teaching assets without turning authored content into a fragile build pipeline.

## Context

The reproducibility review can validate deterministic HTML projections, but cannot explain where many images, SVGs, and binary assets came from or how they were transformed.

## What to build

Define lightweight per-asset or per-batch lineage metadata covering source, license/attribution, transformation command, and expected output hash where appropriate.

## Acceptance criteria

- [ ] The lineage format distinguishes authored, downloaded, generated, and transformed assets.
- [ ] Each sampled committed binary/visual asset records source or author, license/attribution requirements, and applicable transformation command.
- [ ] Validation flags missing required lineage and stale output hashes without downloading or rewriting assets.
- [ ] The format integrates with lesson citations where the visual source is also a teaching source.
