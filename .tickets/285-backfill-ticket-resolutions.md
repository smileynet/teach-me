---
id: "285"
title: "Backfill Resolution sections on ~110 historical done tickets (validate warnings)"
status: done
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

- [x] Policy decided + recorded (baseline-accept + forward-only enforcement)
- [x] `[stub-body]` (165/166/170) resolved (165+166 filled & closed done; 170 filled & kept open — never built)
- [x] `[unchecked-acs-on-done]` reconciled (163 + 158 honestly annotated; rest already annotated/descoped)
- [x] `tkt validate --brief` findings materially reduced (stub-body 3→0; remaining missing/tbd-resolution documented as an accepted baseline)

## References
- `tkt validate --brief` output (128 findings, 2026-09-01).
- `sync-plan --check` fails only on absent `docs/plan.md` — BY DESIGN (`tkt ready` is authoritative,
  no PLAN.md in this project). Not part of this ticket.


## Resolution (2026-09-04) — baseline-accept + forward-only enforcement

**Policy (evidence-backed).** Research (ESLint bulk-suppressions, detekt/Android `baseline.xml`,
flake8-baseline, ratchet tooling) + closure-note norms converge on: **accept historical debt,
gate only new**. Git-log backfill was verified non-viable (~60% of old closes are batch/generic
commits or direct frontmatter edits with no closing commit); no grandfather field exists in `tkt`;
and none of these items are compliance-scoped (pure internal hygiene). So we do NOT bulk-backfill.

**Accepted baseline (as of 2026-09-04, `tkt validate --brief`):**
- 98 `[missing-resolution]` + 18 `[tbd-resolution]` = 116 pre-convention done tickets — ACCEPTED,
  non-blocking, documented here. The count may only DECREASE (ratchet) — add a Resolution
  opportunistically when touching an old ticket; no mass pass.
- `[stub-body]`: 3 → 0.
- `[unchecked-acs-on-done]`: 10, all now honestly annotated or legitimately descoped (never faked).

**Forward enforcement.** `.tickets/config.toml` sets `close.require_resolution=true` — new closes
must carry a `## Resolution`. This is the "gate only new" half; it stops the debt regrowing.
AGENTS.md documents both the convention and the accepted baseline.

**Actionable few fixed:**
- 165 (skill narrative+subfolders) — shipped; filled body + Resolution, closed done.
- 166 (script subfolder support) — shipped (proven by the blender-texture-prep track); closed done.
- 170 (SR TF-IDF dedup) — verified NEVER built (`sr-check.py` has no `--dedup`); filled body from
  #171's spec, kept OPEN as real low-priority backlog (no fake close).
- 163 — its "renumber toon-shader lessons to 01/02" box is STILL unmet (verified: `0003-`/`0004-`
  not renamed; the #166 deferral didn't cover it). Left unchecked + annotated honestly — NOT faked.
  Surfaced a real inconsistency (godot-toon-shaders keeps global 0003–0014 vs per-domain elsewhere)
  → follow-up.
- 158 — lone "fresh review" box: F1/F2 fixes shipped with regression tests + on `main` passing
  verify; a fresh review of months-old tested code is low-value. Annotated as an accepted gap.

**Not done (deliberately):** bulk backfill of the 116 historical tickets — low-value churn / an
anti-pattern per the research. The remaining warnings are a documented, accepted, non-blocking
baseline — the best-practice end state, not "zero findings."
