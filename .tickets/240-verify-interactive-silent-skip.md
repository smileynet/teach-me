---
id: "240"
title: "verify-interactive.py silently skips when an unrelated server occupies 8787/8080"
status: done
blocked_by: []
priority: high
tags: ["platform"]
---

# verify-interactive.py silently skips when an unrelated server occupies 8787/8080

## Why

The interactive Playwright stage of `mise run verify` silently no-ops (exit 0,
"⚠ No suitable lesson page served — skipping interactive checks") whenever an
unrelated server occupies port 8787 or 8080. On a dev machine with `mise run serve`
running, the entire interactive gate self-disables. This surfaced closing #237:
verify went green but the interactive components were never actually exercised.

## Verified root cause

`main()` probes ports 9123 → 8787 → 8080 and adopts the FIRST that answers a TCP
connection as `base_url`, treating even a 404 as "server running, still usable".
It never checks that server serves the expected content. If a different-workspace
server is up on 8787, the tool binds to it, then `find_test_page()` probes its
fixed candidate list, none resolve, and it hits the `url is None` skip branch.

Evidence (this machine, 2026-08-28):
- Port 8787 was LISTENING (pid 90264, a `mise run serve` on another workspace).
- `verify-interactive.py` standalone → "No suitable lesson page served", exit 0.
- Serving `examples/godot-gamedev` manually on a private port: `/lessons/0004-toon-banding.html`
  AND `/lessons/blender-texture-prep/01-texture-audit.html` both return **200** —
  the pages exist and ARE servable; the tool just adopted the wrong server.

## What to do (refined after subagent research + code audit)

Root cause is precise (verify-interactive.py lines 265–275): the probe loop adopts the
FIRST port (9123→8787→8080) that returns ANY TCP response — including a 404 — as
`base_url` without confirming it's THIS project's server. serve.py returns 404 at `/`
by design (no root index.html in godot-gamedev), so the "404 = ready" heuristic that's
correct for OUR server also lets a FOREIGN server pass. Then find_test_page finds no
lesson pages → None → silent skip (exit 0).

**Fix B (primary) — own an ephemeral port; never adopt a foreign server.**
Always start our own serve.py on an OS-assigned free port and use it. Preferred
mechanism (least-invasive to serve.py): parent pre-binds a socket to `:0`, reads the
assigned port via getsockname(), closes it, passes that number as `--port`. This makes
`verify` hermetic and removes the fixed-port collision surface (9123/8787/8080) and the
undocumented 8080 coupling with visual-qa.py.

**Optional convenience — validated reuse of a running dev server.**
Before self-starting, probe `http://localhost:8787` with a `_serves_lessons()` check
(fetch a known lesson path, require HTTP 200) and adopt ONLY on a verified 200. Fast
when a valid dev server exists, correct when it doesn't. Mirrors Playwright's
reuseExistingServer convention. This is optional — Fix B alone is sufficient.

**Fix 2 — reclassify skip vs fail (research: a smoke test that checks reachability must
FAIL on unreachable, never silently skip; silent skips roll up green and erode the gate).**
- KEEP skip (genuine env gap): playwright not installed; serve.py/uv deps genuinely absent.
- CHANGE to FAIL (misconfig/regression): our own server started but our own pages 404
  (find_test_page None on a known-good workspace); server-won't-start when tooling is present.

**Also (sibling bug):** visual-qa.py has the same failure class via a different mechanism —
hardcoded port 8080 with no bind-collision check, so if 8080 is occupied it silently tests
someone else's server. Apply the same ephemeral-port pattern. Track as a follow-up if it
expands scope (may split to its own ticket).

Do NOT change the 8 component check assertions. Minor cleanups noted by the audit
(dead `resp` binding L268, missing wait() on early-skip teardown L313, 1s find_test_page
timeout) are optional.

## Acceptance criteria

- [x] verify-interactive.py starts its OWN server on an ephemeral (:0) port and does NOT adopt a foreign server on 8787/8080
- [x] With an unrelated server running on 8787, the tool still runs the 8 checks against its own server (prints "✓ Interactive checks pass"), does NOT skip
- [x] With no servers running, the tool starts its own, finds godot-gamedev pages, runs the checks
- [x] "Our own server up but a known lesson page 404s" now EXITS NON-ZERO (loud), not silent skip
- [x] Genuine skip paths preserved: playwright-not-installed still exits 0 with a skip message
- [x] `mise run verify` EXIT 0 with the interactive stage RUNNING (not skipping) — verified by reading the "Interactive checks pass" line, negative-tested with a stray 8787 server present
- [x] No change to the 8 component check assertions
- [x] visual-qa.py hardcoded-8080 sibling bug: fixed here OR filed as a follow-up ticket

## Resolution (2026-08-28)

Fixed verify-interactive.py: (1) hoisted candidate pages to `_CANDIDATE_PAGES`;
(2) added `_free_port()` (bind :0) and `_serves_lessons()` (200-validated content check);
(3) main() now reuses a 8787 dev server ONLY if `_serves_lessons` passes, else self-starts
serve.py on an OS-assigned ephemeral port — never adopts a foreign server; (4) reclassified
skip→fail: serve.py-won't-start → exit 2, our-server-up-but-page-404s → exit 1; playwright
-missing skip (exit 0) preserved. sibling visual-qa.py bug filed as #241 (backlog).

Evidence (all live-tested):
- Stray content-less server on 8787 (the original bug repro): tool did NOT adopt it,
  self-started ephemeral, ran all 8 checks → "✓ Interactive checks pass (8 checks)".
- VALID godot-gamedev server on 8787: tool reused it, 8 checks pass.
- No server: tool self-started, 8 checks pass.
- Fail-loud branch (find_test_page→None via monkeypatch harness): SystemExit code=1 with
  "✗ No lesson page served ... interactive gate cannot run" — no silent skip.
- `mise run verify` EXIT 0 with interactive stage RUNNING (8 checks, ~25s vs ~12s when it
  used to skip) — #237 caveat closed.
