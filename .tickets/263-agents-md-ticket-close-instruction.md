---
id: "263"
title: "AGENTS.md 'Closing a ticket' says hand-edit status:done; tkt close works fine now (reconcile)"
status: backlog
priority: low
tags: ["platform"]
blocked_by: []
---

# Reconcile AGENTS.md ticket-closing guidance with tkt close behavior

## Intent source
Observed across this session (2026-08-29): closed #254, #256, #257, #261 all via
`tkt close --check-all` with no error. But AGENTS.md's Workflow table row "Closing a
ticket" instructs: "Edit frontmatter `status: done` directly — `tkt close` has a config
validation bug that rejects valid tickets."

## What's wrong
The AGENTS.md instruction is now STALE and actively harmful: hand-editing `status: done`
skips `tkt close`'s gates (acceptance criteria, resolution, evidence) and the atomic push
protocol — exactly what the global `frontier-work.md` steering forbids ("Never set
`status: done` by editing the ticket file. Always run `tkt close`"). The two guidances
directly contradict, and the local one is wrong (tkt close is working).

## What to build
- Verify `tkt close` on a fresh test ticket (confirm no config-validation rejection).
- If it works (expected): update the AGENTS.md "Closing a ticket" row to say use
  `tkt close --check-all --evidence ... --resolution ...`, removing the hand-edit
  instruction and the stale bug claim. Align with `frontier-work.md`.
- If it STILL fails on some ticket shape: document the exact repro + the specific shape
  that triggers it, and keep a narrowed workaround note (not a blanket "always hand-edit").

## Context
- AGENTS.md Workflow table, "Closing a ticket" row.
- Global steering: `~/.kiro/steering/frontier-work.md` (Marking Done section).
- Evidence this session: #254→267d898, #256→3da2f54, #257→56a2e11, #261→47c77b6 all closed
  via `tkt close`.

## Acceptance criteria
- [ ] `tkt close` behavior re-verified on a throwaway ticket (works / documented failure shape)
- [ ] AGENTS.md "Closing a ticket" row reconciled — no contradiction with frontier-work.md
- [ ] If tkt close works, the hand-edit instruction + stale bug claim are removed

## Out of scope
- Any change to tkt itself.
