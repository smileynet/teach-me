---
id: "244"
title: "Slim validate-ink-gd.py via declarative mise env/tasks (native execution)"
type: chore
status: done
priority: high
blocked_by: []
tags: ["ink", "validation", "tooling"]
---

# Slim validate-ink-gd.py via declarative mise env/tasks

The #235 harness wrapper (`tools/validate-ink-gd.py`, ~130 lines) hand-rolls what
mise does natively: finding Godot, hardcoding the inklecate path, sequencing
compile→import→harness, and exit handling. Move the declarative parts into
`mise.toml` so tools/env are native and the surviving script is only the
irreducible logic (file-copy + output-filter + exit-map). Do this BEFORE #238's
remaining work — it rewrites the same wrapper and removes a class of the shell
blocking we keep hitting.

Research: `.scratch/research/{mise-env,mise-task-composition}.md`,
`.scratch/review/mise-helper-review.md`.

## Dividing line (from review)
- mise owns: WHERE tools live (find godot/inklecate) + WHAT ORDER commands run.
- Script owns: TRANSFORMING BYTES (copy shipped files, filter Godot's noisy stdout,
  map exit codes to skip=0 / setup-error=2 / harness-passthrough). No mise primitive.

## Step 0 — PREREQUISITE (verified gap)
`mise.local.toml` is NOT gitignored and `.gitignore` has no mise entry. Add
`mise.local.toml` to `.gitignore` FIRST, or machine paths (D:/tools/...) risk being
committed.

## What moves to mise
1. `find_godot()` → `[env] GODOT = { default = "godot" }`; real path in mise.local.toml.
   (mise `{default=}` = the "use $GODOT else fall back" pattern the script hand-codes.)
2. Hardcoded `INKLECATE = "D:/tools/..."` → `[env] INKLECATE = { default = "inklecate" }`;
   real path in mise.local.toml. Removes the committed absolute Windows path.
3. `main()` sequencing + early returns → `run = [...]` array (mise aborts on first
   non-zero exit, replacing `if not compile(): return 2`).
4. `compile_stories()` → reuse existing `validate-ink.py` as a run-array step.

## What stays (split into two tiny scripts)
- `tools/ink-gd-sync.py` (~10 lines) — the A4 copy mapping (shipped reference → harness).
- `tools/ink-gd-run.py` (~25 lines) — skip-guard, import false-exit-1 guard
  (only fail on SCRIPT ERROR / Parse Error), harness run, output filter (drop RID
  noise, keep [L0…]/[sound]), exit-code map. Reads GODOT from env (mise populates it).

## [tools] decision (verify, don't assume)
Run `mise registry godot` / `mise registry inklecate` first.
- inklecate: clean GitHub-release zips → good `github:`/`http:` backend candidate.
- Godot: awkward (ubi deprecated; known install failure needs binary + export-template
  folders — mise discussion #4440). DEFAULT: `[env]`-only for Godot on Windows; optional
  `[tools]` github backend for inklecate only.

## Acceptance criteria
- [x] `mise.local.toml` added to `.gitignore` (step 0)
- [x] `[env] GODOT` + `INKLECATE` declared with `{default=}`; machine paths in mise.local.toml (not committed)
- [x] `ink:validate-gd` task uses a `run=[...]` array (sync → compile → run)
- [x] `validate-ink-gd.py` replaced by `ink-gd-sync.py` (~10 lines) + `ink-gd-run.py` (~25 lines); no committed absolute paths
- [x] `mise run ink:validate-gd` reproduces #235 behavior: L06 green, L05 red (until #236), skip-if-Godot-absent exit 0, import-failure exit 2
- [x] `mise registry` checked before any `[tools]` entry (documented decision either way)

## Note
This is a refactor of WORKING infra (the wrapper caught the L05 bug), not new
capability. Payoff: no committed machine paths, declarative/portable tool discovery,
smaller imperative surface, less shell-blocking during harness runs.


## Findings-adjusted plan (2026-08-28, 4 subagents: 2 research + 2 review)

Raw: `.scratch/research/{mise-backends-godot-inklecate,mise-crossplatform-skip}.md`,
`.scratch/review/{current-mise-wiring,gitignore-local-mechanics}.md`.

### Correction 1 — [tools] is VIABLE for both (flip from env-only default)
The Godot ubi failure (discussion #4440 extract_all directory-hash crash) was a MISE
bug FIXED in PR #5394; ubi is now deprecated → use `github:`. So:
- inklecate: `github:inkle/ink` or pinned `http:`. Windows build is SELF-CONTAINED
  (~26 MB, bundles .NET — no separate runtime). Verified live v1.2.1 + sha256.
- Godot: `github:godotengine/godot` (needs asset filter + bin/alias for versioned exe).
UNVERIFIED on this machine (4 open Qs): asset-filter option name, bin/rename for the
versioned Godot exe, inklecate zip layout, NO live mise install run yet.
→ VERIFY with `mise install --verbose` + `mise lock` BEFORE committing any [tools].
Fallback: [tools] inklecate (clean) + [env]-only Godot if its install is fiddly.

### Correction 2 — skip logic stays in Python; run-array is a Windows trap
mise runs `run` array steps via `cmd /c` on Windows (not PowerShell; no `command -v`;
errexit unix-only). A cross-platform skip-if-absent CANNOT live in an inline run step
→ keep it in Python (`shutil.which` + `sys.exit(0)`). Keep orchestration in the script,
not a fragile run array.

### Correction 3 — sweep ALL committed hardcoded paths (3 sites, not 1); [env] exists
`D:/tools/inklecate/inklecate.exe` is committed in THREE files:
- ink-test-project/mise.toml:2 ([env] INKLECATE)
- tools/lib/ink_compile.py:34 (DEFAULT_INKLECATE, shared helper)
- tools/validate-ink-gd.py:45 (duplicate)
All → `"inklecate"` PATH default; real path in gitignored mise.local.toml.
Root mise.toml ALREADY has [env] (PYTHONDONTWRITEBYTECODE, venv) — EXTEND it.
GODOT is NOT committed anywhere (test-scene uses aqua:godotengine/godot) — adding
[env] GODOT is net-new, not a sweep.

### Correction 4 — reuse validate-ink.py for compile (confirmed)
validate-ink.py compiles (writes .ink.json via shared compile_file), dir-generic →
usable as the compile step, drops validate-ink-gd.py's duplicate compile_stories().
Caveat: it sys.exit(2)s if inklecate missing (fine once inklecate is a [tools] dep).

### Revised steps
0. .gitignore += `mise.local.toml` + `**/mise.local.toml` (verified absent).
1. Sweep 3 committed inklecate paths → "inklecate".
2. [tools]: live-verify `mise install` github:inkle/ink (commit if clean); github:
   godotengine/godot (commit if exe/alias resolves, else [env]-only Godot). `mise lock`.
3. [env]: extend existing block with GODOT/INKLECATE = {default=}; machine overrides in
   mise.local.toml only if [tools] doesn't cover.
4. Scripts: ink-gd-sync.py (copy) + ink-gd-run.py (shutil.which skip + import-guard +
   harness + filter + exit-map); delete validate-ink-gd.py. Orchestration in Python.
5. Verify: `mise run ink:validate-gd` → L06 green / L05 red, skip→0, import-fail→2.

Absorbs #238 A3+A4. Also update ink-test-project/mise.toml [tasks.compile-ink] which
uses $INKLECATE.

## Resolution (2026-08-28)

inklecate via mise [tools] github:inkle/ink@1.2.1 (swept 2 committed D:/tools paths to {default=inklecate}); [env] GODOT/INKLECATE={default=}, Godot env-only (heavy/optional); split 130-line wrapper into ink-gd-sync.py + ink-gd-run.py, ink:validate-gd run=[] array; deleted validate-ink-gd.py; made inklecate_available PATH-aware. Absorbs #238 A3/A4.
