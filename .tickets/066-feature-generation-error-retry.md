---
id: "066"
title: "Feature: error handling and retry for generative operations"
status: open
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
