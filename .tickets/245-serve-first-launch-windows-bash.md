---
id: "245"
title: "serve.py first-launch crashes on Windows: bash subprocess resolves to WSL"
type: bug
status: done
priority: high
blocked_by: []
tags: ["serve", "windows", "first-launch"]
---

# serve.py first-launch crashes on Windows: bash subprocess resolves to WSL

Discovered 2026-08-28 while trying to start the LAN server on a fresh clone
(`workspace/` absent). Server could not start at all on Windows.

## Root cause (researched, reproducible)

`tools/serve.py:142` (`_parse_args`, first-launch branch) runs:

```python
_sp.run(["bash", str(PROJECT_ROOT / "tools" / "init-workspace.sh"), "--default"], check=True)
```

Three failure layers (all confirmed by 2026-08-28 research pass):

1. **Wrong bash.** Python's `subprocess.run(["bash", ...])` resolves to
   `C:\Windows\System32\bash.exe` (WSL), not Git bash. Windows CreateProcess
   searches System32 *before* PATH, so PATH order (Git bash first) is
   irrelevant to subprocess resolution — even though `where.exe bash` and
   interactive pwsh both resolve Git bash first. This is a well-documented
   trap (poetry#3537: System32 bash is the WSL launcher, on PATH everywhere;
   MS CreateProcessA search-order docs). **The only reliable way to target
   Git bash is an absolute path** (`C:\Program Files\Git\bin\bash.exe`,
   discovered via registry `HKLM\SOFTWARE\GitForWindows\InstallPath` or
   derived from `git.exe`) — NOT name resolution, and NOT `cwd=`. `shell=True`
   makes it worse (routes through cmd.exe → back to System32/WSL).
2. **WSL bash can't read Windows paths.** `D:\code\...` → backslashes eaten
   (`D:codeteach-metools...`, exit 127); `D:/code/...` (`.as_posix()`) →
   still invalid, WSL needs `/mnt/d/...`.
3. **`python3` name + POSIX `ln -s`.** Even under Git bash,
   `tools/init-workspace.sh` (assets-symlink block) calls `python3` for a
   relpath computation, which Git bash doesn't provide (Windows interpreter is
   `python`; `python3` often resolves to a zero-byte WindowsApps Store alias
   stub that MSYS can't even stat) → `set -e` aborts before writing
   `lessons/index.html`. It also uses `ln -s`, which on Windows produces a
   broken text-stub symlink (per AGENTS.md "git symlinks on Windows are text
   files"). Dirs + MISSION/RESOURCES exist by then, so serve.py's *bare*
   `workspace/`-exists check passes on the next run — masking a half-built
   workspace (index.html silently missing).

**Correction to the earlier option-B assumption:** passing `cwd=PROJECT_ROOT`
does NOT fix layer 1. cwd translation only helps *after* the right bash is
chosen; it does not change which `bash.exe` CreateProcess selects (still WSL).
So a cwd-relative tweak leaves the primary crash intact on any box where WSL
is installed. See `.scratch/research/245-bash-subprocess.md`.

## Fix options (updated 2026-08-28 with research + code/docs review)

| | Option | Cost | Verdict |
|---|---|---|---|
| A | No code change — run `bash tools/init-workspace.sh --default` once from pwsh (PATH resolves Git bash), tolerate the python3 abort | 1 command | Unblocks only this machine; not a fix |
| B | serve.py subprocess tweak — `cwd=PROJECT_ROOT` + relative script name + `check=False` | 1–3 lines | **Rejected: does not fix layer 1.** cwd doesn't change which bash CreateProcess picks (still WSL). Would need explicit `find_git_bash()` absolute-path resolution to work at all, and still leaves layers 2–3. |
| C | **Port scaffold to pure Python** (`tools/init-workspace.py`); serve.py calls it **in-process** (`import`), not via subprocess; keep `.sh` as a thin passthrough (or retire) | ~60–80 lines | **Recommended.** Removes bash, `python3`-name, and `ln -s` dependencies at once. Matches the established sr-* pattern and the #229 precedent. In-process call sidesteps the interpreter-name problem entirely. |
| D | Sidestep — serve an examples workspace | 0 | Not the live workspace; escape hatch only |

**Recommendation flipped to C** (was B). Rationale from the research pass:

- **B is not actually durable.** The core failure (layer 1) is bash resolution,
  which `cwd=` cannot fix — only an absolute Git-bash path would, and that
  reintroduces registry/discovery fragility across scoop/winget/portable Git
  installs. B also leaves the `python3` + `ln -s` layers.
- **C matches existing project convention.** Ticket #229 (DONE) fixed this
  *exact* Windows failure class in the `verify` task by removing bash and
  bare-`python` (switched to `uv run python`). All `sr-*` tools are pure
  Python invoked directly, no shell intermediary — that IS the pattern the
  ticket's option C references.
- **In-process beats subprocess.** serve.py already runs under the project
  venv; `from init_workspace import init_workspace; init_workspace(default=True)`
  avoids spawning a child process and the `python`-vs-`python3` name issue
  altogether. No `sys.executable` guessing needed.
- **Skip the assets symlink on Windows.** serve.py mounts `/assets` from
  PROJECT_ROOT (`app.mount("/assets", ...)`), so the workspace-local symlink
  is only needed for `python -m http.server` debugging. The Python port should
  create it on POSIX and skip (or junction) on Windows rather than emit a
  broken text stub — no hard failure either way.

If C is chosen, record it in a new ADR (0011) per AC below — no ADR currently
covers workspace init / first-launch / serve.py architecture (all 10 existing
ADRs checked).

Full evidence: `.scratch/research/245-{bash-subprocess,portable-init,code-review,docs-config}.md`.

## Additional issues surfaced by review (fold into this ticket)

- **Inconsistent "already initialized" guard.** serve.py checks
  `(PROJECT_ROOT / "workspace").exists()` (bare dir); init-workspace.sh checks
  `$WORKSPACE/lessons` exists. A half-built workspace (dirs but no
  `lessons/index.html`) passes serve.py's check and is never repaired.
  **Standardize on the stricter `workspace/lessons` guard** so a partial init
  self-heals on the next serve.
- **cp1252 stdout.** init-workspace.sh prints `✓`/`✗`; a Python port must be
  ASCII-safe or set `PYTHONIOENCODING=utf-8` (AGENTS.md quirk).

## Out of scope (create follow-up tickets, don't expand this one)

- `serve` / `serve:lan` mise tasks use bare `python` (the unreliability #229
  flagged). If `mise run serve` can't reach `_parse_args` on a fresh Windows
  box, fixing serve.py's subprocess is necessary but not sufficient. Verify
  during implementation; if it's a separate blocker, file a follow-up to move
  serve tasks to `uv run python` (mirrors #229).
- `serve:restart` uses Unix-only `lsof`/`kill -9` (Windows-broken; #229 left
  out of scope). Follow-up ticket.

## Acceptance criteria

- [x] On a Windows machine with no `workspace/`, `python tools/serve.py --lan`
      starts successfully and serves `http://192.168.x.x:8787` with a fully
      scaffolded workspace (dirs + MISSION/RESOURCES + `lessons/index.html`),
      no bash/`python3`/WSL dependency
- [x] No bare `bash`/`python3` subprocess in the first-launch path (C: init
      called in-process; `.sh` retained only as a thin passthrough or retired)
- [x] `check=True` crash path eliminated: init failure produces a clear
      warning, not a traceback
- [x] "Already initialized" guard standardized on `workspace/lessons` so a
      half-built workspace self-heals on next serve (serve.py + script agree)
- [x] Assets symlink: created on POSIX, skipped/junctioned on Windows without
      hard failure (serve.py mounts `/assets` from PROJECT_ROOT regardless)
- [x] Port output is ASCII-safe (or sets `PYTHONIOENCODING=utf-8`) — no cp1252
      crash on `✓`/`✗`
- [x] Linux/macOS first-launch still works (no regression) — validate on WSL
- [x] ADR 0011 recorded (option C changes the init architecture)
- [x] Follow-up tickets filed for out-of-scope items IF confirmed blocking:
      serve/serve:lan bare-`python`, serve:restart `lsof`/`kill`

## Resolution (2026-08-28)

Option C: ported scaffold to tools/init_workspace.py (pure Python, importable); serve.py calls init_workspace(default=True) in-process (no bash/python3/symlink dep); guard standardized on workspace/lessons; check=True crash replaced with graceful warning+exit; assets symlink POSIX-only (Windows skip); ASCII-safe output; init-workspace.sh now a thin passthrough; mise task + AGENTS.md updated; ADR 0011 recorded. Out-of-scope follow-ups filed as #247 (serve bare-python) and #248 (serve:restart lsof/kill).
