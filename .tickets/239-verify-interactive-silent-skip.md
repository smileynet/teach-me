---
id: "239"
title: "verify-interactive.py silently skips when an unrelated server occupies 8787/8080"
status: done
blocked_by: []
priority: high
tags: ["platform"]
---

# verify-interactive.py silently skips when an unrelated server occupies 8787/8080

## What to build

DUPLICATE of #240 (same title, same bug). #240 was implemented and closed
2026-08-28: verify-interactive.py now owns an ephemeral port (bind :0) instead of
adopting any server on 8787/8080, validates content before reusing a dev server,
and fails loud instead of silent-skip. This stub (#239) was never fleshed out.

## Acceptance criteria

- [x] Superseded by #240 (fixed + closed) — no separate work needed

## Resolution (2026-08-28)

Closed as duplicate of #240. #240 implemented the ephemeral-port + validated-reuse + fail-loud fix; no separate work needed for #239 (never fleshed out beyond the stub)
