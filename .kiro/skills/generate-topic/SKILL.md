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

**Source-ingested topics:** If `source-chunks/{domain}.json` exists, this topic was derived from a source document. In this case:
- **Skip web research** — the source chunks ARE the research
- Read the chunk(s) matching this topic's heading from the JSON
- Use chunk content as the authoritative source for the lesson
- When writing SR questions, populate `source_section` (chunk heading), `source_page` (chunk page_start), and `source_quote` (exact passage from the chunk content) on every card

**After all return:** Synthesize in main context. Resolve conflicts between sources. Determine: what to teach, what to cite, what the learner already knows from prereqs.

**Concept hints (opt-in):** If `source-chunks/{domain}.json` exists, run:
```
python tools/concept_hints.py source-chunks/{domain}.json --topic {slug} --domain {domain}
```
This produces `.scratch/concepts/{slug}.json` with:
- Ranked candidate glossary terms (use as starting checklist for jargon, not a mandate)
- L-level suggestions per concept (L1=core recall, L2=practice, L3=analysis — informed by foundational-ness score + prerequisite depth)
- Prerequisite edge suggestions (use for "explain why X depends on Y" question framing)

If no source-chunks exist (web-researched topic), skip this step — the agent uses its own judgment for terms and levels.

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

1. **Body content only** — produce ONLY the lesson body (h2 sections, paragraphs, SVGs, tables, exercises). Do NOT write `<!DOCTYPE>`, `<html>`, `<head>`, script tags, or import statements. The `page_template.py` handles all boilerplate.
2. **Write the lesson** — using synthesized research. Follow teach skill conventions (SVG diagram with CSS vars, citations, key-concept blocks, exercise with hint + answer). The exercise tests the lesson's **Win statement** — core concept comprehension, not detail recall or gotchas (see visual-teaching.md § Exercise Design). Call `python3 -c "from tools.lib.page_template import render_lesson_page; ..."` or have the agent write the body to a temp file and wrap with the template.
3. **Write the reference doc** — produce body content only (tables, lists, one-sentence summaries). Wrap with `render_reference_page()` from `tools/lib/page_template.py`.
4. **Write SR questions** — append to `learning-records/questions/{domain}.jsonl`. 4-8 open-answer questions + 2-3 interactive questions per topic.

#### Open-Answer Question Archetypes (use at least 3 different types per topic)

| Archetype | Framing | Tests | When to use |
|-----------|---------|-------|-------------|
| **Explain-why** | "Why does X work this way?" / "Why not Y instead?" | Causal understanding | Core mechanism of the lesson |
| **Scenario** | "You're building X and encounter Y. What do you do?" | Application under constraints | Practical skills, decision-making |
| **Predict** | "If you change X, what happens to Y?" | Mental model accuracy | Config, parameters, dependencies |
| **Debug** | "This isn't working: [symptom]. What went wrong?" | Diagnostic reasoning | Common mistakes from the lesson |
| **Teach-back** | "Explain to [specific person] how to..." | Deep synthesis | Integration across concepts |
| **Connect** | "How does X relate to [concept from earlier lesson]?" | Transfer across topics | Cross-topic relationships |

**Do NOT** make all questions the same archetype. Variety of surface form forces genuine understanding vs pattern-matching the lesson text.

#### Criteria Format (REQUIRED — enforced by `sr:check`)

Every open-answer question MUST have a `criteria` field with this structure:

```
"criteria": "Should mention: (1) first key point, (2) second key point, (3) third key point. Bonus: stretch insight that shows deep understanding."
```

Rules:
- 2-4 numbered must-mention points — specific and testable
- 1 bonus point — the "aha" insight that proves deep understanding
- Each point is a *concept to address*, not exact wording to reproduce
- Key insight: identify the ONE sentence that distinguishes understanding from memorization

#### Another Angle (REQUIRED for new questions)

Every open-answer question MUST include an `eli5` field:

```json
{"prompt": "...", "criteria": "...", "eli5": "Think of it like..."}
```

The `eli5` is NOT a simpler version — it's a *different angle*: an analogy, concrete example, or reframing that helps the concept click from a second direction. Shown to the user as "Another angle" alongside the criteria.

#### Provenance & Level Tagging (REQUIRED for new questions — ADR 0007)

**If `.scratch/concepts/{slug}.json` exists**, read it before writing questions:
- Use concept `level` field for the `tags` L-level (L1/L2/L3)
- Prioritize questions on concepts with highest `score` (most foundational)
- Use `edges[].suggestion` for relationship-type questions ("explain why X depends on Y")
- Ensure at least one question per concept above `coverage_target`

If no concept hints file exists, assign L-levels by judgment (as before).

Every open-answer question SHOULD include these fields:

```json
{
  "prompt": "...",
  "criteria": "...",
  "eli5": "...",
  "source_section": "The heading of the lesson section this question tests",
  "source_page": 14,
  "source_quote": "The exact sentence or passage from the lesson that teaches this answer",
  "derivation": "direct",
  "tags": ["L1-core"]
}
```

**`source_section`** — The heading (H2/H3) of the lesson section this card was derived from. Shown in the quiz UI after answering as "📖 From: §source_section".

**`source_page`** — The page number or chunk index from the source document. Shown alongside source_section when available.

**`source_quote`** — The passage from the lesson that teaches what this question tests. Enables re-read routing when the learner fails a card. REQUIRED for `derivation: "direct"` questions; optional for inference/synthesis.

**`derivation`** — How the answer relates to lesson content:
- `"direct"` — answer found in a single passage (cite it in source_quote)
- `"inference"` — requires connecting ideas within the lesson
- `"synthesis"` — spans multiple sections or cross-topic

**`tags`** (level tagging) — cognitive load tier:
- `["L1-core"]` — fundamental concepts, always true, tested first
- `["L2-practice"]` — best practices, usually-true rules, tested after core consolidates
- `["L3-nuance"]` — edge cases, "it depends", mastery-level

Order in JSONL: L1 questions first, then L2, then L3. This is the implicit difficulty progression.

#### Interactive Questions (2-3 per topic)

Include a mix of:
- `"type": "sequence"` — ordering steps/hierarchy (with `items` + `correct_order`)
- `"type": "match"` — connecting terms to definitions (with `pairs`)
- `"type": "fill"` — completing key statements (with `template` + `answers`)

These test recognition and recall; open-answer questions test deeper understanding. Both are needed.

#### Difficulty Progression (implicit, never labeled)

Order questions in the JSONL from recognition → application → synthesis. Don't label difficulty — users feel the progression naturally. First questions should be approachable (explain-why about the core concept); later questions should require combining ideas (connect, predict, debug).
5. **Extract code files** — For each unique `data-file` in the lesson HTML, write the final-state version to `reference/code/{lesson-slug}/`. If a file appears in multiple blocks (complete → diff), assemble the final version by applying diffs in document order. Include a README.md listing each file. Add a "Code Files" section to the lesson body (before "What's Next") with `<a href="..." download>` links. Skip this step if the lesson has no `data-file` blocks.
6. **Update previous lesson's forward link** — If this topic has a prereq that's already complete, find that lesson's "What's Next" section and replace the plain-text topic reference with an `<a href="{new-lesson-filename}">` link. This connects the reading flow so learners can navigate forward without returning to the map.
7. **Generate quiz page** — `python3 tools/generate-quiz-page.py --workspace {workspace} --lesson-id {slug} --title "{title}" --lesson-file {filename} --map-page {map-page} --domain "{domain}" --domain-slug {domain-slug}`

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
