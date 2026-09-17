---
id: "370"
title: "Action bar offers to generate the quiz you are already taking"
status: done
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

- [x] Quiz pages show no "Generate quiz" affordance for their own quiz (and no doubled `quiz/quiz/` probe in the console)
- [x] Quick-check pages likewise
- [x] Lesson pages keep the correct Take quiz / Generate quiz behavior (probe resolves as today)
- [x] `mise run verify` exits 0; interactive checks stay green

## Resolution

Component-side guard in `LessonActions.js` (chosen over per-generator template flags —
one fix covers quiz pages, quick-check/review pages, the deprecated preact_page path,
and any hand-authored page): when the resolved lessonId ends with `-quiz` or the page
path contains `/quiz/`, the bar skips the HEAD probe entirely (no `quiz/quiz/...`
doubled-path 404 in the console) and renders no quiz affordance at all. Lesson pages
are untouched — their config island still drives the normal Take quiz / Generate quiz
probe. Interactive checks (`verify-interactive.py`) and the full `verify` suite exit 0;
visual confirmation via Playwright walkthrough of lesson, quiz, and review pages.
