---
id: "060"
title: "Feature: generation progress modal — live checklist in browser"
status: open
priority: medium
blocked_by: ["058", "059"]
type: feature
---

# Feature: generation progress modal

## What to build

Replace the "copy command" modal on map pages with a live generation progress UI that shows a step checklist, streaming log, and completion actions.

## Design

### Modal States

**Confirming:**
```
┌─ Generate: Storage & Table Formats ──┐
│                                       │
│  This will research and write a       │
│  lesson on this topic (~3-5 min).     │
│                                       │
│  [Start Generation]    [Cancel]       │
└───────────────────────────────────────┘
```

**Running:**
```
┌─ Generating: Storage & Table Formats ─┐
│                                        │
│  ✓ Researching sources      (0:42)     │
│  ◐ Writing lesson...        (1:15)     │
│  ○ Generating SR cards                 │
│  ○ Writing reference doc               │
│                                        │
│  ▼ Log (click to expand)               │
│                                        │
│  Elapsed: 1:57         [Cancel]        │
└────────────────────────────────────────┘
```

**Complete:**
```
┌─ ✓ Generated: Storage & Table Formats ┐
│                                        │
│  ✓ Researching sources      (0:42)     │
│  ✓ Writing lesson           (1:33)     │
│  ✓ Generating SR cards      (0:28)     │
│  ✓ Writing reference doc    (0:19)     │
│                                        │
│  Total: 3:02                           │
│                                        │
│  [Open Lesson →]    [Close]            │
└────────────────────────────────────────┘
```

### Browser Implementation

- Vanilla JS (no framework)
- EventSource connects to SSE stream URL
- Pattern matching on `event: step` / `event: log` / `event: done`
- Elapsed timer updates every second
- Collapsible log section (last 20 lines visible)
- Browser Notification API on completion (if tab backgrounded)

### Step Detection (Tier 2 — pattern matching)

```javascript
const STEP_PATTERNS = [
  [/research|search|looking up|finding sources/i, "Researching sources"],
  [/writing|drafting|composing.*lesson/i, "Writing lesson"],
  [/generat.*(?:SR|spaced|question|quiz)/i, "Generating SR cards"],
  [/reference|companion/i, "Writing reference doc"],
  [/saving|wrote|created.*\.html/i, "Saving files"],
];
```

## Acceptance criteria

- [ ] "Generate" button shows confirmation modal first
- [ ] On confirm: POST to server, open SSE connection
- [ ] Checklist updates in real-time as steps are detected
- [ ] Elapsed timer runs during generation
- [ ] Collapsible log shows raw output
- [ ] On completion: "Open Lesson →" button appears
- [ ] On error: error message + retry button
- [ ] Cancel button sends DELETE and shows cancelled state
