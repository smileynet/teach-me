---
id: "362"
title: "Add a regression fixture for project skill activation"
status: open
priority: medium
type: feature
blocked_by: ["359", "360"]
tags: ["arch-review", "skills", "testing"]
validation_criteria:
  - "Skill-trigger examples detect missing owners and ambiguous routing"
---

# Add a regression fixture for project skill activation

## Intent

Prevent missing or overlapping project skills from silently drifting out of the documented user experience.

## Context

Thirteen live skills have no activation regression harness; #200's missing Ink skill demonstrates that tickets and prose can claim a route that no longer exists.

## What to build

Create a small maintained fixture of representative user prompts, expected skill owner(s), and allowed no-skill cases. Validate skill existence, trigger metadata, and routing ambiguity without attempting to fully evaluate model behavior.

## Acceptance criteria

- [ ] A fixture covers every project skill plus deliberate negative probes.
- [ ] Validation fails when an expected skill path is missing or a documented trigger has no owner.
- [ ] Overlapping trigger cases declare a preferred owner and acceptable handoff.
- [ ] The harness produces concise actionable output and runs in the normal verification workflow or a documented CI job.
- [ ] It does not claim deterministic LLM activation; documentation states the structural scope.
