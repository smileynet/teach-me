---
id: "225"
title: "Harden play-ink.py (error scoping, state-hash loop detection)"
status: done
blocked_by: []
priority: high
type: fix
tags: ["ink"]
---

# Harden play-ink.py

## Problem

Independent audit of the playthrough validator (#224) found should-fix issues. The tool works for the current 4 stories but has correctness gaps that could produce false PASS/FAIL on future stories.

## Audit findings to fix

### should-fix
1. **Error scoping** — broad `except Exception` at story level conflates tool bugs (AttributeError/TypeError) with story runtime errors, AND one strategy's error aborts all others (so `last:ERROR` vetoes a clean `first:END`). Fix: catch bink's specific ink error per-strategy; let tool bugs propagate; wrap each play_once so per-strategy ERROR is a recorded outcome, not a global abort.

2. **State-hash loop detection** — flat 200-turn cap can't distinguish a true 2-state cycle from a long finite path. Fix: hash story state (save_state JSON) after each step; classify LOOP on first repeat with certainty. Keep turn-cap as a hard backstop. State-hash under-detects (visit counts differ) but never over-detects — no false positives.

3. **Strategy false-positive + ticket divergence** — "any strategy = PASS" swallows a strategy-dependent hang into the detail string. Also diverges from #224's decision logic. Fix: report per-strategy outcomes explicitly; align WARN with ticket (e.g., flag when first/last disagree).

### nice-to-have
4. Dead code: `is_ended()` (L62-64) unused — play_once re-implements inline. Remove or use it.
5. `.ink.json` compiled files written beside sources, never cleaned — litters stories dir. Compile to a temp dir or clean up after.
6. Arg parser raises uncaught IndexError on a flag with no value.
7. The 3 random runs share ONE rng stream (continuing walks, not i.i.d.); random_best reports placeholder turn_cap not actual turns on all-LOOP.

## Acceptance criteria

- [x] Per-strategy error isolation (one strategy's ink error doesn't abort others; tool bugs propagate)
- [x] State-hash loop detection with turn-cap backstop
- [x] Explicit per-strategy outcome reporting
- [x] Cleanup: dead code removed, .ink.json not littered (temp dir), arg parser robust
- [x] All 5 current stories still PASS
- [x] Re-run confirms no regression

## Resolution (2026-08-26)

Rewrote play-ink.py (230 lines):
- **Error scoping:** `InkRuntimeError` class + `run_strategy()` wrapper. Ink runtime errors ("ran out of content") become a per-strategy ERROR outcome; tool bugs (AttributeError etc.) propagate. One strategy's error no longer aborts the others.
- **State-hash cycle detection:** sha1 of `save_state()` after each step; repeated state → LOOP. Documented as best-effort (visit counts always increment so it under-detects) with the turn-cap as the guaranteed backstop.
- **Explicit reporting:** every strategy's outcome shown (e.g. `last:END(7t), first:LOOP(200t), random:END(19t)`).
- **Cleanup:** compile to a tempfile.TemporaryDirectory (no .ink.json litter), robust arg parsing (no IndexError), independent seeded RNG per random run, removed dead `is_ended()`.

Verified: all 5 stories PASS. A deliberately-broken dead-end story (once-only choice looping with no fallback) correctly reported FAIL with `last:ERROR, first:ERROR, random:ERROR` — and did NOT abort the other 5 stories' validation.

Note: pre-existing hygiene issue (out of scope) — 01_flow_and_knots.ink.json and hello.ink.json are tracked compiled artifacts that ideally shouldn't be committed.

## Post-hardening validation (2026-08-27)

- **State-hash probe:** confirmed empirically that a stateless loop story produces a UNIQUE hash every turn (ink save_state includes incrementing visit counts). State-hash detection can never fire → removed as dead code, documented honestly. Turn-cap is the sole loop mechanism.
- **Broken corpus test (3 shapes):** deadend-once-only → FAIL(ERROR) ✓; tunnel-no-return → FAIL(ERROR) ✓; linear-clean → PASS ✓. Error detection works across distinct failure modes, not just "ran out of content."
- **Independent re-audit:** PASS on all 5 should-fix items (error scoping, state-hash removal, reporting, cleanup, correctness). One cosmetic docstring nit fixed.
- **Final regression:** 5/5 stories PASS.
