---
name: teach
description: "Teach the user a new skill or concept over multiple sessions, using the current directory as a stateful teaching workspace. Trigger: teach, teach me, learn, I want to learn, help me understand, next lesson."
metadata:
  type: process
  invocation: user-only
  practice: null
---

The user wants to learn something. This is stateful — they intend multiple sessions.

## Teaching Workspace

The current directory is the workspace. State lives in:

- `MISSION.md` — why the learner wants this (grounds everything)
- `RESOURCES.md` — verified sources with trust ratings (populated BEFORE lessons)
- `lessons/*.html` — self-contained HTML lessons (one concept each)
- `reference/*.html` — scannable lookup companions to lessons
- `learning-records/*.md` — demonstrated understanding (drives ZPD)
- `assets/` — shared components (CSS, JS, diagrams)
- `NOTES.md` — learner preferences, working notes

## Workflow

1. **Mission first.** If `MISSION.md` is empty, ask why they're learning this. Don't produce a lesson without a mission.
2. **Research the domain.** Identify 3-6 subtopics, dispatch research, populate RESOURCES.md. See [references/research-methodology.md](./references/research-methodology.md). This is a hard gate — no lesson from parametric memory.
3. **Find the ZPD.** Read learning records, determine what to teach next.
4. **Write the lesson.** One concept, one win. Read the scaffold from `assets/scaffolds/lesson.html` first. Follow [references/lesson-components.md](./references/lesson-components.md) for theming, diagrams, glossary, exercises.
5. **Write the reference doc.** Simultaneously — same authoring pass. Scannable, lookup-oriented.
6. **Generate SR questions.** 3-5 conceptual questions with criteria-based answers. See [references/sr-question-design.md](./references/sr-question-design.md).
7. **Run quality gates.** `mise run sr:check` + the publish checklist below.

## Lesson Shape

- **Opening:** end-state preview → context (why this matters) → teach
- **Tone:** knowledgeable colleague at a whiteboard. Direct, assumes intelligence.
- **Style:** Grade 8-10 reading level. Short paragraphs. Plain words. One clause per sentence max.
- **Claims:** Cited or framed as general. Never invent specific numbers.
- **Visuals:** Every conceptual section has a diagram. Labels ON the diagram.
- **Limitations:** Frame as "What to pursue alongside this" — actionable recommendations, not defensive disclaimers.

## Session Start (new learner)

Detection: No workspace with populated MISSION.md found (all contain template placeholders or don't exist).

This is the first-contact flow. The user opened this project in their AI assistant and either said something vague or asked to learn something.

1. **Orient** (one sentence): "This is a teaching workspace — I research topics, write interactive lessons with diagrams, and help you build lasting understanding through quizzes and spaced repetition. What would you like to learn?"

2. **Elicit mission** (conversational):
   - "What's driving you to learn this?" (grounds everything in a real reason)
   - "What should you be able to DO after learning this?" (defines success)
   - "Any constraints — time pressure, prior knowledge, must-cover areas?"

3. **Scaffold** (automatic): Run `tools/init-workspace.sh --path workspace` (or `examples/{slug}` for demos). Write MISSION.md from their answers.

4. **Offer customization** (brief, don't block):
   - "Before I research, any preferences? Detailed walkthroughs or jump-to-the-point? Lots of diagrams or mostly text?"
   - Write preferences to `NOTES.md` in the workspace
   - If they say "just start" — use defaults (direct, diagrams, dark mode)

5. **Mention the experience ahead**:
   - "I'll research the domain, then break it into a map of 5-7 topics you can explore in any order."
   - "After a lesson or two, I'll offer Socratic review — you explain concepts back and I probe your understanding. It's how we make knowledge stick."
   - "The lessons are interactive HTML pages you open in your browser. I generate them, you read and explore, then come back for quizzes or new material."

6. **Begin**: Dispatch research subagents → generate MAP.md → offer first topic.

## Session Start (returning learner)

1. Run `python tools/sr-status.py` — check if cards are due
2. If due: recommend review (never force). "You have N cards due. Want to review first, or jump to new material?"
3. If learner wants new material: provide it immediately, no friction
4. If learner wants review: surface 2-3 cards conversationally, record quality

## Philosophy

Three kinds of learning:
- **Knowledge** — from researched, trusted resources (never parametric memory)
- **Skills** — from practice with tight feedback loops
- **Wisdom** — from communities and real-world application (delegate, don't simulate)

Build **storage strength** (long-term retention) not just fluency (in-the-moment recall). Use retrieval practice, spacing, interleaving.

## Reference Documents

Produce alongside every lesson. The reference is what the learner pulls up at work — not a summary but the conceptual model + facts in lookup form. A colleague who never read the lesson should understand the core concept from the reference alone.

## Before Publishing

Pre-flight gate — check BEFORE presenting the lesson to the user:

- [ ] SVG diagram present with `var(--svg-*)` colors (no hardcoded hex)
- [ ] glossary-data JSON block with 3+ defined terms
- [ ] 3+ source citations (specific URLs, not generic base paths)
- [ ] Exercise with `<details>` hint AND criteria-based answer
- [ ] page-shell.js included as single module script
- [ ] Reference doc written alongside

Full checklist (verify after user accepts):

- [ ] Context at top — why this matters for the mission
- [ ] Claims cited or framed as general
- [ ] SR questions generated (3-5, criteria-based)
- [ ] `mise run sr:check` passes
- [ ] "What's Next" section present

## It's Working If

- RESOURCES.md fills before lessons do; lessons cite sources
- A lesson leaves the learner able to explain one thing they couldn't before
- Reference docs are pulled up at work and help
- Learning records grow; lessons stop re-teaching demonstrated knowledge
- Lessons look like one course (shared theme, consistent visual language)

## Complete Topic Generation

For the full pipeline (research → lesson → jargon → quiz → reference → verify), use the `generate-topic` skill. It wraps this skill with parallel subagent dispatch for research and verification, ensuring all post-processing steps happen automatically. Use `generate-topic` when you want guaranteed completeness; use `teach` directly for quick drafts or interactive teaching sessions.

## Multi-Source Enrichment

When generating or regenerating a lesson for a topic that has enrichment data, read `sources/{domain}/enrichments.json`. This overlay records matches from additional sources ingested after the original.

**What to do with it:**

1. **Check for matches** — if the current topic slug appears in any enrichment record's `matches[]`, that topic has additional source material.
2. **Per-claim source badges** — weave claims from the new source into the lesson with clear attribution: "According to [Source B]..." or a margin badge.
3. **Typed conflict callouts** — when `conflict_type` is not `"complementary"`, render a callout:
   - `factual`: "Sources disagree: Source A says X, Source B says Y"
   - `outdated`: "Updated: Source B (2025) reports Y, superseding Source A's figure of X"
   - `opinion`: "Different perspective: Source B argues Y, while Source A takes the position that X"
4. **Corroboration prompt** — after a conflict callout, add a brief question: "Why might these sources differ?" This triggers deeper processing (DISC hypothesis).
5. **New topics** — if `new_topics_proposed` contains entries, mention them in the lesson's "What's Next" section as available subtopics from the additional source.

**What NOT to do:**
- Don't remove or rewrite existing content from the original source
- Don't silently choose one source over another — surface both
- Don't present every match as a conflict — `"complementary"` means the new source adds depth, not contradiction

## It's NOT Working If

- Lessons cite no sources (teaching from memory)
- Lessons produced before understanding why the learner cares
- Reference docs read like shorter lessons instead of lookup artifacts
- The learner reads but never explains anything back

## Zoom Navigation (Sub-Maps)

When the learner wants to go deeper on a topic, use recursive sub-maps.

### Map Generation Rules (all maps)

These apply every time you generate or edit a MAP.md:

1. **Natural branching** — prereqs express genuine dependencies. If two topics can be learned in parallel, don't chain them. The DAG branches and converges based on actual knowledge dependencies.
2. **No scope markers** — don't include `scope:` fields. The learner doesn't need effort estimates.
3. **leads_to needs descriptions** — every `leads_to` item has a `slug` and a `why` (one sentence). Bare slugs are useless to the learner.
4. **leads_to renders as buttons** — each one is actionable with a description of what it opens up.
5. **Generation is live** — "Generate this topic" buttons hit `/api/generate` and stream progress via SSE. Never show copy-paste commands.
6. **"Explore subtopics"** — the button for drilling into a sub-map. Not "Zoom in" (unclear to users).

### Trigger Phrases

| Phrase | Action |
|--------|--------|
| "zoom in on [X]" / "go deeper on [X]" / "more about [X]" | Generate or load subtopic MAP.md |
| "zoom out" / "big picture" / "go back" | Navigate to parent MAP.md |
| "show me the map" | Re-present current MAP.md |

### Zoom In Flow

1. Identify which topic slug the learner means (fuzzy match against current map's topics)
2. Check: does a child MAP.md exist? (`find_child_map` from `tools/map_parser.py`)
   - **Yes:** Load it, present its orientation, offer first topic
   - **No:** Research that subtopic space, generate a sub-MAP.md (3-5 topics), generate its map page
3. Sub-MAP.md requirements:
   - `depth:` = parent depth + 1
   - `parent:` = parent's domain name
   - 3-5 focused subtopics (fewer than a root map)
   - Same format as any MAP.md (frontmatter + orientation + topics)
4. After generating: run `python3 tools/generate_map_page.py <new-map> --workspace <ws> --output <ws>/lessons/<domain>-map.html`
5. Regenerate parent map page so its topic card shows the direct zoom link

### Zoom Out Flow

1. Read current MAP.md's `parent` field
2. Find and load the parent MAP.md (`get_parent_map` from `tools/map_parser.py`)
3. Present the parent's orientation and topic list

### Depth Limit

Maximum depth is 3 (constant `MAX_DEPTH` in `tools/map_parser.py`). At depth 3:
- Do NOT generate another sub-map
- Instead suggest external resources: official docs, books, courses, or papers
- Frame as: "This is deep enough for exploration — here's where to go for mastery"

### File Naming

Maps live flat in `workspace/maps/`:
```
data-analytics.MAP.md              # depth 0
storage-and-table-formats.MAP.md   # depth 1 (child of a data-analytics topic)
object-storage-fundamentals.MAP.md # depth 2 (child of a storage topic)
```

The `parent:` frontmatter field is the link back up. No `--` separators needed at depth 1-2 unless there's a slug collision.
