---
id: "374"
title: "Handle OverlayRecoveryError in check-topic-completeness (corrupt overlay crashes the checker)"
status: in_progress
blocked_by: []
priority: low
type: bug
tags: ["tools", "overlay", "risk-review"]
validation_criteria:
  - "A corrupt private overlay produces a readable diagnostic from every consumer, not a raw traceback"
---

# Handle OverlayRecoveryError in check-topic-completeness (corrupt overlay crashes the checker)

## Intent

The fail-loud overlay contract (#353) should surface as a readable diagnostic in every consumer,
including the CLI completeness checker.

## Context (found 2026-09-18 risk review of the 2026-09-16/17 window)

`575e1de` (#353) flipped `Overlay.load()` from "corrupt file → silently return empty doc (reset
progress)" to raising `OverlayRecoveryError` (`tools/lib/overlay.py:158-170`), including strict
per-record ULID/status validation. `tools/serve.py` handles it correctly (503 with the diagnostic
at `serve.py:139-143, 241-258`). But `tools/check-topic-completeness.py:284` calls
`Overlay(workspace).status_map()` unguarded — a corrupt `.user/status-overlay.json` now produces
a raw traceback there instead of a report.

Verified scope: the map/index generators are NOT affected — `demo_status_map_for_map` reads the
committed `demo-status.json` with its own tolerant loader (`tools/lib/overlay.py:243-263`), not
the private overlay. `check-topic-completeness.py` is the one unguarded consumer found.

Note the strict validation also makes previously-tolerated non-ULID overlay keys fatal; whether
any real `.user/` overlay contains such keys is unverifiable (gitignored).

## What to build

Catch `OverlayRecoveryError` in `check-topic-completeness.py` and report the diagnostic (name
the file, keep the fail-loud posture — do NOT silently ignore) with a distinct non-zero exit or
a clearly-marked incomplete report.

## Acceptance criteria

- [ ] With a corrupt overlay file, `check-topic-completeness.py` prints the recovery diagnostic (path + reason) and exits deliberately, not via traceback
- [ ] The checker never silently treats corrupt state as "no progress recorded"
- [ ] A fixture test covers the corrupt-overlay path for the checker

## References

- Commit `575e1de` (#353); `tools/check-topic-completeness.py:284`; `tools/lib/overlay.py:158-170`
