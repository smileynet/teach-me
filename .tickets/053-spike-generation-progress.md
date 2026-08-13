---
id: "053"
title: "Spike: generation progress checklist — live feedback during topic creation"
status: done
priority: low
blocked_by: []
type: spike
---

# Spike: generation progress checklist

## What to test

When a user triggers topic generation from the map page, can we show a dynamic checklist of steps (researching → writing lesson → generating diagrams → creating SR cards) with live status updates?

## The challenge

teach-me has no backend server — pages are static HTML. The agent runs in the terminal. Bridging these requires one of:

1. **File polling** — agent writes status to `.scratch/generation-status/{slug}.json`, page polls with JS `fetch()` (requires serving from localhost)
2. **Terminal-only** — the modal just shows the CLI command, user watches progress in terminal (current approach)
3. **Tiny local server** — ~50 LOC Python server that accepts POST from the agent and exposes GET for the browser (Tier 2 from research)

## What to build in the spike

Test approach 1 (file polling) since we already have `python -m http.server` running:

1. Agent writes step status to `.scratch/generation-status/ingestion.json`:
   ```json
   {"steps": [
     {"name": "Research", "status": "complete"},
     {"name": "Write lesson", "status": "in-progress"},
     {"name": "Generate diagrams", "status": "pending"},
     {"name": "Create SR cards", "status": "pending"}
   ]}
   ```
2. Browser page polls this file every 2s and updates a checklist UI
3. On completion, the page refreshes or updates the topic card state

## Questions to answer

1. Does file polling via `fetch()` from a static server work reliably?
2. Is the latency acceptable (2s polling interval)?
3. Is this worth the complexity vs "just watch the terminal"?
4. Does the agent naturally report these steps already (could we parse its output)?

## Success criteria

- [ ] Checklist UI shows steps with status indicators (○ pending, ◐ in-progress, ✓ complete)
- [ ] Status updates within 2-3 seconds of agent writing the file
- [ ] Final state: all steps ✓, topic card updates to "Open lesson →"
- [ ] Evaluate: is this actually better than watching the terminal?
## Resolution (closed 2026-08-11)

Superseded by tickets 057-061 (browser-triggered generation with SSE streaming). Those tickets cover the same scope with a more complete design.
