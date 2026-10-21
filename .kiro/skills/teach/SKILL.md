---
name: teach
description: "Teach the user a new skill or concept over multiple sessions, using the current directory as a stateful teaching workspace. Trigger: teach, teach me, learn, I want to learn, help me understand, next lesson."
metadata:
  type: process
  invocation: user-only
  practice: null
---

The user wants to learn something. This is stateful — they intend multiple sessions.

## Ownership & Routing

`teach` is the **conversational learning engine**. It owns the live relationship with the
learner; `generate-topic` owns the durable artifact assembly line. The two never both drive
the same request.

**`teach` owns:**
- First-contact orientation and mission elicitation (`.user/learner-profile.md`)
- Finding the ZPD and deciding *what* to teach next
- Interactive teaching: re-explanation of existing material, Socratic follow-ups, zoom navigation
- Quick single-lesson drafts during a live session (no completeness guarantee)
- The map (MAP.md) as the curriculum spine
- Learner-state reads/writes (under `.user/` only)

**`teach` does NOT own (hand off, don't duplicate):**
- The durable authoring sequence (research → lesson → reference → SR → quiz → verify). That
  procedure has a single owner: the `generate-topic` **Phase 2 pipeline**. When `teach` needs
  a complete, verified, tracked artifact, it invokes `generate-topic` rather than re-running
  the steps itself.
- SR-question structure — owned by
  [generate-topic/references/sr-question-authoring.md](../generate-topic/references/sr-question-authoring.md).
- Exercise design and the callout/decision hierarchy — owned by `visual-teaching.md`.
- Retention quizzing of already-taught material — owned by `quiz-me`.

**Hand off to `generate-topic` when:** the learner names a topic to learn, asks for a new
lesson, or asks to "complete" / fill gaps on an existing topic — anything that must produce a
durable, verified artifact. Hand off to `quiz-me` when the learner wants to be tested on what
they already learned.

**Keep in `teach` when:** the learner is mid-conversation and needs a concept re-explained
("wait, what?"), wants orientation ("show me the map", "where do I start?"), is setting up
their mission/preferences, or explicitly wants a throwaway draft inside the current session.

See the routing table in [#routing-table](#routing-table) for how specific prompts resolve.

## Teaching Workspace

The workspace separates shareable curriculum from private learner state:

- `RESOURCES.md` — verified sources with trust ratings (populated BEFORE lessons)
- `lessons/*.html` — self-contained HTML lessons (one concept each)
- `reference/*.html` — scannable lookup companions to lessons
- `assets/` — shared components (CSS, JS, diagrams)
- `.user/learner-profile.md` — mission, pace, preferences, working notes, and demonstrated understanding
- `.user/learning-records/` — private quiz and SR outcomes

Never write learner-specific state to committed paths such as `MISSION.md`, `NOTES.md`,
or `learning-records/`. Curriculum, sources, maps, and lesson assets remain shareable.

## Workflow

The live-session loop. Steps 1-3 are `teach`'s own; step 4 hands the durable authoring off to
the single owner.

1. **Mission first.** Read `.user/learner-profile.md`; if it has no mission, check whether a legacy `MISSION.md` carries a real mission (a pre-#361 workspace the scaffolder hasn't backfilled) and migrate it into the profile — leave `MISSION.md` untouched; otherwise ask why they're learning this. Don't produce a lesson without a mission.
2. **Research the domain.** Identify 3-6 subtopics, dispatch research, populate RESOURCES.md. See [references/research-methodology.md](./references/research-methodology.md). This is a hard gate — no lesson from parametric memory.
3. **Find the ZPD.** Read `.user/learning-records/`, determine what to teach next.
4. **Author the topic.** Hand off to the `generate-topic` **Phase 2 pipeline** — the single
   owner of the durable authoring sequence (lesson → reference → SR questions → quiz → code
   extraction → verify). Do NOT re-run those steps from a parallel checklist here; that
   caused duplicate, drifting instructions. The only exception is a **throwaway in-session
   draft** the learner explicitly asks for and that will not be tracked — write it directly
   following [references/lesson-components.md](./references/lesson-components.md) and the
   Lesson Shape below, and skip the completeness gate.

Everything below (Lesson Shape, Reference Documents, publish gates) describes the *qualities*
`generate-topic` must honor when it authors on `teach`'s behalf — it is teach's statement of
intent, not a second copy of the pipeline.

## Lesson Shape

- **Opening:** end-state preview → context (why this matters) → teach
- **Tone:** knowledgeable colleague at a whiteboard. Direct, assumes intelligence.
- **Style:** Grade 8-10 reading level. Short paragraphs. Plain words. One clause per sentence max.
- **Claims:** Cited or framed as general. Never invent specific numbers.
- **Visuals:** Every conceptual section has a diagram. Labels ON the diagram.
- **Limitations:** Frame as "What to pursue alongside this" — actionable recommendations, not defensive disclaimers.

## Session Start (new learner)

Detection: no workspace with `.user/learner-profile.md` containing a mission.

This is the first-contact flow. The user opened this project in their AI assistant and either said something vague or asked to learn something.

1. **Orient** (one sentence): "This is a teaching workspace — I research topics, write interactive lessons with diagrams, and help you build lasting understanding through quizzes and spaced repetition. What would you like to learn?"

2. **Elicit mission** (conversational):
   - "What's driving you to learn this?" (grounds everything in a real reason)
   - "What should you be able to DO after learning this?" (defines success)
   - "Any constraints — time pressure, prior knowledge, must-cover areas?"

3. **Scaffold** (automatic): Run `python tools/init_workspace.py --default` for a personal workspace. If the selected workspace is missing, diagnose it and scaffold it before writing state. Write the mission to `.user/learner-profile.md`.

4. **Offer customization** (brief, don't block):
   - "Before I research, any preferences? Detailed walkthroughs or jump-to-the-point? Lots of diagrams or mostly text?"
   - Write preferences to `.user/learner-profile.md` in the workspace
   - If they say "just start" — use defaults (direct, diagrams, dark mode)

5. **Mention the experience ahead**:
   - "I'll research the domain, then break it into a map of 5-7 topics you can explore in any order."
   - "After a lesson or two, I'll offer Socratic review — you explain concepts back and I probe your understanding. It's how we make knowledge stick."
   - "The lessons are interactive HTML pages you open in your browser. I generate them, you read and explore, then come back for quizzes or new material."

6. **Begin**: Dispatch research subagents → generate MAP.md → offer first topic. When the
   learner picks a topic, hand it to `generate-topic` to author (teach owns the pick, not the
   pipeline).

> **The MAP is a DAG, not a line.** Topics connect by `prereqs` edges — a topic whose
> mechanism differs from its neighbor (different shader, different concept) is a SEPARATE
> node hanging off its true conceptual prereq, NOT a linear child of the previous lesson.
> (E.g. the ramp lesson branches off `toon-banding`, not off `toon-control-maps`, because
> a ramp is an alternative banding mechanism — established #246, 2026-08-28.) Don't force a
> linear spine; let prereq edges express the real graph.

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

This is `teach`'s **acceptance contract** — the qualities any durable lesson must have. When
`generate-topic` authors on teach's behalf, its verify phase enforces these; this list is what
"done" means, not a second procedure. A throwaway in-session draft is exempt from the full
checklist (it is explicitly not tracked), but should still carry the pre-flight items.

Pre-flight gate — check BEFORE presenting the lesson to the user:

- [ ] SVG diagram present with `var(--svg-*)` colors (no hardcoded hex)
- [ ] glossary-data JSON block with 3+ defined terms
- [ ] 3+ source citations (specific URLs, not generic base paths)
- [ ] Exercise with `<details>` hint AND criteria-based answer — must test the lesson's Win statement (core concept application, not gotchas or detail recall)
- [ ] page-shell.js included as single module script
- [ ] Reference doc written alongside

Full checklist (verify after user accepts):

- [ ] Context at top — why this matters for the mission
- [ ] Claims cited or framed as general
- [ ] SR questions generated (per [references/sr-question-design.md](./references/sr-question-design.md), which defers to the single owner)
- [ ] `mise run sr:check` passes
- [ ] "What's Next" section present
- [ ] Code/story artifacts validated via the track's toolchain. For Ink lessons, that's the Ink validation contract — see `.kiro/steering/ink-authoring.md` → "The validation pipeline" (commands, prerequisites, skip/fail behavior).

## It's Working If

- RESOURCES.md fills before lessons do; lessons cite sources
- A lesson leaves the learner able to explain one thing they couldn't before
- Reference docs are pulled up at work and help
- Learning records grow; lessons stop re-teaching demonstrated knowledge
- Lessons look like one course (shared theme, consistent visual language)

## Complete Topic Generation

The durable authoring pipeline (research → lesson → jargon → quiz → reference → verify) is
owned by the `generate-topic` skill — it is the single source of truth for that sequence.
`teach` invokes it; it does not re-implement it. Use `generate-topic` whenever the learner
needs a tracked, verified artifact (a new topic, or "completing"/filling gaps on an existing
one). Author directly in `teach` **only** for an explicit throwaway draft inside a live
session — that path trades the completeness gate for speed and produces nothing tracked.

<a id="routing-table"></a>
### Routing table

Equivalent requests resolve to exactly one owner:

| Learner says | Owner | Why |
|--------------|-------|-----|
| "Teach me X" / "I want to learn X" (new) | `generate-topic` | Durable topic needs the verified pipeline |
| "Give me a lesson on X" / "generate a lesson" | `generate-topic` | Durable artifact |
| "Complete this topic" / "fill the gaps on X" | `generate-topic` | Audit/rewrite is a pipeline run |
| "Next lesson" (advancing the map) | `teach` → hands to `generate-topic` | teach picks the ZPD node, generate-topic authors it |
| "Show me the map" / "where do I start?" | `teach` | Orientation, no authoring |
| "Zoom in / go deeper on X" | `teach` | Navigation; authors the sub-map, then hands topic authoring to `generate-topic` |
| "Wait, what?" / "I don't get X" | `teach` (or `wait-what`) | Re-explanation of existing material |
| "Quiz me" / "test me on X" | `quiz-me` | Retention check, not authoring |
| "Just give me a quick draft, don't track it" | `teach` (draft path) | Explicit throwaway, gate skipped |

The rule when two could plausibly match: **if the request must produce a durable, verified
artifact, `generate-topic` owns it; if it is conversation, orientation, or re-explanation,
`teach` owns it.**

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
5. **Generation is honest, not automatic** — a topic with a lesson shows an "Open lesson" link; one without shows "Generate this topic", which reveals the exact prompt to run with an agent in this repo (no server-side autogeneration). Same for quiz buttons (#317/#319).
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
