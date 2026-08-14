---
id: "130"
title: "Confirm and address Codex review findings through f7a8087"
status: open
blocked_by: []
priority: high
---

# Confirm and address Codex review findings through f7a8087

## Review provenance

- Reporter: Codex
- Review run: `9528C703-E768-47BA-B473-E26903F701D5`
- Review target: `f7a8087e22a6c36a0598328ead7e30af5367ffe5`
- Review coverage: `d02d6125dc503503d069b9c046eca82b60cb3c20..f7a8087e22a6c36a0598328ead7e30af5367ffe5`
- Confirmation status: unconfirmed

These findings were produced by Codex. They are reviewer hypotheses, not
established defects. The agent working this ticket must reproduce and confirm
each finding against current code before changing it.

## Findings

### F1 — high: the required quiz-navigation check only validates button text

- Location: `tools/verify-interactive.py:129`
- Evidence: The remediation for ticket 125 names this check `quiz_button_label` and passes when the first action-bar button has one of two expected labels. It never clicks the control or asserts the destination, even though ticket 124 now claims quiz-button coverage and the original finding explicitly required navigation. `mise run verify` passes with this label-only check.
- Risk: A dead quiz button or incorrect quiz destination can ship while the required interactive gate remains green.
- Suggested confirmation: Point the representative lesson's quiz action at an invalid destination without changing its label, run `mise run verify`, and confirm the suite still passes.
- Codex confidence: verified

### F2 — high: the prior aggregate review ticket was closed without independent confirmation

- Location: `.tickets/125-codex-review-findings-28383c.md:17`
- Evidence: Ticket 125 remains `Confirmation status: unconfirmed`, all six aggregate acceptance criteria are unchecked, and its resolution only asserts that all findings were corrected. `tkt validate` consequently reports `unchecked-acs-on-done` for ticket 125. Finding F1 above also demonstrates that its F2 remediation did not satisfy the stated navigation requirement.
- Risk: Review hypotheses can be treated as resolved without the required independent confirmation or fresh review, allowing incomplete remediation to become the accepted baseline.
- Suggested confirmation: Reopen ticket 125's evidence, independently classify F1–F3, and test each claimed correction against the original reproduction steps before updating its confirmation status or criteria.
- Codex confidence: verified

### F3 — medium: a second done ticket still violates the closure contract

- Location: `.tickets/047-feature-supertopics.md:47`
- Evidence: All five acceptance criteria remain unchecked and the resolution is still `TBD`, while the ticket status is `done`. `tkt validate` reports this as `unchecked-acs-on-done`.
- Risk: The ticket ledger declares the feature complete without recorded acceptance or resolution evidence, so downstream work cannot reliably distinguish delivered behavior from unfinished scope.
- Suggested confirmation: Trace each acceptance criterion through the parser, API, generation flow, and user-visible language; then record evidence, reject obsolete criteria with rationale, or reopen the ticket.
- Codex confidence: verified

## Acceptance criteria

- [ ] Every finding is independently marked confirmed, rejected, or obsolete
- [ ] Rejected or obsolete findings include evidence and rationale
- [ ] Confirmed findings are corrected
- [ ] Regression tests cover confirmed defects where practical
- [ ] Relevant build, test, and lint checks pass
- [ ] Corrected changes receive a fresh review
