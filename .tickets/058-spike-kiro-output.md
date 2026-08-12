---
id: "058"
title: "Spike: kiro-cli output characterization — buffering, patterns, streaming"
status: done
priority: high
blocked_by: []
type: spike
---

# Spike: kiro-cli output characterization

## Question to answer

When kiro-cli runs `--no-interactive`, does its stdout stream line-by-line or buffer? What recognizable patterns appear in the output that we can match to generation phases?

## What to test

1. Run `NO_COLOR=1 PYTHONUNBUFFERED=1 kiro-cli chat --no-interactive "teach me about [small topic]"` and capture output with timestamps:
   ```bash
   NO_COLOR=1 kiro-cli chat --no-interactive "teach me about HTTP caching" 2>&1 | ts '%H:%M:%.S' > /tmp/kiro-output.log
   ```
2. Examine the log for:
   - Buffering: do lines appear one at a time or in bursts?
   - Phase patterns: are there recognizable strings for research/writing/saving?
   - ANSI codes: does NO_COLOR fully suppress them?
   - Total duration: how long does a typical generation take?
3. Try piping through `stdbuf -oL` if direct output is buffered
4. Test SIGTERM: does `kill -TERM $PID` produce a clean shutdown?

## Success criteria

- [x] Documented: streaming behavior (line-by-line vs buffered)
- [x] Documented: 5+ recognizable output patterns for phase detection
- [x] Documented: whether NO_COLOR=1 fully suppresses ANSI
- [x] Documented: SIGTERM behavior (clean exit? orphaned processes?)
- [x] Recommendation: what env vars / wrappers needed for clean streaming

## Resolution (2026-08-11)

Findings in `.scratch/research/kiro-cli-output-characterization.md`.

Key results:
- **Buffering:** BURST output (not line-by-line). Internal to kiro-cli, stdbuf doesn't help.
- **Patterns:** 9 matchable patterns identified (thinking, tool use, file diff, response, timing footer, etc.)
- **ANSI:** NO_COLOR=1 does NOT suppress escape codes. Always strip.
- **SIGTERM:** Kill `kiro-cli-chat` (the worker child), not `kiro-cli` (the wrapper). Wrapper kill orphans processes.
- **Recommendation:** Use `start_new_session=True`, strip ANSI on every line, design for phase-level progress (not token streaming), heartbeat during thinking silence.

## Expected output

A findings file at `.scratch/research/kiro-cli-output-characterization.md` with timestamped examples, pattern catalogue, and environment recommendations.
