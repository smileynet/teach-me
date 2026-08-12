---
id: "057"
title: "Spike: subprocess + SSE streaming — prove the pattern works"
status: open
priority: high
blocked_by: []
type: spike
---

# Spike: subprocess + SSE streaming

## Question to answer

Can a minimal Python server spawn a subprocess and stream its stdout to a browser via Server-Sent Events in real-time?

## What to build

A ~60-line `tools/serve.py` (FastAPI + uvicorn) that:
1. Serves static files from the project root
2. POST `/api/generate` — spawns a test subprocess, returns task_id + stream URL
3. GET `/api/generate/{id}/stream` — SSE stream of stdout lines as they arrive

Test with a mock command (not kiro-cli yet):
```bash
echo "[STEP:1/3] Researching..." && sleep 2 && echo "[STEP:2/3] Writing..." && sleep 2 && echo "[STEP:3/3] Done" && sleep 1 && echo "[DONE]"
```

Plus a minimal HTML test page that connects via EventSource and renders a checklist.

## Success criteria

- [ ] POST to `/api/generate` spawns subprocess and returns 202
- [ ] EventSource receives lines in real-time (not buffered until process ends)
- [ ] 3 simulated steps appear one at a time with ~2s gaps
- [ ] Process exit triggers a final SSE event
- [ ] Works in Chrome and Firefox
- [ ] Server stays responsive during subprocess execution
- [ ] Zero external deps beyond fastapi + uvicorn

## What this does NOT test

- Real kiro-cli invocation (that's spike 058)
- Full modal UI integration
- Error handling / cancellation
- Concurrent tasks
