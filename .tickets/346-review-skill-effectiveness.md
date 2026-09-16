---
id: "346"
title: "Deep-dive agent skill activation and workflow overlap"
status: done
priority: low
blocked_by: ["342"]
type: research
tags: ["arch-review", "skills"]
validation_criteria:
  - "Every project skill has positive and negative activation examples"
  - "Overlapping skills are tested against representative prompts"
  - "Recommendations map to observed behavior rather than file length"
---

# Deep-dive agent skill activation and workflow overlap

## Intent source

Follow-up proposed by the architecture review. This repository is the test bed for learning
skills, but the skill layer has not been evaluated as a system.

## What to review

Assess activation accuracy, false positives, missing triggers, workflow completeness,
reference depth, duplicated instructions, and handoffs among teach, generate-topic, quiz-me,
wait-what, jargon, visual QA, diagram, Ink, and asset-conversion skills.

## Context

Read `.kiro/skills/**/SKILL.md`, global skill-authoring guidance, AGENTS.md's workflow table,
and representative completed tickets. Judge effectiveness from observed routing and outcomes.

## Acceptance criteria

- [x] Every skill has at least two positive and two negative activation probes
- [x] Tests cover teach/generate-topic and the Ink/tooling family overlaps
- [x] Findings distinguish activation, instruction quality, and missing capability
- [x] Recommended edits cite observed failed or inefficient behavior
- [x] Accepted changes receive tickets; rejected consolidations include rationale

## Resolution

Completed the 13-skill activation and workflow review in `.scratch/research/346-skill-effectiveness.md`, including positive/negative probes and live overlap classification. The report verifies a nonexistent Ink skill claim, the ambiguous teach/generate-topic boundary, and local-state instruction drift while rejecting broad consolidation. Tickets #359–#362 capture the follow-up work; #361 is sequenced behind #341. Evidence: complete skill inventory, live routing probes, AGENTS/skill comparison, and Git history for the claimed Ink path.
