---
id: "012"
title: "Feature: clickable inline glossary component"
status: done
priority: high
blocked_by: []
type: feature
---

# Feature: clickable inline glossary component

## What to build

A lightweight JS component that turns marked-up terms in lessons into clickable tooltips showing definitions from the workspace glossary. Lets learners refresh on terminology without asking full questions or leaving the lesson.

## Design

### In-lesson markup

```html
<span class="term" data-def="A complete set of data files visible at a point in time. Created on every write.">snapshot</span>
```

Or, for terms defined in GLOSSARY.md, reference by term name:

```html
<span class="term" data-term="snapshot">snapshot</span>
```

### Behavior

- Terms appear with a subtle underline (dotted, muted color)
- Click or hover → tooltip/popover with the definition
- Tooltip includes a "📖 See glossary" link to the reference doc if one exists
- Mobile: tap to show, tap elsewhere to dismiss
- Keyboard: focusable, shows on Enter/Space

### Where definitions come from

1. **Inline** (`data-def="..."`) — for one-off terms specific to this lesson
2. **Glossary reference** (`data-term="..."`) — looks up from a `<script type="application/json" id="glossary-data">` block at the bottom of the lesson (generated from GLOSSARY.md)

### Agent workflow

When writing a lesson, the teach skill should:
1. Identify terms the learner may not know (from GLOSSARY.md or new this lesson)
2. Wrap them in `<span class="term">` on first use
3. Include definitions inline or in the glossary JSON block
4. Add new terms to GLOSSARY.md after the lesson

## Acceptance criteria

- [x] `assets/glossary.js` + `assets/glossary.css` created
- [x] Click/hover shows definition tooltip
- [x] Works with both inline `data-def` and referenced `data-term`
- [x] Keyboard accessible (focusable, shows on Enter)
- [x] Dismisses on click-outside or Escape
- [x] Visually subtle (doesn't distract from lesson flow)
- [x] < 80 lines JS, < 40 lines CSS
- [x] Works with existing style.css
