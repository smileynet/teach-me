---
id: "247"
title: "serve/serve:lan mise tasks use bare python (unreliable on Windows)"
status: backlog
blocked_by: []
priority: high
tags: ["serve", "windows"]
---

# serve/serve:lan mise tasks use bare python (unreliable on Windows)

Surfaced during #245 (docs/config review). The `serve` and `serve:lan` mise
tasks call bare `python tools/serve.py`, relying on mise's venv PATH injection
— documented as unreliable on Windows non-interactively (shim-recursion trap,
AGENTS.md). Ticket #229 fixed the identical class in the `verify` task by
switching to `uv run python` (uv already declared + is the dep installer).

#245 fixed serve.py's *internal* first-launch bash subprocess, but if
`mise run serve` can't reliably reach `_parse_args` on a fresh Windows box, the
task-level bare-`python` is a separate blocker.

## What to build

Switch `serve`, `serve:lan` (and consider the whole serve family) to
`uv run python tools/serve.py ...`, mirroring #229. Confirm `mise run serve`
starts on a fresh Windows box.

## Acceptance criteria

- [ ] `mise run serve` and `mise run serve:lan` start reliably on Windows
- [ ] Uses `uv run python` (not bare `python`), consistent with #229
- [ ] Linux/macOS unaffected
