---
id: "157"
title: "Adopt diff-style code presentation in lessons"
status: open
priority: medium
blocked_by: []
---

# Adopt Diff-Style Code Presentation in Lessons

## Context

When lessons show incremental modifications to existing code, showing only the new code block without context leaves learners confused about:
1. Whether this is a new file or a modification of the existing one
2. Which lines to add/remove vs which are unchanged context
3. Where in the file the changes go

Discovered during gdhelper-pipeline shader lessons: a learner copied a code snippet thinking it was a standalone file, when it was meant to replace specific lines.

## What to Adopt

When a lesson asks the learner to modify existing code, use a **diff-style presentation**:

```html
<pre><code> // unchanged context lines (leading space)
<span style="color:var(--error)">-// removed lines (red, minus prefix)</span>
<span style="color:var(--success)">+// added lines (green, plus prefix)</span>
 // more unchanged context</code></pre>
```

### Rules

1. **Always state which file** before the code block: "Modify your same `filename.ext`:" or "Create a new file `filename.ext`:"
2. **Use diff format for modifications** — red (removed), green (added), plain (context)
3. **Use plain code blocks for new files** — no diff markers, just the complete content
4. **Show 1-2 context lines** around changes so the learner can locate them
5. **Never show a partial snippet** without saying whether it replaces something or is additive

### CSS Variables

Use the existing theme variables:
- Removed: `color: var(--error)` (red/pink)
- Added: `color: var(--success)` (green)
- Context: default text color

## Acceptance Criteria

- [ ] Convention documented in lesson scaffold or teaching guidelines
- [ ] Existing lessons (gdhelper-pipeline shader track) already use this pattern as example
- [ ] New lesson generation follows this pattern when showing modifications
