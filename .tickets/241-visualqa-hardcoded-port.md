---
id: "241"
title: "visual-qa.py hardcodes port 8080 with no bind-collision check (sibling of #240)"
status: backlog
blocked_by: []
priority: medium
tags: ["platform"]
---

# visual-qa.py hardcodes port 8080 with no bind-collision check (sibling of #240)

## Why

Found during the #240 code audit. `tools/visual-qa.py` `--serve` always starts its
own `python -m http.server` on a **hardcoded 8080** with a fixed `time.sleep(0.5)`
and no readiness/collision check. If 8080 is already occupied, `http.server` fails
to bind and visual-qa silently runs against **someone else's** 8080 server — the same
"silently test the wrong server" failure class #240 fixed in verify-interactive.py,
via a different mechanism. It also uses raw `http.server` (from cwd) instead of
`serve.py`, so `/assets` and API routes aren't mounted — different fidelity than the
real serve path.

## What to do

Apply the #240 pattern: bind an ephemeral (:0) port instead of hardcoded 8080, use a
readiness poll instead of a fixed sleep, and prefer `serve.py` over `http.server` for
route/asset fidelity. Reuse `_free_port()` / readiness logic established in #240
(verify-interactive.py) — but do NOT extract a shared helper unless a third consumer
appears (avoid single-use abstraction).

## Acceptance criteria

- [ ] visual-qa.py serves on an OS-assigned free port, not hardcoded 8080
- [ ] Uses a readiness poll (not a fixed sleep) before running checks
- [ ] Does not silently run against a foreign server if 8080/its port is occupied
- [ ] Existing visual-qa checks still pass (`mise run visual-qa`)
