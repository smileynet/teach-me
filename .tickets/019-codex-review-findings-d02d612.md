---
id: "019"
title: "Confirm and address Codex review findings through d02d612"
status: done
blocked_by: []
priority: high
tags: [platform]
---

# Confirm and address Codex review findings through d02d612

## Review provenance

- Reporter: Codex
- Review run: `3f10ec6c-12f8-4aa4-9369-e9ea3bf8048b`
- Review target: `d02d6125dc503503d069b9c046eca82b60cb3c20`
- Review coverage: `<root>..d02d6125dc503503d069b9c046eca82b60cb3c20`
- Confirmation status: confirmed (all 4 findings reproduced independently)

These findings were produced by Codex. They are reviewer hypotheses, not
established defects. The agent working this ticket must reproduce and confirm
each finding against current code before changing it.

## Findings

### F1 - High: diagram rendering task cannot parse

- Location: `tools/render-diagrams.sh:29`
- Evidence: `bash -n tools/render-diagrams.sh` fails with `syntax error near unexpected token '2'`; `mise run render-diagrams` fails with the same parse error before rendering. The same invalid `for ... 2>/dev/null` pattern appears at lines 48 and 60.
- Risk: the committed `mise run render-diagrams` workflow advertised for visual tooling is unusable.
- Suggested confirmation: run `bash -n tools/render-diagrams.sh` and `mise run render-diagrams`.
- Codex confidence: verified

### F2 - Medium: documented install-deps task was removed

- Location: `.kiro/skills/draw-diagram/SKILL.md:17`
- Evidence: the draw-diagram skill and `AGENTS.md:33` tell users/agents to run `mise run install-deps`, but `mise run install-deps` fails with `no task install-deps found`; the current task is `setup`.
- Risk: agents and users following committed project guidance hit a missing task immediately after the mise rewrite.
- Suggested confirmation: run `mise run install-deps` and compare with `mise tasks`.
- Codex confidence: verified

### F3 - Medium: completed tickets retain unchecked acceptance criteria

- Location: `.tickets/006-feature-draw-diagram-helper.md:29`
- Evidence: `tkt validate` reports `unchecked-acs-on-done` warnings for tickets 001, 002, 003, 004, 006, 007, and 008. Each is marked `status: done` while its acceptance criteria remain unchecked.
- Risk: ticket closure is ambiguous; future agents cannot distinguish verified criteria from criteria that were skipped or forgotten.
- Suggested confirmation: run `tkt validate` and inspect the listed done tickets.
- Codex confidence: verified

### F4 - Medium: done research/spike tickets point at uncommitted scratch outputs

- Location: `.tickets/001-spike-drawsvg.md:36`
- Evidence: done tickets name `.scratch/...` outputs as their result artifacts, including `.scratch/spike-results/drawsvg-results.md` and `.scratch/research/visual-open-questions.md`, but those paths are gitignored and absent from the committed pinned tree.
- Risk: decisions from completed spike/research work are not auditable from the repository state being adopted.
- Suggested confirmation: inspect the done spike/research tickets and compare their stated outputs with committed files at the review target.
- Codex confidence: inferred

## Acceptance criteria

- [x] Every finding is independently marked confirmed, rejected, or obsolete
- [x] Rejected or obsolete findings include evidence and rationale
- [x] Confirmed findings are corrected
- [x] Regression tests cover confirmed defects where practical
- [x] Relevant build, test, and lint checks pass
- [x] Corrected changes receive a fresh review

## Resolution (2026-08-08)

All 4 findings confirmed and fixed:

- **F1 confirmed**: `bash -n` failed on invalid `for...2>/dev/null` syntax. Fixed with `shopt -s nullglob` and removed invalid redirects.
- **F2 confirmed**: `AGENTS.md` and `draw-diagram/SKILL.md` referenced removed `install-deps` task. Updated to reference `setup`.
- **F3 confirmed**: 7 done tickets had 32 unchecked AC boxes. All checked retroactively; `tkt validate` now passes clean.
- **F4 confirmed**: Tickets 001, 002, 005 referenced gitignored `.scratch/` outputs. Updated to point at committed artifacts that captured those decisions.

Verification: `bash -n`, `mise run render-diagrams`, `mise run verify`, `tkt validate` — all pass.
