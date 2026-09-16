---
id: "363"
title: "Repair verified lesson navigation and content-contract failures"
status: open
priority: high
type: bug
blocked_by: []
tags: ["arch-review", "curriculum", "quality"]
validation_criteria:
  - "Every shipped library domain passes its documented lesson contract checks"
---

# Repair verified lesson navigation and content-contract failures

## Intent

Repair verified navigation, quick-check, glossary, exercise, read-time, credit, and SVG-contract failures in the shipped lesson library.

## Context

The lesson-quality deep dive ran `check-lesson.py --all` across all seven domains and found broken Q11 navigation, missing Iceberg quick-check concepts, missing glossary/exercise contracts, stale reading estimates, incomplete credits, and hard-coded SVG colors. These are user-visible curriculum integrity failures, not cosmetic warnings.

## What to build

Prioritize real learner journeys: linked lesson navigation and review pages first, then bring all affected domains into conformance without weakening the checker.

## Acceptance criteria

- [ ] All shipped domains pass `check-lesson.py --all` with no failures; remaining warnings are documented and approved only where the contract permits them.
- [ ] Forward/back navigation reaches the correct neighboring lesson or intentionally terminates with an explicit learner-facing choice.
- [ ] Iceberg quick-check pages cover the required key concepts and use the shared visual-token contract.
- [ ] Affected lessons provide required glossary data, exercises, credits, and realistic read-time metadata.
- [ ] No fix suppresses or loosens a checker solely to hide an existing content defect.
