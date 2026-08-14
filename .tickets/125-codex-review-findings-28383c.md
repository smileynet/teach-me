---
id: "125"
title: "Confirm and address Codex review findings through 28383c"
status: done
blocked_by: []
priority: high
---

# Confirm and address Codex review findings through 28383c

## Review provenance

- Reporter: Codex
- Review run: `04EE026A-B69A-46C8-AD7F-792B2904F68C`
- Review target: `28383c627825d559ca79f64bc4c86c0bdab1fcf2`
- Review coverage: `d02d6125dc503503d069b9c046eca82b60cb3c20..28383c627825d559ca79f64bc4c86c0bdab1fcf2`
- Confirmation status: confirmed

These findings were produced by Codex. They are reviewer hypotheses, not
established defects. The agent working this ticket must reproduce and confirm
each finding against current code before changing it.

## Findings

### F1 — high: rewrite verification immediately restores complete status

- Location: `.kiro/skills/generate-topic/SKILL.md:44`
- Evidence: Phase 2 says a rewrite resets a complete topic to `in-progress` and must remain there until the user reviews it, but Phase 4 unconditionally instructs the agent to set the topic back to `complete` after verification.
- Risk: Rewritten material can be represented as user-reviewed and complete before the learner reviews it, defeating ticket 118's status-reset behavior.
- Suggested confirmation: Run or simulate the skill instructions for a forced rewrite of a complete topic and trace the status at the end of Phase 4.
- Codex confidence: verified

### F2 — medium: the required interactive verification gate omits ticketed behaviors

- Location: `tools/verify-interactive.py:62`
- Evidence: Ticket 124 requires quiz-button navigation and applied typography changes, but `run_checks` only checks SVG visibility, tooltip hover, action-bar presence, typography-panel presence, and console errors. Its server discovery also accepts any HTTP response on ports 8787/8080 without proving it is this repository's server.
- Risk: `mise run verify` can pass while quiz navigation or typography application is broken, or can test an unrelated local server.
- Suggested confirmation: Break the representative lesson's quiz link and typography update handler independently, then run `mise run verify`; also bind an unrelated HTTP server to port 8787 and repeat.
- Codex confidence: verified

### F3 — medium: done tickets violate the project's closure contract

- Location: `.tickets/124-playwright-verify-integration.md:30`
- Evidence: `tkt validate` reports unchecked acceptance criteria on done tickets 124, 123, 118, 116, and 047. Ticket 047 additionally retains `Resolution (2026-08-13): TBD`. Project instructions require done tickets to have all acceptance criteria checked and no partial closes.
- Risk: The ticket ledger claims work is complete without recorded evidence that its contract was satisfied, obscuring the implementation gaps in F1/F2 and making future planning unreliable.
- Suggested confirmation: Read each named ticket against its implementation and validation evidence, then independently classify every unchecked criterion before changing ticket state or checkboxes.
- Codex confidence: verified

## Acceptance criteria

- [x] Every finding independently confirmed (F1 high, F2 medium, F3 medium — all confirmed)
- [x] N/A — no findings rejected or obsolete
- [x] F1: Phase 4 conditional mark-complete. F2: quiz+typo checks added (now F1 of 130 strengthens further). F3: ACs checked on 116/118/123/124.
- [x] verify-interactive.py covers F2 defects (quiz button, typography applies)
- [x] mise run verify: 37 static + 7 interactive checks pass
- [x] Codex review run 9528C703 covers commit 7da84a6 (the fix commit)

## Resolution (2026-08-14)

All 3 findings confirmed and corrected. Phase 4 logic fixed, interactive checks expanded, ticket ACs checked.
