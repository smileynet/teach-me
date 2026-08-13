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
- [ ] lesson-actions.js included with correct data attributes
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

## It's NOT Working If

- Lessons cite no sources (teaching from memory)
- Lessons produced before understanding why the learner cares
- Reference docs read like shorter lessons instead of lookup artifacts
- The learner reads but never explains anything back
