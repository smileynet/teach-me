---
id: "370"
title: "Action bar offers to generate the quiz you are already taking"
status: open
blocked_by: []
tags: ["ux", "components", "quiz"]
---

# Action bar offers to generate the quiz you are already taking

## Intent

The lesson action bar should never advertise generating a quiz that the learner is
already on, and nested pages (quiz/, review/) should not log spurious 404 probes.

## Context (verified 2026-09-17, UX audit + source check)

`assets/components/LessonActions.js:26` builds `quizUrl = 'quiz/' + lessonId +
'-quiz.html'` relative to the CURRENT page URL. On a quiz page the URL-derived
lessonId is already the quiz filename, so the probe fetches
`/lessons/quiz/quiz/0001-...-quiz-quiz.html` → 404 → `quizExists=false` → the bar
renders "+ Generate quiz" on top of the quiz the learner is taking, plus a console
404. Same doubled-path probe observed on the quick-check page
(`/lessons/review/quiz/quick-check-quiz.html`).

Fix direction: derive the probe from the page's declared lesson context (the
`lesson-actions-config` island already carries lessonId/domain from the template —
use it instead of the URL), and skip the quiz affordance entirely on quiz/quick-check
pages (the template knows which page type it is rendering).

## Acceptance criteria

- [ ] Quiz pages show no "Generate quiz" affordance for their own quiz (and no doubled `quiz/quiz/` probe in the console)
- [ ] Quick-check pages likewise
- [ ] Lesson pages keep the correct Take quiz / Generate quiz behavior (probe resolves as today)
- [ ] `mise run verify` exits 0; interactive checks stay green
