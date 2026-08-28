---
id: "248"
title: "serve:restart uses Unix-only lsof/kill (broken on Windows)"
status: backlog
blocked_by: []
tags: ["serve", "windows"]
---

# serve:restart uses Unix-only lsof/kill (broken on Windows)

Surfaced during #245 (docs/config review). The `serve:restart` mise task runs
`lsof -ti :8787 | xargs kill -9 ...` — Unix-only; fails on Windows. #229
explicitly listed this among remaining Windows-broken tasks left out of scope.

## What to build

Make `serve:restart` cross-platform — e.g. a small Python helper that finds and
kills the process on the port (psutil, or `netstat`/`taskkill` on Windows and
`lsof`/`kill` on POSIX), invoked via `python tools/...`.

## Acceptance criteria

- [ ] `mise run serve:restart` kills the existing server and restarts on Windows
- [ ] Still works on Linux/macOS
- [ ] No bare `lsof`/`kill` shell dependency
