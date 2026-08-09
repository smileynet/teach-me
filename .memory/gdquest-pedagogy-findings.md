# GDQuest Pedagogical Analysis — Synthesis

Research for ticket 018. Sources: 4 subagent analyses covering style, structure, code presentation, and assessment across 15+ GDQuest lesson files + 6 concept entries.

## Executive Summary

GDQuest's teaching is effective because of three core principles:
1. **Show the problem before the solution** — make the learner feel the gap
2. **Action first, explanation optional** — do → see result → understand why (in that order)
3. **Scaffolding that removes itself** — hand-hold early, withdraw explicitly later

Their approach is transferable to our HTML-lesson format. Key techniques we should adopt are below.

---

## Techniques to Adopt in teach-me

### 1. Problem-First Opening (high impact)

Every lesson should open with the pain, not the solution. Patterns:
- "You can do X, but what about Y?" (gap between current state and need)
- Show the broken/limited result BEFORE showing the fix
- One concrete example of the problem (not abstract description)

**For teach-me:** Start each lesson with "Here's what doesn't work yet" before "Here's how it works."

### 2. Show the Result First (high impact)

Before any explanation, show what the learner will achieve by the end. GDQuest uses video; we can use a diagram or a key-concept callout showing the end state.

**For teach-me:** Add a "What you'll be able to explain/do after this lesson" visual near the top.

### 3. Expandable Deep Dives (medium impact)

Core content stays short and action-oriented. Deeper "why" explanations go in collapsible sections. This respects two audiences: the learner who wants to move forward, and the one who wants depth.

**For teach-me:** Add a `<details>` pattern for optional depth. Document in the teach skill.

### 4. Explicit Callbacks (medium impact)

When a concept from lesson N reappears in lesson N+5, explicitly name it: "Remember from Lesson 1: snapshots are frozen views of file state." Don't assume the learner retained it.

**For teach-me:** The teach skill should cross-reference prior learning records when introducing related concepts.

### 5. Three-Tier Assessment (medium impact)

1. Inline quiz (comprehension) — already have this via quiz component
2. "Try it yourself" challenges — not yet implemented
3. Synthesis projects — out of scope currently

**For teach-me:** Add a challenge/exercise pattern (describe the task, progressive hints, then solution).

### 6. Expandable Reminders for Prior Knowledge (medium impact)

In later lessons, wrap previously-taught procedures in `<details>`:
```html
<details><summary>How does a manifest list work? (reminder)</summary>
One sentence refresher from lesson 1.
</details>
```

**For teach-me:** Teach skill should use this when referencing concepts from 2+ lessons ago.

### 7. Definition Through Usage (style)

Never define a term formally first. Show it in action, then name it. "Iceberg creates a new snapshot — a frozen view of the file set — on every write." The definition is embedded in the first use.

**For teach-me:** Already doing this with the jargon skill's inline definitions. Reinforces the approach.

### 8. Reading Level Target

Grade 8-10 English. Sentences 15-20 words. No subordinate clause stacking. Single-sentence paragraphs for emphasis. Non-native speaker friendly.

**For teach-me:** Add to teach skill as a writing constraint.

---

## Techniques to Skip (don't apply to our context)

| GDQuest technique | Why skip |
|-------------------|----------|
| Video demonstrations | Our format is HTML text + SVG. No video pipeline. |
| Interactive code practices (in-editor) | We teach concepts, not a specific tool's editor |
| File-system navigation instructions | Our learners aren't in an IDE |
| Avatar-signed asides | One teacher voice is simpler for agents |
| Platform-rendered quizzes (click-to-reveal answers) | Our quiz component handles this differently |

---

## Recommendations for teach Skill Updates

1. **Add "Problem Opening" to lesson template** — every lesson must state what's broken/missing before explaining the solution
2. **Add "End State Preview" after the lesson-meta** — diagram or one-liner showing what the learner will be able to do
3. **Document `<details>` pattern** for optional deep dives and prior-knowledge reminders
4. **Add reading level constraint** — Grade 8-10, 15-20 words/sentence, no idioms
5. **Add challenge/exercise pattern** — describe task, progressive `<details>` hints, then solution
6. **Cross-reference learning records** — when a concept from a prior lesson reappears, name it explicitly

---

## Coverage Assessment

- ✅ Teaching style & tone — fully extracted
- ✅ Pedagogical structure — fully extracted
- ✅ Code presentation — fully extracted (less relevant for our non-code-editor context)
- ✅ Assessment & retention — fully extracted
- ⚠️ Visual/interactive elements — partially covered (their visuals are screenshots/video, less relevant)
- ✅ Problem-first teaching — deeply extracted with specific patterns
