---
id: "006"
title: "Create quiz component for lesson HTML"
status: open
priority: high
blocked_by: []
---

# Create quiz component for lesson HTML

## What to build

A reusable JavaScript quiz component at `assets/quiz.js` + `assets/quiz.css` that the teach skill uses to embed interactive quizzes in HTML lessons. Addresses the known issue from Matt Pocock's skill where correct answers always land in position A.

## Design

- Multiple choice questions rendered as clickable cards
- **Answers are shuffled at render time** (not at generation time) using Fisher-Yates
- Immediate feedback: correct = green + explanation, incorrect = red + hint
- All answer options same visual weight (same length constraint is in the skill, not the component)
- Tracks score for the session (shown at end)
- Accessible: keyboard navigable, ARIA labels

## Data format (in-HTML)

```html
<div class="quiz" data-quiz>
  <div class="quiz-question" data-correct="2">
    <p class="quiz-prompt">What does the manifest file track?</p>
    <div class="quiz-option" data-explanation="Correct! Manifests list data files with per-file column stats.">Data file locations and column-level statistics</div>
    <div class="quiz-option" data-explanation="The catalog stores this, not manifests.">The current metadata file pointer</div>
    <div class="quiz-option" data-explanation="Schema lives in the metadata file, not manifests.">Table schema and partition specs</div>
    <div class="quiz-option" data-explanation="Access control is handled by Lake Formation.">User access permissions</div>
  </div>
</div>
```

## Acceptance criteria

- [ ] `assets/quiz.js` + `assets/quiz.css` created
- [ ] Answers shuffle on page load (position randomized)
- [ ] Immediate feedback on selection
- [ ] Keyboard accessible (tab + enter to select)
- [ ] Works with the teach skill's lesson format
- [ ] Score summary after all questions answered
