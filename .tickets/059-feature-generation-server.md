---
id: "059"
title: "Feature: tools/serve.py — generation server with SSE streaming"
status: done
priority: medium
blocked_by: []
type: feature
tags: [platform]
---

# Feature: generation server (tools/serve.py)

## Foundation (from spikes 057 + 058)

`tools/serve.py` already exists with the proven core: POST /api/generate, GET /stream (SSE),
POST /cancel. This ticket extends it to production quality.

Key findings baked in:
- Output is burst-buffered (phase-level progress, not token streaming)
- NO_COLOR=1 doesn't work — ANSI always stripped
- SIGTERM must target `kiro-cli-chat` (or use `start_new_session=True` + process group kill)
- 9 matchable output patterns for phase detection (see `.scratch/research/kiro-cli-output-characterization.md`)

## What to build (remaining work)

A FastAPI server that replaces `python -m http.server` and adds generation trigger + progress streaming capabilities.

## Design

### Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/*` | Static file serving (project root) |
| POST | `/api/generate` | Trigger generation (topic or quiz) |
| GET | `/api/generate/{id}/stream` | SSE stream of subprocess output |
| DELETE | `/api/generate/{id}` | Cancel a running generation |

### POST /api/generate

Request body:
```json
{"type": "topic", "slug": "storage-and-table-formats", "title": "Storage & Open Table Formats"}
```
or:
```json
{"type": "quiz", "slug": "storage-and-table-formats", "title": "Storage & Open Table Formats"}
```

Spawns:
- topic: `kiro-cli chat --no-interactive "teach me about {title}"`
- quiz: `kiro-cli chat --no-interactive "generate quick-check questions for {title}"`

Response: `202 Accepted` with `{"task_id": "...", "stream_url": "/api/generate/{id}/stream"}`

### Security

- Bind to 127.0.0.1 only (not 0.0.0.0)
- Command allowlist: only `kiro-cli chat` with validated arguments
- Slug/title validated against `[a-zA-Z0-9 &:_-]` regex
- No shell=True (use subprocess array)

### SSE Stream Format

```
event: step
data: {"current": 1, "total": 4, "label": "Researching sources"}

event: log  
data: {"line": "Searching web for 'storage formats comparison'..."}

event: artifact
data: {"path": "lessons/0002-storage-formats.html"}

event: done
data: {"exit_code": 0, "duration_s": 142}
```

### Dependencies

- `fastapi` + `uvicorn` (added to mise setup)

## Acceptance criteria

- [x] `mise run serve` starts the server on port 8787
- [x] Static files served correctly (replaces python -m http.server) — done in spike
- [x] POST /api/generate spawns subprocess and returns 202 — done in spike
- [x] GET /stream delivers stdout as SSE events in real-time — done in spike
- [x] Cancel kills process group cleanly — done in spike
- [x] Real kiro-cli integration (topic + quiz generation from slug/title)
- [x] Command allowlist prevents arbitrary execution — only kiro-cli chat with validated prompt
- [x] Slug/title validated against safe regex — SAFE_PROMPT_RE, 500 char limit
- [x] Binds to 127.0.0.1 only — default localhost, --lan flag for network access
- [x] SSE events use structured format (phase, artifact path, duration) — phase events + done event with exit_code

## Resolution (2026-08-12)

Server is in production use across all 3 map pages. Features beyond original spec:
- /api/lessons endpoint for dynamic lesson detection
- Auto-navigate to generated lesson on completion
- Noise filtering (checkpoint errors suppressed)
- Mock and long_mock modes for testing
