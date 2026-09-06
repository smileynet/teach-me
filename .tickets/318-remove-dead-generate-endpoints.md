---
id: "318"
title: "Remove dead /api/generate SSE endpoints from serve.py (replaced by honest prompt UI)"
status: open
blocked_by: []
validation_criteria:
  - "serve.py no longer exposes /api/generate, /api/generate/{id}/stream, or /cancel; the GenerationTask/mock-cmd/SSE machinery is removed"
  - "mise run serve + serve-workspace skill checks still pass (workspace mount + /api/map unaffected)"
tags: ["platform"]
---

# Remove dead /api/generate SSE endpoints from serve.py (replaced by honest prompt UI)

## Context

#317 replaced the frontend's incomplete autogeneration (an SSE stream that spawned `kiro-cli chat`
on the server host and blindly flipped a topic to `complete` when the process exited) with an honest
prompt panel — the user copies a prompt and runs it with an agent in the repo. The frontend SSE client
(`generation.js`, `GenerationStream.js`) was removed in #317.

The **server side is now dead code**: nothing calls `/api/generate`. About ~200 lines of `serve.py`
(the `GenerationTask` model, `strip_ansi`/`detect_phase` helpers, `MOCK_CMD`/`LONG_MOCK_CMD`,
`SAFE_PROMPT_RE`, and the three endpoints + `_sse_generator`) exist only to serve requests that can no
longer arrive.

## What to build

Remove the generation subsystem from `tools/serve.py`:
- `POST /api/generate`, `GET /api/generate/{id}/stream`, `POST /api/generate/{id}/cancel`
- `GenerationTask`, the `TASKS` registry, `_read_output`, `_sse_generator`
- `MOCK_CMD`, `LONG_MOCK_CMD`, `SAFE_PROMPT_RE`, `detect_phase`, `strip_ansi` (if unused elsewhere)
- The module docstring lines describing those endpoints

Leave the core server intact: workspace mount at `/`, `/assets`, and the `/api/map/*` status endpoints.

## Acceptance criteria

- [ ] `serve.py` no longer defines `/api/generate*` routes or the `GenerationTask`/SSE/mock machinery
- [ ] `grep -rn "api/generate\|GenerationTask\|MOCK_CMD" tools/ assets/` returns nothing
- [ ] `mise run serve:bg` starts, serves a workspace, and `/api/map/{domain}` still works
- [ ] `mise run verify` passes (only the pre-existing #316 drift may remain)

## Notes

- Kept separate from #317 to keep that fix scoped to the user-facing behavior; this is a pure
  server-side dead-code removal with its own (serve.py) test surface.
- Confirm no test or skill references the mock commands before deleting (`serve-workspace` SKILL
  documents the status API, not `/api/generate`).
