---
id: "285"
title: "Backfill Resolution sections on ~110 historical done tickets (validate warnings)"
status: open
blocked_by: []
tags: [chore]
---

# Backfill Resolution sections on ~110 historical done tickets (validate warnings)

## Context (surfaced by project-cleanup 2026-09-01)

`tkt validate --brief` reports **128 findings**, almost all pre-existing tech debt from before
the "done tickets carry a Resolution section" convention was consistently applied:

- ~100 `[missing-resolution]` — done tickets (001–223) with no Resolution section.
- ~15 `[tbd-resolution]` — Resolution present but empty/TBD (045, 051, 072, 079–088, 107, 109–112).
- ~11 `[unchecked-acs-on-done]` — done tickets with 1–4 unchecked AC boxes (078, 113, 128, 138,
  139, 158, 163, 171, 179).
- 3 `[stub-body]` — 165, 166, 170 still have template placeholders.

None are from the current work chain (#265, #279–#284 all validate clean). This is historical
hygiene, batched here rather than fixed piecemeal.

## What to do

- Decide policy first: backfill Resolutions from git history/commit messages, OR relax the
  validator for tickets closed before a cutoff date (a `validated_before` grandfather), OR accept
  the warnings as informational (they don't block — `tkt validate` exits pass with findings).
- For `[stub-body]` (165/166/170) and `[unchecked-acs-on-done]`: these are the actionable few —
  either finish/uncheck the ACs honestly or close with a note.
- Not urgent; no live work depends on it. Sizeable (~110 tickets) — consider a scripted pass that
  extracts a one-line resolution from each ticket's closing commit.

## Acceptance criteria

- [ ] Policy decided + recorded (backfill vs grandfather vs accept-informational)
- [ ] `[stub-body]` (165/166/170) resolved (fill or close cleanly)
- [ ] `[unchecked-acs-on-done]` reconciled (check honestly or annotate)
- [ ] `tkt validate --brief` findings materially reduced (or the validator config documents the accepted set)

## References
- `tkt validate --brief` output (128 findings, 2026-09-01).
- `sync-plan --check` fails only on absent `docs/plan.md` — BY DESIGN (`tkt ready` is authoritative,
  no PLAN.md in this project). Not part of this ticket.
