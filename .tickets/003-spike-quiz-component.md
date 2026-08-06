---
id: "003"
title: "Spike: interactive quiz component"
status: open
priority: high
blocked_by: []
type: spike
---

# Spike: interactive quiz component

## Question to answer

Can we build a lightweight vanilla JS quiz widget that shuffles answers at render time, provides immediate feedback, and works well in self-contained HTML lesson files?

## Experiment

1. Create `assets/quiz.js` + `assets/quiz.css` (vanilla, no deps)
2. Build a quiz with 3 questions about Iceberg (to test with lesson 1)
3. Requirements:
   - Fisher-Yates shuffle on page load (fixes Matt Pocock's "answer A" bug)
   - Click to select → immediate correct/incorrect feedback with explanation
   - Keyboard accessible (tab + enter)
   - Score shown after last question
4. Test in a standalone HTML page

## Success criteria

- [ ] Answers appear in random order on each page load
- [ ] Immediate feedback (green/red + explanation text)
- [ ] Works with no network requests (fully self-contained)
- [ ] Keyboard navigable
- [ ] Looks good with the existing `assets/style.css`
- [ ] < 100 lines of JS, < 50 lines of CSS

## Output

- `assets/quiz.js` + `assets/quiz.css`
- `lessons/spike-quiz-test.html` — test page (delete after spike)
