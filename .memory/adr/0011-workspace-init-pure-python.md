# 0011 — Workspace init is pure Python, called in-process

**Status:** accepted
**Date:** 2026-08-28

## Context

`serve.py`'s first-launch branch auto-created the default `workspace/` by shelling
out to `bash tools/init-workspace.sh --default` with `check=True`. On Windows this
could not start the server at all (ticket #245):

1. `subprocess.run(["bash", ...])` resolves to `C:\Windows\System32\bash.exe` (WSL),
   not Git bash, because Windows CreateProcess searches System32 before PATH. `cwd=`
   does not change which `bash.exe` is selected; only an absolute Git-bash path would,
   and that is fragile across scoop/winget/portable installs.
2. WSL bash can't read Windows-style paths (`D:\...` → exit 127).
3. Even under Git bash, the script called `python3` (absent on Windows; often a
   zero-byte WindowsApps alias stub) for a relpath computation and used `ln -s`
   (a broken text-stub symlink on Windows) — aborting under `set -e` after the dirs
   existed but before `lessons/index.html` was written, leaving a half-built workspace
   that the old bare `workspace/`-exists guard never repaired.

The project already had a precedent for this exact Windows failure class: ticket #229
removed bash and bare-`python` from the `verify` task, and every `sr-*` tool is a plain
Python script invoked directly with no shell intermediary.

Options considered: (A) manual one-off command — unblocks one machine, not a fix;
(B) tweak the serve.py subprocess (`cwd=` + relative name) — rejected, does not fix the
bash-resolution layer; (C) port the scaffold to pure Python called in-process;
(D) sidestep by serving an examples workspace — escape hatch only.

## Decision

Adopt option C. The scaffold logic lives in `tools/init_workspace.py` as an importable
function `init_workspace(workspace=None, *, default=False)`. `serve.py` calls it
**in-process** (`from init_workspace import init_workspace`) on first launch — no child
process, so the `python`-vs-`python3` name problem never arises.

- The "already initialized" guard is standardized on `workspace/lessons` (both serve.py
  and the initializer) so a half-built workspace self-heals on the next serve.
- The workspace-local `assets` symlink is created on POSIX only; on Windows it is
  skipped with a warning, because serve.py mounts `/assets` from PROJECT_ROOT (the
  symlink is only needed for `python -m http.server` debugging on POSIX).
- Output is ASCII-safe (Windows cp1252 stdout can't encode `✓`/`✗`).
- `init_workspace()` returns a structured dict (`status`, `created`, `warnings`) per the
  project's validation-contract convention.
- `tools/init-workspace.sh` is retained as a thin passthrough (finds an interpreter,
  execs the `.py`) for POSIX callers/muscle memory; the `init-workspace` mise task and
  AGENTS.md now point at `python tools/init_workspace.py`, matching the sr-* pattern.

## Consequences

- First launch works on Windows with no bash/WSL/`python3`/symlink dependency; init
  failure degrades to a clear message instead of a `check=True` traceback.
- One source of truth for scaffolding (the `.py`); the `.sh` is a forwarder that can be
  deleted later without behavior change.
- The Windows workspace has no local `assets` symlink — fine under serve.py, but
  `python -m http.server` in the workspace dir won't resolve `../assets/...` there
  (documented; use serve.py, which mounts `/assets`).
- Out of scope, left for follow-up tickets: `serve`/`serve:lan` still use bare `python`
  (the unreliability #229 flagged), and `serve:restart` uses Unix-only `lsof`/`kill`.
