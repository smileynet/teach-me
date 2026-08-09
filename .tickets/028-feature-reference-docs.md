---
id: "028"
title: "Feature: reference docs generated alongside lessons"
status: open
priority: high
blocked_by: []
type: feature
---

# Feature: reference docs generated alongside lessons

## What to build

When the teach skill writes a lesson, it simultaneously generates a companion reference doc in `reference/`. The reference is not a post-processing step — it's part of the same authoring act.

## Design

The lesson teaches (narrative, explanation, diagrams, context). The reference doc is what you pull up at work (compressed, scannable, no narrative).

### Reference doc structure

```
reference/0001-iceberg-metadata-tree.html
├── One-liner summary
├── Key table or diagram (same SVG from lesson, or a simplified version)
├── Decision aids ("when to use / when not to")
├── Quick-reference definitions (terms introduced in this lesson)
└── Link back to full lesson
```

### What belongs in reference vs lesson

| In the lesson | In the reference |
|---------------|-----------------|
| Why this matters | What it is (compressed) |
| The problem it solves | The solution (table/diagram form) |
| Explanation of mechanics | The facts (no explanation) |
| Citations and sources | Just the result |
| Exercises and gates | Nothing interactive |

### In the teach skill

Add to lesson authoring: "When writing a lesson, also produce `reference/NNNN-slug.html` alongside it. The reference uses the same stylesheet but is structured for scanning, not reading."

## Acceptance criteria

- [ ] Teach skill documents reference doc generation as part of lesson authoring
- [ ] Reference doc format defined (scannable, compressed, links back to lesson)
- [ ] Lesson 1 gets a companion reference doc as an example
- [ ] Lessons link to their reference ("Reference: [cheat sheet]")
- [ ] Reference links back to its lesson ("Full explanation: [lesson]")
