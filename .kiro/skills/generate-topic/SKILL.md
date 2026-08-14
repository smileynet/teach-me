---
name: generate-topic
description: "Generate a complete topic: research → lesson → post-process → verify. Fans out subagents for research and verification. Trigger: generate topic, generate lesson, complete topic, full generation."
metadata:
  type: process
  invocation: both
  practice: null
---

# Generate Topic

Orchestrates the full lesson generation pipeline for one topic. Ensures every downstream step (jargon, quiz, reference, SVG theming, verification) actually happens — not just the lesson writing.

## When to use

- Generating a new topic from a MAP.md
- "Completing" an existing topic that's missing artifacts (run against it to fill gaps)
- Any time you want the full pipeline, not just a quick lesson draft

## Input

- A workspace path (e.g., `examples/oidc-rust`)
- A topic slug from the workspace's MAP.md (e.g., `token-validation-middleware`)
- The topic's prereqs should already be complete

## The Pipeline (4 Phases)

### Phase 1: Research (PARALLEL — fan out 2-4 subagents)

Dispatch simultaneously:

| Agent | Task | Output |
|-------|------|--------|
| Domain research | Web search for topic concepts, key facts, 3+ sources | `.scratch/research/{slug}.md` |
| Workspace context | Read MAP.md, existing lessons, RESOURCES.md — what's taught, what prereqs cover, avoid repetition | `.scratch/research/{slug}-context.md` |
| Source verification | Check top URLs from RESOURCES.md are live, extract key claims relevant to this topic | `.scratch/research/{slug}-sources.md` |

**After all return:** Synthesize in main context. Resolve conflicts between sources. Determine: what to teach, what to cite, what the learner already knows from prereqs.

**Failure handling:** If 1 of 3 returns empty, retry once. If still empty after retry, proceed with available research (note the gap).

### Phase 2: Generate (SEQUENTIAL — main context)

**Before writing:** Check the topic's current status in MAP.md. If it's `complete`, this is a **rewrite**:
1. Reset status to `in-progress` via `map_parser.update_status(map_path, slug, "in-progress")`
2. Delete the existing quiz page for this topic (will be regenerated below)
3. Remove existing SR questions for this topic from the domain JSONL (filter out lines where `"topic": "{slug}"`)
4. Regenerate the map page (reflects the status change immediately)
5. Inform the user: "Topic was complete — reset to in-progress for rewrite. Mark complete again once you've reviewed the new lesson."

**Note:** The pipeline does NOT auto-mark the topic complete after generation. The user marks it complete themselves (via the lesson page button) after reviewing the rewritten content.

Each step depends on the previous:

1. **Read the scaffold** — `assets/scaffolds/lesson.html`
2. **Write the lesson** — using synthesized research. Follow teach skill conventions (SVG diagram with CSS vars, citations, key-concept blocks, exercise with hint + answer).
3. **Write the reference doc** — read `assets/scaffolds/reference.html`. Scannable lookup format: Core Concept, factual tables, Decision Aid.
4. **Write SR questions** — append to `learning-records/questions/{domain}.jsonl`. 4-8 questions, criteria-based answers, mix of explain/apply/predict/quick-check types.
5. **Generate quiz page** — `python3 tools/generate-quiz-page.py --workspace {workspace} --lesson-id {slug} --title "{title}" --lesson-file {filename} --map-page {map-page}`

### Phase 3: Post-process (PARALLEL — fan out 2-3 subagents)

Dispatch simultaneously:

| Agent | Task | Blocking? |
|-------|------|-----------|
| Jargon annotation | Read lesson, find glossary-data keys, wrap first use of each term with `<span class="term" data-term="KEY">` | Optional (skip if fails) |
| SVG variable check | `python3 tools/check-svg-vars.py --workspace {workspace}` — report hardcoded hex | Required (fix before verify) |
| SR quality check | `mise run sr:check -- {slug}` — report prompt issues, missing criteria | Optional (report only) |

**After return:** If SVG check found violations, fix them (sed replacement). If jargon returned annotations, apply them.

### Phase 4: Verify (PARALLEL — fan out 2-3 subagents)

Dispatch simultaneously:

| Agent | Role | Gate |
|-------|------|------|
| Link + lint check | `mise run verify` | MUST pass |
| Visual check | Browser: navigate to lesson URL, confirm SVG visible in dark mode, theme toggle works, bottom nav present, glossary tooltips appear | MUST pass |
| Structural compliance | `python3 tools/check-topic-completeness.py --workspace {workspace} --topic {slug}` | MUST pass |

**Gate:** ALL must pass. Any failure blocks the topic from being marked complete.

**After all pass:**
1. Update MAP.md — if this is a **new topic** (was `not-started` or `in-progress` before generation started), set status to `complete` and add `lesson_file:` field. If this is a **rewrite** (was `complete` before, reset to `in-progress` in Phase 2), leave status as `in-progress` — the user marks complete after reviewing.
2. Regenerate map page — `python3 tools/generate_map_page.py {map.MAP.md} --workspace {workspace} --output {workspace}/lessons/{domain}-map.html`
3. Regenerate index — `python3 tools/generate_index_page.py --scan-dir examples`

## Running Against Existing Topics

The pipeline handles existing topics differently based on whether content changes:

**Verification-only (no `--force`, files exist):**
- Research phase: skips (or refreshes if sources are stale)
- Generate phase: skips (files exist, no content change)
- Post-process phase: re-checks (jargon overwrites existing spans safely)
- Verify phase: always runs (confirms current state is compliant)
- **Status: NOT reset** — no content changed, no reason to un-complete

**Rewrite (`--force` or user explicitly asks to regenerate):**
- Status resets to `in-progress` at the start of Phase 2
- Old quiz page and SR questions for this topic are deleted
- Full generation runs (new lesson, ref, quiz, SR)
- Status remains `in-progress` after pipeline completes
- **User marks complete** after reviewing the new content

This is how you audit existing content: `generate-topic --workspace X --topic Y` should pass silently if everything is correct. To rewrite: ask to regenerate or use `--force`.

## Multiple Topics

**Topics generate sequentially, one at a time.** Each topic completes the full 4-phase pipeline before the next begins. This ensures:

1. **No dilution:** Each topic gets full research depth and verification attention
2. **Prereq awareness:** Later topics can reference what earlier ones established
3. **Early failure detection:** A broken topic blocks further generation (don't accumulate debt)
4. **Quality over throughput:** 2 excellent topics > 5 mediocre ones

The parallel fan-out happens WITHIN each topic (research agents, verify agents) — never ACROSS topics. If you need 3 topics generated, that's 3 sequential runs of the full pipeline, not one run with 3 topics batched.

```
Topic 1: research (parallel) → generate → post-process (parallel) → verify (parallel) → ✓ complete
Topic 2: research (parallel) → generate → post-process (parallel) → verify (parallel) → ✓ complete
Topic 3: research (parallel) → generate → post-process (parallel) → verify (parallel) → ✓ complete
```

## Does NOT

- Replace the teach skill (teach is the creative engine; this is the assembly line)
- Add infrastructure (no workflow YAML parser, just a skill document)
- Force the user to use it (teach works standalone for quick lessons)
- Generate content for topics whose prereqs aren't complete
- Mark topics complete without the verify gate passing

## Error Recovery

| Failure | Response |
|---------|----------|
| Research agent returns empty | Retry once. If still empty, proceed with partial research + note gap. |
| Lesson generation produces bad HTML | `mise run verify` catches broken links/structure in Phase 4. |
| Jargon pass corrupts file | Non-blocking. If term count = 0 after annotation, revert to pre-jargon state. |
| Quiz generation fails (no questions) | Blocking. Can't have a quiz without questions. Write questions first, then retry. |
| Verify agent disagrees with lint | Trust the tool output (lint/completeness scripts), not the visual check. Fix what the tool says. |
| Playwright can't connect | Skip visual check, report gap. Other two verify agents still gate. |
