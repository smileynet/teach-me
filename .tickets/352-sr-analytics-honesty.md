---
id: "352"
title: "Correct unsupported SR analytics claims and topic scoping"
status: open
priority: medium
type: feature
blocked_by: ["350"]
tags: ["arch-review", "sr", "analytics"]
validation_criteria:
  - "Displayed SR metrics state whether they are observed measures or estimates"
---

# Correct unsupported SR analytics claims and topic scoping

## Intent

Make spaced-repetition analytics accurate about their meaning and correctly scoped to the learner's selected content.

## Context

The current `exp(-t/interval)` value is labelled knowledge even though it is not a calibrated SM-2 or FSRS retention prediction. Topic analytics are global, and malformed/future timestamps have unclear behavior.

## What to build

Replace or clearly label unsupported estimates, add correct topic filtering, and establish a migration gate before any FSRS-derived prediction is shown.

## Acceptance criteria

- [ ] Unsupported heuristic values are removed or labelled as non-predictive estimates with their formula and limits.
- [ ] Topic-scoped views use only the selected topic's cards and events.
- [ ] Observed review counts, pass rates, and due-card metrics match deterministic fixtures.
- [ ] Future, malformed, and missing timestamps have explicit safe behavior.
- [ ] Any FSRS metric is gated behind a documented scheduler/version migration, not inferred from SM-2 data.
