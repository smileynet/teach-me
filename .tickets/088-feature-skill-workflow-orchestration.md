---
id: "088"
title: "Feature: skill workflow orchestration — subagent pipeline for lesson generation"
status: open
blocked_by: []
priority: medium
---

# Feature: skill workflow orchestration — subagent pipeline for lesson generation

## Problem

Skills run independently — the teach skill generates a lesson, but the jargon skill, quiz generation, reference doc creation, and SVG migration all require separate manual invocations. This causes:

1. **Missed steps**: lessons ship without jargon annotations (found by Playwright audit — 7/9 lessons had no term spans)
2. **Inconsistency**: some pages get all post-processing, others don't
3. **Agent burden**: the agent must remember the full sequence every time
4. **No validation gate**: nothing checks that all pipeline steps completed before marking a topic "done"

## Proposed Architecture

A **lesson generation workflow** that chains skills as subagent stages in a pipeline:

```
teach (generate lesson)
  → draw-diagram (ensure SVG uses CSS vars)
  → jargon (annotate domain terms)
  → generate-quiz-page (from SR questions)
  → generate-reference (companion doc)
  → generate-map-page (update with new topic)
  → verify (mise run verify)
```

### Implementation Options

**Option A: Orchestrator skill (lightweight)**
A new `generate-topic` skill that dispatches each step as a subagent:
```yaml
name: generate-topic
description: "Generate a complete topic: lesson + diagram check + jargon + quiz + reference + map update"
```
The skill reads the MAP.md for the topic, then orchestrates sub-skills in sequence. Each stage validates its output before proceeding. The workflow is defined in the skill's process section.

**Option B: mise task pipeline**
Define the workflow as a mise task with dependencies:
```toml
[tasks."topic:generate"]
depends = ["setup"]
run = """
python tools/generate-lesson.py --topic $1 --workspace $2
python tools/generate-quiz-page.py --workspace $2 --lesson-id $1 ...
python tools/jargon-annotate.py --file $2/lessons/$1.html
mise run verify
"""
```
This requires turning the jargon pass into a script (currently it's a skill/agent task).

**Option C: Workflow definition file (most flexible)**
A `workflows/lesson-generation.yaml` that defines stages, dependencies, and validation gates:
```yaml
name: lesson-generation
stages:
  - name: research
    skill: teach
    output: lessons/{id}.html
  - name: diagram-check
    script: tools/check-svg-vars.py
    input: lessons/{id}.html
  - name: jargon
    skill: jargon
    input: lessons/{id}.html
  - name: quiz
    tool: generate-quiz-page.py
    args: [--workspace, "{workspace}", --lesson-id, "{id}"]
  - name: reference
    skill: teach  # reference generation sub-mode
    output: reference/{id}.html
  - name: map-update
    tool: generate_map_page.py
    args: ["{map}", --workspace, "{workspace}"]
  - name: verify
    run: mise run verify
```
The orchestrator reads this file and dispatches each stage.

### Recommendation: Option A (Orchestrator Skill)

Start with Option A. It's the simplest — just a skill that documents the pipeline steps and dispatches them. It doesn't require new infrastructure. If the pattern proves useful across multiple workflows (quiz-generation, topic-completion, workspace-init), then extract it into Option C (workflow definition file).

### Key Design Decisions

1. **Failure handling**: If jargon pass fails, the lesson is still valid — mark jargon as skipped, continue. If quiz gen fails (no questions), that's a real failure — block.
2. **Idempotency**: Each stage must be safe to re-run. Jargon re-annotation overwrites existing spans. Quiz regeneration overwrites existing quiz page.
3. **Workspace-awareness**: Every stage receives `--workspace` to operate on the correct directory.
4. **Validation gate**: `mise run verify` runs at the end and must pass before the topic is marked complete in MAP.md.

## What to build

1. Create `.kiro/skills/generate-topic/SKILL.md` — orchestrator skill that runs the full pipeline
2. Document the pipeline steps and which are required vs optional
3. Add a validation step (e.g., `tools/check-topic-completeness.py`) that verifies all artifacts exist for a topic
4. Update the `teach` skill to reference `generate-topic` as the workflow that wraps it
5. Consider: should `generate-topic` dispatch subagents or just call tools sequentially?

## Acceptance criteria

- [ ] `generate-topic` skill exists and documents the full lesson generation pipeline
- [ ] Running the skill produces: lesson + reference + quiz + jargon annotations + map update
- [ ] Each stage handles failure gracefully (skip optional, block on required)
- [ ] `mise run verify` is the final gate
- [ ] Existing lessons can be "completed" by running the workflow against them (catches missing steps)
