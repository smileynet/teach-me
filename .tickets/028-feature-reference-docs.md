---
id: "028"
title: "Feature: reference docs generated alongside lessons"
status: open
priority: high
blocked_by: []
type: feature
---

# Feature: reference docs generated alongside lessons

## Context

The teach skill currently produces lessons (explanatory, narrative, teach-once artifacts) but no compressed reference docs (scannable, lookup-at-work artifacts). Pocock's teach skill defines both: lessons are rarely revisited, reference docs are. Our learner's JTBD is "understand well enough to architect and advise" — meaning they'll need quick-reference material during actual work (meetings, architecture reviews, writing docs for their customer).

The gap: after reading lesson 1, the learner has no desk artifact to pull up when a colleague asks "wait, what are the five layers again?" They'd have to re-read the full lesson.

## Intent

Reference docs are the bridge between "I learned this" and "I can use this at work." They're generated *alongside* the lesson (not as a separate step) because they're a different *view* of the same knowledge — compressed, not expanded.

## What to build

### 1. Update teach skill

Add to the lesson authoring flow: "When writing a lesson, also produce `reference/NNNN-slug.html`. The reference is a companion artifact — same stylesheet, different structure."

### 2. Define reference doc format

```
reference/0001-iceberg-metadata-tree.html
├── One-liner summary (the "elevator pitch" for this concept)
├── Key visual (same SVG or a simplified version)
├── Facts table (layer → what it stores → where it lives)
├── Decision aid ("when X, do Y" — if applicable)
├── Terms introduced (short definitions, no tooltip needed)
├── Link: "Full explanation → lesson 1"
```

### 3. Produce lesson 1's reference doc as the working example

### 4. Cross-link

- Lesson ends with: "Reference: [Iceberg Metadata Tree →](../reference/0001-...)"
- Reference ends with: "Full lesson: [The Iceberg Metadata Tree →](../lessons/0001-...)"

## What belongs in reference vs lesson

| In the lesson | In the reference |
|---------------|-----------------|
| Why this matters for your mission | What it is (one sentence) |
| The problem it solves | The solution (visual + table) |
| Explanation of mechanics | The facts (no narrative) |
| Citations and sources | Nothing — the lesson has them |
| Exercises and gates | Nothing interactive |
| Collapsible deep dives | Nothing optional — everything here is essential |

## Validation

- [ ] A colleague unfamiliar with the topic can use the reference doc to answer "what are the layers and where do they live?" without reading the lesson
- [ ] The reference doc fits on one screen (no scrolling for the core content)
- [ ] The teach skill generates both artifacts in one pass (not separate invocations)
- [ ] Cross-links work in both directions

## Acceptance criteria

- [ ] Teach skill documents reference doc generation as part of lesson authoring
- [ ] Reference doc format defined with structure guidance
- [ ] Lesson 1 gets a companion reference doc
- [ ] Bidirectional cross-links between lesson and reference
- [ ] Reference doc uses same stylesheet + theme (dark/light toggle works)
