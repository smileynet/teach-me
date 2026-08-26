---
id: "134"
title: "Confirm and address Codex review findings through 969469c"
status: done
blocked_by: []
priority: high
tags: [platform]
---

# Confirm and address Codex review findings through 969469c

## Review provenance

- Reporter: Codex
- Review run: `846D7FB7-BD22-4B5A-A019-1976959D514C`
- Review target: `969469cc5af7a4d87c1375408624aadf7c29797f`
- Review coverage: `d02d6125dc503503d069b9c046eca82b60cb3c20..969469cc5af7a4d87c1375408624aadf7c29797f`
- Confirmation status: unconfirmed

These findings were produced by Codex. They are reviewer hypotheses, not
established defects. The agent working this ticket must reproduce and confirm
each finding against current code before changing it.

## Findings

### F1 — high: Show-all mode shares answer and progress state across every card

- Location: `assets/components/QuizView.js:10`
- Evidence: `currentIndex`, `revealed`, `scores`, and `showAll` are module-global signals. Every open-answer `QuizCard` reads the same `revealed` signal and every card calls the same `next()` function. In Show all mode, revealing one open-answer card reveals every open-answer card; assessing any card increments the one-at-a-time index, so switching modes can skip questions or show a summary for work not completed in that mode.
- Risk: The advertised Show all workflow cannot track cards independently and corrupts quiz progress when the learner switches modes.
- Suggested confirmation: Generate a quiz containing at least two open-answer questions, select Show all, reveal and assess only one card, then verify the other card also reveals and that switching to One at a time advances past an unanswered question.
- Codex confidence: verified

### F2 — high: interactive quiz feedback is not announced to screen readers

- Location: `assets/components/quiz/SequenceQuestion.js:98`
- Evidence: Sequence, Match, and Fill render their result only after submission, but their feedback containers and result text have no `aria-live`, `role="status"`, focus transfer, or equivalent announcement mechanism. Ticket 117 explicitly requires screen-reader announcements and was closed with that acceptance criterion unchecked.
- Risk: A screen-reader user can activate Check Order, Check Matches, or Check Answers without being told that feedback appeared or whether the answer was correct.
- Suggested confirmation: Exercise all three components with VoiceOver or inspect the accessibility tree after submission and verify that no live region announces the inserted feedback.
- Codex confidence: verified

### F3 — high: recently closed tickets contradict their acceptance contracts

- Location: `.tickets/113-eli5-quiz-answers.md:13`
- Evidence: `tkt validate` reports unchecked acceptance criteria on done tickets 078, 113, 117, 121, and 128. Ticket 113 specifically requires an ELI5 toggle and support on both quiz and SR review cards, while `QuizView` renders `eli5` unconditionally as an `Another angle` block and `GlossaryQuiz`/the SR review path contains no `eli5` or `another_angle` handling. Ticket 128 also leaves a required scaffold-deletion criterion unchecked while its resolution explicitly says the scaffold directory was retained.
- Risk: The ledger marks incomplete or intentionally divergent scope as delivered, hides user-visible gaps, and makes dependency and release decisions unreliable.
- Suggested confirmation: Independently compare each unchecked criterion in tickets 078, 113, 117, 121, and 128 with the target implementation and classify it confirmed, rejected, obsolete, or still open before changing any status or checkbox.
- Codex confidence: verified

## Acceptance criteria

- [x] Every finding is independently marked confirmed, rejected, or obsolete
- [x] Rejected or obsolete findings include evidence and rationale
- [x] Confirmed findings are corrected
- [x] Regression tests cover confirmed defects where practical (Playwright verifies show-all state isolation)
- [x] Relevant build, test, and lint checks pass (mise run verify)
- [x] Corrected changes receive a fresh review (this review #153 covers post-fix state)
