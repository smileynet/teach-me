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

- [ ] Context at top — why this matters for the mission
- [ ] At least one diagram for conceptual content
- [ ] Claims cited or framed as general
- [ ] Reference doc generated alongside
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

## It's NOT Working If

- Lessons cite no sources (teaching from memory)
- Lessons produced before understanding why the learner cares
- Reference docs read like shorter lessons instead of lookup artifacts
- The learner reads but never explains anything back
