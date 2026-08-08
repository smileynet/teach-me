---
id: "014"
title: "Integrate: quiz component best practices"
status: done
priority: medium
blocked_by: []
type: feature
---

# Integrate: quiz component best practices

## Source findings

`.scratch/research/quiz-component-patterns.md` — researched 2026-08-06

Key findings NOT yet integrated:

### Semantic HTML (current quiz uses div soup)
- Should use `<fieldset>` + `<legend>` for question grouping (partially done in JS, but not in source HTML)
- Use `<input type="radio">` + `<label>` (done ✓)
- `aria-live="polite"` on feedback region for screen reader announcements

### Persistence
- localStorage keyed by quiz ID for resumability
- Track per-question history (needed for spaced repetition later — ticket 011)

### Progressive enhancement
- Quiz should degrade gracefully without JS (show all options, no interactivity)
- `<noscript>` fallback message

### Data format
- Consider JSON block in the HTML for machine-readability (helps with ticket 011 spaced repetition)
- Schema: `{id, prompt, options: [{text, explanation, sources, correct}]}`

## What to update

1. **`assets/quiz.js`** — add `aria-live` on feedback, localStorage persistence
2. **`assets/quiz.css`** — ensure color-independent correct/incorrect indicators (add ✓/✗ icons)
3. **Quiz-me skill** — document the JSON data format for programmatic quiz generation
4. **Teach skill** — add noscript fallback guidance when embedding quizzes

## Acceptance criteria

- [x] `aria-live="polite"` on feedback region
- [x] Color-independent indicators (icons, not just color)
- [x] localStorage stores answered state (refresh doesn't reset)
- [x] Noscript fallback documented
