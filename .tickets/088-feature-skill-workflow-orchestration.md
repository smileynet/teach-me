---
id: "088"
title: "Feature: skill workflow orchestration — subagent pipeline for lesson generation"
status: done
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

A **lesson generation workflow** that chains skills as subagent stages in a pipeline, with **parallel fan-out** for research and verification:

```
┌─ PARALLEL: Research ─────────────────────────────┐
│  subagent: domain research (web search + sources) │
│  subagent: prior art scan (existing lessons/maps) │
│  subagent: resource verification (URL checks)     │
└──────────────────────────────────────────────────┘
         │ (all return → synthesize in main context)
         ▼
┌─ SEQUENTIAL: Generate ───────────────────────────┐
│  teach (generate lesson HTML)                     │
│  generate-reference (companion doc)               │
│  generate-quiz-page (from SR questions)           │
└──────────────────────────────────────────────────┘
         │
         ▼
┌─ PARALLEL: Post-process ─────────────────────────┐
│  subagent: jargon annotation                      │
│  subagent: SVG variable migration check           │
│  subagent: SR question quality check              │
└──────────────────────────────────────────────────┘
         │ (all return → collect results)
         ▼
┌─ PARALLEL: Verify ───────────────────────────────┐
│  subagent: mise run verify (links + lint)         │
│  subagent: Playwright visual check (dark + light) │
│  subagent: quiz compliance (5+ questions, 3+ types)│
└──────────────────────────────────────────────────┘
         │ (all pass → mark topic complete)
         ▼
     Update MAP.md + regenerate map page
```

### Parallelism Rules

| Phase | Strategy | Why |
|-------|----------|-----|
| **Research** | Fan out (3-4 subagents) | Independent queries, no shared state. Biggest context saver. |
| **Generate** | Sequential | Each step depends on the previous (quiz needs lesson, reference needs lesson) |
| **Post-process** | Fan out (2-3 subagents) | Independent file edits on different files or non-overlapping parts |
| **Verify** | Fan out (2-3 subagents) | Read-only checks, no conflicts. Catches different failure modes. |

### Fan-out Details

**Research phase (always parallel):**
- Agent 1: Web search for domain knowledge (concepts, facts, sources)
- Agent 2: Check existing workspace (what's already taught, what prereqs exist, avoid repetition)
- Agent 3: Verify cited sources are live + extract key claims
- Synthesis happens in main context after all return (cross-reference findings, resolve conflicts)

**Verify phase (always parallel):**
- Agent 1: `mise run verify` (link checker + HTML lint)
- Agent 2: Playwright headless — navigate page, check dark/light mode, confirm interactive elements work
- Agent 3: Structural compliance — check against scaffold checklist (question count, types, sections present)
- Gate: ALL must pass. Any failure blocks the topic from being marked complete.

**Post-process phase (parallel when possible):**
- Jargon annotation: operates on lesson file
- SVG check: operates on lesson file (read-only — just reports)
- SR quality: operates on JSONL (independent file)
- Note: jargon and SVG check touch the same file but jargon adds spans in body text while SVG check only reads — safe to parallelize. If both need to WRITE, serialize them.

### Implementation Options

**Option A: Orchestrator skill (recommended start)**
A new `generate-topic` skill that orchestrates the pipeline with explicit parallel dispatch:

```yaml
name: generate-topic
description: "Generate a complete topic: research → lesson → post-process → verify. Fans out subagents for research and verification."
```

The skill's process section documents:
1. Which stages dispatch subagents (research, post-process, verify)
2. Which stages run sequentially in main context (generate)
3. How to handle partial failures (verify agent fails but lint passes)
4. The gate condition for marking a topic complete

**Option B: Workflow definition file (scale target)**
A `workflows/lesson-generation.yaml` defining stages with `parallel: true`:
```yaml
name: lesson-generation
phases:
  - name: research
    parallel: true
    stages:
      - {role: kiro_default, task: "Search web for {topic} concepts..."}
      - {role: kiro_default, task: "Read workspace for existing coverage..."}
      - {role: browser, task: "Verify source URLs from RESOURCES.md..."}
    gate: all-return  # synthesize after all complete

  - name: generate
    parallel: false
    stages:
      - {skill: teach, output: "lessons/{id}.html"}
      - {skill: teach, mode: reference, output: "reference/{id}.html"}
      - {tool: generate-quiz-page.py, args: [...]}

  - name: post-process
    parallel: true
    stages:
      - {skill: jargon, input: "lessons/{id}.html"}
      - {script: "tools/check-svg-vars.py", input: "lessons/{id}.html"}
      - {tool: "sr:check", scope: "{id}"}

  - name: verify
    parallel: true
    stages:
      - {run: "mise run verify"}
      - {role: browser, task: "Navigate to {url}, check dark/light, quiz interaction"}
      - {script: "tools/check-topic-completeness.py", args: ["--workspace", "{workspace}", "--topic", "{id}"]}
    gate: all-pass  # ALL must pass to proceed

  - name: finalize
    parallel: false
    stages:
      - {action: "mark topic complete in MAP.md"}
      - {tool: generate_map_page.py, args: [...]}
```

**Option C: mise task (tooling-only steps)**
For the subset that's pure tooling (no agent reasoning needed):
```toml
[tasks."topic:post-process"]
run = """
python tools/jargon-annotate.py --file $1 &
python tools/check-svg-vars.py --file $1 &
mise run sr:check -- $(basename $1 .html) &
wait
"""
```
Useful as an inner piece — the parallel shell `&` + `wait` pattern works for tool-only steps. But research and verify need agent reasoning (web search, visual analysis), so they must be subagent dispatch.

### Recommendation

Start with **Option A** (orchestrator skill). It documents the pipeline, dispatches subagents explicitly, needs no new infrastructure. Graduate to **Option B** (workflow YAML) once 2+ workflows follow the same pattern.

### Key Design Decisions

1. **Research is ALWAYS parallel**: Never research sequentially in main context. Fan out 2-4 subagents, synthesize after all return. Biggest context saver.
2. **Verify is ALWAYS parallel**: Different verification angles catch different failures. Run lint, Playwright, and structural checks simultaneously. Gate on all-pass.
3. **Failure handling**: Research — if 1 of 3 returns empty, retry once. Verify — ANY failure blocks topic completion. Post-process — jargon is optional (skippable), quiz is required (blocks).
4. **Idempotency**: Every stage safe to re-run. Jargon overwrites existing spans. Quiz overwrites existing page.
5. **Workspace-awareness**: Every stage receives `--workspace`.
6. **Subagent prompt size**: <1K tokens per dispatch. Data goes in files, not inline (per subagent-reliability steering).
7. **Batch ceiling**: Max 4 subagents per dispatch. Research (3-4) and verify (3) each fit in one batch.

## What to build

1. Create `.kiro/skills/generate-topic/SKILL.md` — orchestrator skill with the 4-phase pipeline
2. Document which phases fan out (research, post-process, verify) and which are sequential (generate)
3. Add `tools/check-topic-completeness.py` — verifies all artifacts exist (lesson, reference, quiz, jargon, SR questions)
4. Add `tools/check-svg-vars.py` — flags hardcoded hex in lesson SVGs
5. Update the `teach` skill to reference `generate-topic` as the complete workflow
6. Test: run against existing topic (should pass) + new topic (should produce all artifacts)

## Acceptance criteria

- [x] `generate-topic` skill exists with 4 documented phases (research, generate, post-process, verify)
- [x] Research phase dispatches 2+ subagents in parallel
- [x] Verify phase dispatches 2+ subagents in parallel (lint + Playwright + structural)
- [x] Running the skill produces: lesson + reference + quiz + jargon + map update
- [x] `check-topic-completeness.py` reports missing artifacts
- [x] Verify gate blocks completion if any check fails
- [x] Sequential phases wait for parallel phases before proceeding

## Resolution (2026-08-12)

TBD
