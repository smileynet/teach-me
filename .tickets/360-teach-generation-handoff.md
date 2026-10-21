---
id: "360"
title: "Define teach and generate-topic ownership and routing"
status: done
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

- [x] Both skills state their owned outcomes, non-goals, and explicit handoff triggers.
- [x] The shared authoring sequence has one source of truth; duplicate instructions are removed or linked.
- [x] Representative prompts for learning an existing topic, asking for a new lesson, and completing a topic route deterministically.
- [x] The behavior preserves the knowledgeable-colleague posture and the research-before-authoring requirement.
- [x] Documentation and ticket records reflect the chosen boundary.

## Resolution (2026-10-21)

Defined teach/generate-topic ownership via ADR 0019 (accepted). teach owns the conversational learning engine (orientation, ZPD selection, re-explanation, navigation, all .user/ learner-state writes); generate-topic owns the durable authoring assembly line and is the single source of truth for the authoring sequence (Phase 1-4, verify gate, committed graph writes). teach invokes generate-topic for tracked artifacts rather than re-running steps. Each SKILL carries a mirrored Ownership & Routing section (owned outcomes, non-goals, handoff triggers); a single routing table maps representative prompts to one owner (rule: durable+verified -> generate-topic, conversation/orientation/re-explanation -> teach). Posture (ADR 0001) and the research-before-authoring gate preserved. AGENTS.md updated. Docs-only change, SKILL frontmatter valid.

### Verification
1. ✓ Equivalent requests route to one named owner without contradictory instructions — "Equivalent requests route to one named owner without contradictory instructions: ADR 0019 routing table + resolving rule; teach SKILL Ownership & Routing section + routing-table anchor maps teach-me-X / generate-a-lesson / complete-a-topic deterministically to a single owner; authoring sequence singly owned by generate-topic so instructions cannot conflict or drift"
