---
id: "058"
title: "Spike: kiro-cli output characterization — buffering, patterns, streaming"
status: open
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

- [ ] Documented: streaming behavior (line-by-line vs buffered)
- [ ] Documented: 5+ recognizable output patterns for phase detection
- [ ] Documented: whether NO_COLOR=1 fully suppresses ANSI
- [ ] Documented: SIGTERM behavior (clean exit? orphaned processes?)
- [ ] Recommendation: what env vars / wrappers needed for clean streaming

## Expected output

A findings file at `.scratch/research/kiro-cli-output-characterization.md` with timestamped examples, pattern catalogue, and environment recommendations.
