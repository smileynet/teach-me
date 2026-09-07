---
id: "318"
title: "Remove dead /api/generate SSE endpoints from serve.py (replaced by honest prompt UI)"
status: done
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

- [x] `serve.py` no longer defines `/api/generate*` routes or the `GenerationTask`/SSE/mock machinery
- [x] `grep -rn "api/generate\|GenerationTask\|MOCK_CMD" tools/ assets/` returns nothing
- [x] `mise run serve:bg` starts, serves a workspace, and `/api/map/{domain}` still works
- [x] `mise run verify` passes fully green (no `--no-verify`; the #316 drift caveat is obsolete — #316 is fixed)

## Notes

- Kept separate from #317 to keep that fix scoped to the user-facing behavior; this is a pure
  server-side dead-code removal with its own (serve.py) test surface.
- Confirm no test or skill references the mock commands before deleting (`serve-workspace` SKILL
  documents the status API, not `/api/generate`).

## Resolution

Removed the dead `/api/generate` generation subsystem. Research + review (`.scratch/research/318-dead-code-removal.md`,
`.scratch/review/318-serve-boundary.md`, `.scratch/review/318-caller-sweep.md`) found the ticket
under-scoped it: the removal spans **4 files** (not 1) and **8 orphaned imports** (not 5).

Deleted:
- `tools/serve.py` (~180 lines): the 3 routes (`/api/generate`, `/stream`, `/cancel`), `GenerationTask`,
  `TASKS`, `_read_output`, `_sse_generator`, `GenerateRequest`, `MOCK_CMD`/`LONG_MOCK_CMD`,
  `SAFE_PROMPT_RE`/`MAX_PROMPT_LEN`, `strip_ansi`/`ANSI_RE`, `detect_phase`/`PHASE_PATTERNS`. Pruned 8
  now-orphaned imports (`asyncio`, `os`, `re`, `signal`, `subprocess`, `uuid`, `AsyncGenerator`,
  `StreamingResponse`). Rewrote the docstring + FastAPI title (it's a workspace/status server now).
- `library/iceberg-workspace/lessons/0001-iceberg-metadata-tree.html`: the dead `offerQuiz()` script
  (defined, never wired to any button) that fetched `/api/generate`.
- `tools/sse-test.html`: deleted (manual SSE harness for the removed endpoints; no inbound links).
- `.kiro/skills/teach/SKILL.md`: rewrote the false "Generation is live / hits `/api/generate` / never
  show copy-paste commands" line — it stated the exact opposite of the shipped honest-prompt UI (#317/#319).

Net: 424 deletions, 12 insertions.

**Verified:**
- `python -m py_compile tools/serve.py` clean.
- Repo sweep `grep -rn "api/generate|GenerationTask|MOCK_CMD|offerQuiz|createGenerationStream|stream_url"`
  across tools/ assets/ library/ .kiro/ → empty (outside historical `.tickets/` + ADR roster, left as record).
- `mise run verify` fully green, committed through the pre-commit hook (no `--no-verify`).
- Runtime: `serve:bg` on library/gltf-format — `GET /api/map/gltf-format` → 200, lesson page → 200,
  `POST /api/generate` → 405 (route gone, not a crash). Surviving 10 endpoints intact.

Committed 1487d2b.
