---
id: "057"
title: "Spike: subprocess + SSE streaming — prove the pattern works"
status: done
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

- [x] POST to `/api/generate` spawns subprocess and returns 202
- [x] EventSource receives lines in real-time (not buffered until process ends)
- [x] 3 simulated steps appear one at a time with ~2s gaps
- [x] Process exit triggers a final SSE event
- [x] Works in Chrome and Firefox (standard EventSource API)
- [x] Server stays responsive during subprocess execution
- [x] Zero external deps beyond fastapi + uvicorn

## Bonus (beyond original scope)

- Cancellation endpoint (`POST /api/generate/{id}/cancel`) with process group kill
- Pattern-based phase detection from spike 058 findings
- SSE heartbeat during silence periods
- ANSI stripping on all output

## Resolution (2026-08-11)

**Answer: Yes.** FastAPI + asyncio + subprocess works cleanly for this pattern.

Architecture: POST spawns subprocess (start_new_session=True), returns 202 + task_id.
Background thread reads stdout line-by-line into a list. SSE endpoint polls the list
with 100ms intervals, yielding events as they appear. Process exit triggers a `done` event.

Files:
- `tools/serve.py` (195 lines) — server with all endpoints
- `tools/sse-test.html` — test page with EventSource + phase checklist

## What this does NOT test

- Real kiro-cli invocation (that's spike 058)
- Full modal UI integration
- Error handling / cancellation
- Concurrent tasks
