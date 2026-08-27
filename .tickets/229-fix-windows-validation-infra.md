---
id: "229"
title: "Fix Windows-breaking validation infra: mise verify task + verify-links symlink handling"
status: done
priority: medium
blocked_by: []
tags: [infra, windows, validation]
---

# Fix Windows-breaking validation infra: mise verify task + verify-links symlink handling

## Problem

Two pre-existing bugs make the project's canonical validation gate unusable on Windows. Surfaced while validating lesson #217 — neither is a #217 regression. Full diagnosis with file:line + patch snippets: `.scratch/subagent-review/validation-bugs.md`; cross-platform research: `.scratch/subagent-research/{mise-crossplatform,symlink-link-check}.md`.

### Bug 1 — `mise run verify` fails on Windows at step 1

Two independent defects in `[tasks.verify]` (`mise.toml:314-324`):
- **1a `/dev/null` bash-ism** (`mise.toml:317`) — `> /dev/null` is not a valid sink under mise's Windows task shell (cmd uses `NUL`, PowerShell `Out-Null`). Fails unconditionally.
- **1b bare `python`** (`mise.toml:317-323`) — mise's venv PATH injection is unreliable on Windows non-interactively (documented shim-recursion in AGENTS.md); only `.venv\Scripts\python.exe` resolves reliably.

### Bug 2 — `verify-links.py` false-positive storm on Windows

`examples/*/assets` is a git symlink checked out as a ~12-byte TEXT STUB file (content e.g. `../../assets`), not a directory. `check_file()` (`tools/verify-links.py:78-80`) does `(parent/href).resolve()` then `.exists()`, so every lesson's `../assets/*.css|js` resolves under a non-directory → "file not found". Result: 218 false failures across 65 files, drowning any real broken link. `serve.py:458` mounts `/assets` from `PROJECT_ROOT/assets`, so the disk resolver looks in the wrong place. `Path.is_symlink()` returns False for these stubs — must special-case the assets mount.

## Fixes (from review)

**Bug 1** (`mise.toml` verify task):
- Replace `> /dev/null` with `--out .scratch/verify-smoke.svg` (draw-diagram supports `--out`).
- Prefix each command with `uv run ` — `uv` already declared (`mise.toml:8`), deps installed via uv (`mise.toml:29`); sidesteps the shim-recursion bug, no bash dependency.

**Bug 2** (`tools/verify-links.py`):
- Add helper `_resolve_via_assets_mount(href)` (~`:33`) that maps any href traversing an `assets/` segment onto `PROJECT_ROOT/assets` (mirrors `serve.py:458`).
- Use it as a FALLBACK at `:80` — only when the literal `target.exists()` misses. No false negatives: genuine misses still report.

**Scope note:** sibling tasks `open-lesson` (`:47-49`), `serve:restart` (`:72`), `maps:regenerate` (`:277-289`) have the same bash-ism problem (maps:regenerate already documented broken in AGENTS.md). Out of scope here unless trivial — track separately if not fixed.

## Acceptance criteria

- [x] `mise run verify` runs to completion (green) on Windows — EXIT 0, all 6 steps + ink transcripts pass
- [x] verify task uses `uv run python` and no `/dev/null` — converted `run` to array form (mise runs array in series; multi-line string only ran the first command under Windows cmd); inline `--data` JSON replaced with `tools/smoke-draw-diagram.py` (no shell quoting)
- [x] `verify-links.py` reports 0 false positives for `assets/` links — 67 files verified, 0 broken (was 218 false failures)
- [x] `verify-links.py` still FAILS on a genuinely broken link — counter-tested: `../../assets/DOES-NOT-EXIST.css` + `./nonexistent-local.js` both caught, real `style.css` passed; temp file removed
- [x] No regression: `check-svg-vars` (15 files, no hex), `lint-html` (0 errors), map tests (37 passed) all green under the fixed task

### Additional fixes required (found during verification)

- **`verify-interactive.py` used Unix-only `os.setsid`/`os.killpg`** → added `_terminate_server()` + `CREATE_NEW_PROCESS_GROUP` on win32; spawn server with `--workspace` (root `workspace/` absent → `examples/godot-gamedev`); `find_test_page` returns None → graceful skip instead of a 404 fallback.
- **Real defect caught by the fixed gate:** the #217 quiz page path mismatch — the lesson action bar derives the quiz URL as `quiz/{id}-quiz.html` relative to the lesson (`LessonActions.js:24`), i.e. `lessons/blender-texture-prep/quiz/...`, but the quiz was generated in flat `lessons/quiz/`. Regenerated to the subfolder; verify-interactive now 8/8 pass (quiz nav 200, clean console).

### Follow-up (separate ticket-worthy)

- `generate-quiz-page.py` hardcodes `depth=2` (`:66`) and depth-2 relative back-links. A quiz in a per-domain subfolder (`lessons/{domain}/quiz/`, depth 3) gets wrong `../../assets` and back-link prefixes. → **Filed and RESOLVED as #230** (depth-aware generation; all 6 links 200; no depth-2 regression).
- Sibling bash-ism tasks (`open-lesson`, `serve:restart`, `maps:regenerate`) remain Windows-broken — out of scope here.

## CI enforcement (investigated 2026-08-27)

`mise run verify` is **intentionally not run on push** — per #131 (done, priority high), CI was replaced with git hooks while the architecture is in flux:
- `.githooks/pre-commit` runs `mise run verify` and blocks the commit on failure; pre-push runs the full verify incl Playwright. `core.hooksPath=.githooks` is wired by `mise run setup`.
- GitHub Actions `verify.yml` is `workflow_dispatch` (manual) on `ubuntu-latest` — so these fixes are exercised on Linux when dispatched, and enforced locally on every commit via the hook. The gate IS wired; not via push-CI by design.

So these Windows fixes are what make local commits possible on Windows (the pre-commit hook runs verify), and they must also stay correct on Linux (the dispatch CI job + Linux contributors).

## Cross-platform validation (WSL Linux, 2026-08-27)

Verified the OS-specific code paths on real Linux (WSL, Python 3.13):
- `verify-links.py` → "All links verified (67 files checked)" on Linux — the `_resolve_via_assets_mount` fix is pure `pathlib`, platform-independent.
- `verify-interactive.py` Unix branch exercised directly: `platform=linux`, `os.setsid` spawn set a pgid, `os.killpg(SIGTERM)` teardown returned cleanly (`-15`); the `_terminate_server` helper imports and its Unix arm is callable; the "playwright not installed → skip" path also fires on Linux.
- The `win32` arm (`CREATE_NEW_PROCESS_GROUP`) is what runs on this Windows box — proven by the green `mise run verify`.
- Couldn't run the full Playwright/drawsvg steps in WSL (no uv/playwright/drawsvg there); those are covered by the ubuntu dispatch CI job.

## Resolution

`mise run verify` runs green end-to-end on Windows (EXIT 0). Fixed four Windows-portability issues: (1) `run` string→array + `uv run` prefix + `smoke-draw-diagram.py` (no shell-quoted JSON); (2) `verify-links.py` assets-mount fallback (218 false positives→0, real breakage still caught); (3) `verify-interactive.py` cross-platform process-group spawn/teardown + real-workspace serve + graceful skip; (4) surfaced+fixed a real quiz-path defect. Verified on Windows (green verify) and Linux (WSL: verify-links + Unix process-group branch). Enforcement confirmed via git hooks per #131.
