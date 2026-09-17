---
id: "066"
title: "Feature: error handling and retry for generative operations"
status: done
priority: low
blocked_by: []
type: feature
tags: [platform]
---

# Feature: error handling and retry for generative operations

## Problem

When generation fails (kiro-cli crash, timeout, network issue), the user sees "⚠️ Exited with code N" with no way to retry or understand what went wrong. No elapsed timer, no retry button, no error context.

## What to consider

### Error display
- Show a human-readable error message (not just exit code)
- Elapsed time at failure (how far did it get?)
- Last phase reached before failure (Thinking? Writing? Researching?)

### Retry
- "Try again" button that re-submits the same prompt
- Option to retry with a modified prompt (edit before resending)
- Rate limiting: prevent rapid retries (cooldown timer)

### Timeout handling
- Configurable timeout (default 120s? 180s?)
- Warning at 60s: "Still working..." with option to cancel
- Hard timeout that auto-cancels and offers retry

### Partial output recovery
- If kiro-cli wrote files before crashing, detect and surface them
- "Generation partially completed — N files created" with links

## Validation

- **E2E (Playwright):** Trigger a generation that will fail (invalid prompt or mock failure mode) → verify error message appears → click retry → verify new generation starts
- **Integration:** POST to `/api/generate` with a prompt that causes kiro-cli to exit non-zero → verify SSE done event includes error context

## Resolution (2026-09-17, #335)

Closed as mooted, not implemented. The entire premise — server-driven generation
(`POST /api/generate`, SSE stream, retry buttons on a generation modal) — was removed
by #319 (honest-prompt model): `tools/serve.py` has no generate/retry endpoints, the
`assets/services/` SSE stream and `GenerationStream` are gone, and generation UX is now
the copy-paste GeneratePrompt component. With no server generation there is no retry
loop to build; "retry" is re-running the agent with the same prompt, outside this app.
Verified against `tools/serve.py` route inventory 2026-09-17. If server-driven
generation ever returns, reopen with the error-display/timeout ideas above.
