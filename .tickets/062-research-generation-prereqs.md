---
id: "062"
title: "Research: browser generation prerequisites — buffering, SSE stability, cancellation"
status: open
priority: high
blocked_by: []
type: research
---

# Research: browser generation prerequisites

## Must investigate before building

These questions block confident implementation. Each should be answered with a short experiment.

### 1. kiro-cli stdout buffering behavior
**Question:** Does `kiro-cli chat --no-interactive` stream stdout line-by-line or buffer until completion?
**Why:** If buffered, SSE streaming is useless (all output arrives at the end).
**Method:** `NO_COLOR=1 kiro-cli chat --no-interactive "explain HTTP caching in one paragraph" 2>&1 | ts '%H:%M:%.S'`
**Also try:** `stdbuf -oL kiro-cli ...` and `script -qec 'kiro-cli ...' /dev/null`

### 2. NO_COLOR effectiveness
**Question:** Does `NO_COLOR=1` fully suppress ANSI escape codes from kiro-cli output?
**Why:** Residual ANSI codes corrupt SSE event data and confuse pattern matching.
**Method:** `NO_COLOR=1 kiro-cli chat --no-interactive "hello" | cat -v` — look for `^[` sequences

### 3. SIGTERM behavior
**Question:** Does `kill -TERM $PID` cleanly stop kiro-cli? Does it leave orphaned child processes?
**Why:** Cancel button needs reliable shutdown without zombie processes.
**Method:** Start a generation, send SIGTERM mid-run, observe with `ps --forest`

### 4. FastAPI native SSE stability
**Question:** Is `EventSourceResponse` in FastAPI ≥0.135.0 stable for multi-minute streams? Or should we use the `sse-starlette` package?
**Why:** Native SSE is newer and less battle-tested. A dropped connection mid-generation is bad UX.
**Method:** Build the spike (057) with native SSE. If issues arise, swap to `sse-starlette`.

### 5. Working directory for file output
**Question:** When kiro-cli spawns with `cwd=project_root`, do generated lessons land in the expected `lessons/` directory?
**Why:** The completion flow needs to know where new files appear.
**Method:** Run a generation with `subprocess.Popen(cwd=...)`, check file locations.

## Would benefit from investigation (lower priority)

| Topic | Value |
|-------|-------|
| EventSource auto-reconnection | Does the browser auto-retry on connection drop? What's the retry interval? Affects long generations on flaky WiFi. |
| Notification API permission UX | When to ask (on first generate click). What happens if denied? Fallback? |
| Partial generation recovery | If kiro-cli dies at step 3/4, is the partial lesson saved? Can we resume? (Likely: no resume support, but partial files may exist.) |
| `stdbuf -oL` portability | Available on Linux (coreutils). Available on macOS? Needed if direct streaming doesn't work. |
| uvicorn `--reload` for dev | Auto-restart serve.py on code changes during development. Worth configuring? |
| Concurrent task queuing | What happens if user clicks "Generate" on two topics quickly? Queue? Reject? Allow parallel? |

## Deliverable

A single research file `.scratch/research/generation-prerequisites.md` answering all "must investigate" questions with evidence (command output, timestamps, file locations).
