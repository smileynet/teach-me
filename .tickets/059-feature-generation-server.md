---
id: "059"
title: "Feature: tools/serve.py — generation server with SSE streaming"
status: open
priority: medium
blocked_by: ["057", "058"]
type: feature
---

# Feature: generation server (tools/serve.py)

## What to build

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

- [ ] `mise run serve` starts the server on port 8080
- [ ] Static files served correctly (replaces python -m http.server)
- [ ] POST /api/generate spawns kiro-cli subprocess
- [ ] GET /stream delivers stdout as SSE events in real-time
- [ ] DELETE cancels with SIGTERM
- [ ] Command allowlist prevents arbitrary execution
- [ ] Binds to 127.0.0.1 only
