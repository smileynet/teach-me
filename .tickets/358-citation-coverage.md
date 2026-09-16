---
id: "358"
title: "Validate lesson citation coverage against authoring contracts"
status: open
priority: medium
type: feature
blocked_by: []
tags: ["arch-review", "provenance", "curriculum"]
validation_criteria:
  - "Citation requirements are mechanically checked where their structure is knowable"
---

# Validate lesson citation coverage against authoring contracts

## Intent

Validate that lessons meet the project requirement to teach from cited sources while preserving author judgment about relevance and quality.

## Context

Source citations are a core teaching contract, but the reproducibility review found no coverage oracle. Broken or missing citations can therefore pass structural checks unnoticed.

## What to build

Add a structural citation checker for lesson/reference formats, with clear limits: it verifies presence, parseability, and reachable-link policy where feasible, not the truth of every pedagogical claim.

## Acceptance criteria

- [ ] The contract specifies which lesson/reference sections require citations and what valid citation metadata contains.
- [ ] Validation identifies missing, malformed, duplicate, and disallowed citation structures with file/line diagnostics.
- [ ] Link validation is bounded, cacheable, and distinguishes an unreachable URL from a missing citation.
- [ ] Fixture lessons cover valid citations and each expected failure mode.
- [ ] Documentation states the checker does not establish factual correctness or source authority by itself.
