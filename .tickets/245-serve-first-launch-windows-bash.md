---
id: "245"
title: "serve.py first-launch crashes on Windows: bash subprocess resolves to WSL"
type: bug
status: open
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

Two failure layers:

1. **Wrong bash.** Python's `subprocess.run(["bash", ...])` resolves to
   `C:\Windows\System32\bash.exe` (WSL), not Git bash. Windows CreateProcess
   searches System32 *before* PATH, so PATH order (Git bash first) is
   irrelevant to subprocess resolution — even though `where.exe bash` and
   interactive pwsh both resolve Git bash first.
2. **WSL bash can't read Windows paths.** `D:\code\...` → backslashes eaten
   (`D:codeteach-metools...`, exit 127); `D:/code/...` (`.as_posix()`) →
   still invalid, WSL needs `/mnt/d/...`.

Latent layer 3: even under Git bash, `tools/init-workspace.sh:85` calls
`python3`, which Git bash doesn't provide → `set -e` aborts before writing
`lessons/index.html`. Dirs + MISSION/RESOURCES would exist by then, which is
enough for serve.py to skip the init branch on the next attempt, so this
layer is tolerable-but-ugly.

## Fix options (from research session 2026-08-28)

| | Option | Cost |
|---|---|---|
| A | No code change — run `bash tools/init-workspace.sh --default` once from pwsh (PATH resolves Git bash), tolerate the python3 abort | 1 command, unblocks only this machine |
| B | Minimal fix in serve.py — invoke with `cwd=PROJECT_ROOT` and relative script name `"tools/init-workspace.sh"` (cwd gets translated under both WSL and Git bash); optionally `check=False` + verify workspace dir exists afterward so script quirks degrade instead of crashing | 1–3 lines, durable |
| C | Port init to Python (`tools/init-workspace.py`), keep `.sh` as a mise shim — matches existing `sr-*` Python-tool pattern, removes bash dependency entirely | ~60 lines, most robust |
| D | Sidestep — serve an examples workspace (`--workspace examples/ink-godot`); init branch never triggers | 0, but not the live workspace |

Recommendation: **B** for this ticket (small, fixes every Windows box); fold
in a `python3`→portable guard in init-workspace.sh if cheap. C is the
endgame if first-launch reliability matters cross-platform.

## Acceptance criteria

- [ ] On a Windows machine with no `workspace/`, `python tools/serve.py --lan`
      starts successfully and serves `http://192.168.x.x:8787` (workspace
      auto-created or gracefully degraded)
- [ ] `check=True` crash path eliminated: init failure (if any) produces a
      clear warning, not a traceback
- [ ] Linux/macOS first-launch still works (no regression)
- [ ] Decision recorded (B vs C) — if C, note in `.memory/adr/` since it
      changes the init architecture
