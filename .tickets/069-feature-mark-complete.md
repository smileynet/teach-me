---
id: "069"
title: "Feature: mark topic as complete — button on lesson page"
status: open
priority: high
blocked_by: ["068"]
type: feature
---

# Feature: mark topic as complete

## What to build

A "Mark as complete" button at the bottom of each lesson page (via lesson-actions.js) that sets the topic status to `complete` in MAP.md.

### UX
- Button appears in the action bar: "✓ Mark as complete"
- On click: POST to `/api/map/{domain}/{slug}/status` with `{"status": "complete"}`
- On success: button changes to "✓ Completed" (disabled, green)
- On page load: if topic is already complete, show the disabled state

### Detection
- lesson-actions.js needs to know its topic slug and parent domain
- Add `data-topic-slug` and `data-domain` attributes to the script tag
- Or: infer from `/api/questions` and `/api/lessons` matching

### What "complete" means (for now)
- User self-declares: "I understand this topic well enough"
- No quiz gate required (that's a backlog exploration — see 064)
- Reversible: clicking again could un-mark (or just don't show an undo for now)

## Acceptance criteria

- [ ] "Mark as complete" button visible on lesson pages
- [ ] Click updates MAP.md status to `complete`
- [ ] Map page shows green node after marking complete
- [ ] Already-complete topics show disabled button on load

## Validation

- **Integration:** POST status update → verify MAP.md changed → GET `/api/map/{domain}` shows `complete`
- **E2E (Playwright):** Open lesson → click "Mark as complete" → navigate to map → verify node is green
