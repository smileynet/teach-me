---
id: "360"
title: "Define teach and generate-topic ownership and routing"
status: open
priority: high
type: design
blocked_by: ["342"]
tags: ["arch-review", "skills", "authoring"]
validation_criteria:
  - "Equivalent requests route to one named owner without contradictory instructions"
---

# Define teach and generate-topic ownership and routing

## Intent

Give `teach` and `generate-topic` distinct, complementary ownership so conversational learning and durable curriculum generation do not issue conflicting instructions.

## Context

The skill review found lexical routing works today, but each skill presents overlapping pipeline authority. The resulting boundary is implied rather than explicit, which risks duplicate generation or untracked learner-state writes.

## What to build

Define a handoff: `teach` owns conversation, orientation, and re-explanation of existing material; `generate-topic` owns research-backed durable artifact creation and invokes shared authoring guidance as needed.

## Acceptance criteria

- [ ] Both skills state their owned outcomes, non-goals, and explicit handoff triggers.
- [ ] The shared authoring sequence has one source of truth; duplicate instructions are removed or linked.
- [ ] Representative prompts for learning an existing topic, asking for a new lesson, and completing a topic route deterministically.
- [ ] The behavior preserves the knowledgeable-colleague posture and the research-before-authoring requirement.
- [ ] Documentation and ticket records reflect the chosen boundary.
