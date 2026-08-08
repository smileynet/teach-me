---
id: "018"
title: "Research: GDQuest vault pedagogical analysis"
status: done
priority: medium
blocked_by: []
type: research
---

# Research: GDQuest vault pedagogical analysis

## Context

We have the full GDQuest paid course vault indexed at `~/code/gdquest-vault` — 3 courses (Learn 2D, Learn 3D, Node Essentials), 243 lessons, 140+ concept entries. GDQuest is considered best-in-class for teaching gamedev to beginners/intermediates. Their teaching approach has observable, extractable patterns that could inform teach-me's lesson design.

## Questions to investigate

### Teaching style & tone
- What reading level / sentence complexity do they target?
- How do they balance precision (correct CS terminology) with accessibility (plain language)?
- How much personality/humor vs clinical instruction?
- What's the ratio of "do this" (imperative) to "here's why" (explanatory)?

### Pedagogical structure
- How do lessons scaffold (what comes before what)?
- What's the pattern for introducing a new concept (observe → name → use → practice)?
- How do they handle the "curse of knowledge" — what do they explicitly NOT assume?
- How do they use repetition and callbacks to earlier lessons?
- What role do "collapsible deep dives" play (optional advanced content)?

### Problem-first teaching
- How consistently do they show the problem before the solution?
- What patterns do they use to make the learner "feel the pain" (spaghetti code, manual repetition)?
- How do they transition from "this is broken" to "here's the pattern that fixes it"?

### Code presentation
- How much code per lesson? What's the max block size?
- Do they show diffs, full files, or incremental additions?
- How do they mark "you write this" vs "this was already here"?
- How do they handle the tension between "show complete code" and "focus on what changed"?

### Visual/interactive elements
- What types of diagrams appear and when (state diagrams, scene trees, flowcharts)?
- How are screenshots/videos integrated with text?
- What interactive elements exist (embedded game views, quizzes, try-it-yourself prompts)?

### Assessment & retention
- How do they check understanding mid-lesson?
- What's the "Try Answering This" pattern — frequency, difficulty, format?
- Do they use spaced repetition or review mechanisms?

## Sources to analyze

- Course lesson files in `~/code/gdquest-vault/courses/` (sample 5-8 lessons across difficulty levels)
- Concept glossary files in `~/code/gdquest-vault/concepts/` (sample 5-10 entries)
- `~/code/gdquest-vault/STYLE.md` for their own articulated style guide
- The course intro/pedagogy lessons (e.g., `l2d-introduction-our-teaching-approach.md`, `l2d-introduction-how-to-stay-productive.md`)

## Output

Write findings to `~/code/teach-me/.scratch/research/gdquest-pedagogy.md` with:
1. Style guide extraction (tone, reading level, conventions)
2. Structural patterns (lesson anatomy, scaffolding rules)
3. Specific techniques with examples (problem-first, code diffs, interactive checkpoints)
4. Applicability assessment — what transfers to teach-me's HTML-lesson format, what doesn't
5. Recommendations for teach-me lesson authoring guidelines
