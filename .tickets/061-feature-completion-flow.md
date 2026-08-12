---
id: "061"
title: "Feature: generation completion flow — auto-update map cards"
status: done
priority: medium
blocked_by: ["059", "060"]
type: feature
---

# Feature: generation completion flow

## What to build

After a generation completes successfully, automatically update the map page to reflect the new content — change the topic card from "Generate" to "Open lesson →", update the SVG node color, and optionally trigger a browser notification.

## Design

### On successful generation:

1. SSE `event: done` fires with `exit_code: 0`
2. Modal shows "✓ Generated" state with "Open Lesson →" button
3. In the background:
   - Fetch the new lesson filename from server (or infer from `event: artifact`)
   - Update the topic card DOM: replace "Generate" button with lesson link
   - Update the badge from "○ not started" to "◐ in progress"
   - Optionally: re-render SVG node color (complex — may skip for v1)
4. If browser tab was backgrounded: fire a Notification ("Lesson ready: Storage & Table Formats")

### On error:

1. SSE `event: error` or stream closes with non-zero exit
2. Modal shows error state with last few log lines
3. "Retry" button re-triggers the same generation
4. Topic card remains unchanged

### Browser notifications

```javascript
if (document.hidden && Notification.permission === 'granted') {
  new Notification('teach-me', { body: `Lesson ready: ${title}` });
}
```

Request permission on first "Start Generation" click (not on page load — avoids annoying prompts).

## Acceptance criteria

- [ ] Successful generation updates the topic card in-place (no page reload needed)
- [ ] "Open Lesson →" link points to the actual generated file
- [ ] Badge updates from "not started" to "in progress"
- [ ] Browser notification fires when tab is backgrounded
- [ ] Error state shows meaningful message + retry
- [ ] Works with both topic and quiz generation

## Resolution (2026-08-12)

**Superseded by 068.** Auto-update of MAP.md status after generation is handled as part of the cohesive map flow (068), alongside the suggestion banner and status API endpoint.
