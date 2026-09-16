---
id: "356"
title: "Add generated-artifact manifest and reproducibility drift matrix"
status: open
priority: medium
type: feature
blocked_by: ["331"]
tags: ["arch-review", "provenance", "build"]
validation_criteria:
  - "Generated outputs can be checked for drift without overwriting authored inputs"
---

# Add generated-artifact manifest and reproducibility drift matrix

## Intent

Make the boundary between authored curriculum inputs and deterministic generated artifacts explicit and verifiable.

## Context

The provenance deep dive found deterministic MAP/index/global-map projections but no manifest declaring generator, inputs, outputs, and validation ownership. Deploy dry-run is separately blocked by #331.

## What to build

Add a versioned artifact manifest and a non-destructive drift matrix for deterministic projections. Keep lesson prose, question authoring, and MAP authoring outside the false promise of reproducible generation.

## Acceptance criteria

- [ ] The manifest lists each deterministic artifact class, generator command, tracked inputs, outputs, and validation command.
- [ ] Drift validation regenerates into a temporary location or compares safely without overwriting authored or tracked output.
- [ ] MAP pages, library index, and global map are covered by the matrix.
- [ ] Authored lessons, MAP source, and question banks are explicitly classified as canonical inputs rather than generated projections.
- [ ] CI or `mise run verify` reports actionable drift results once #331 is repaired.
