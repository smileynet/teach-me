---
id: "244"
title: "Slim validate-ink-gd.py via declarative mise env/tasks (native execution)"
type: chore
status: open
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
- [ ] `mise.local.toml` added to `.gitignore` (step 0)
- [ ] `[env] GODOT` + `INKLECATE` declared with `{default=}`; machine paths in mise.local.toml (not committed)
- [ ] `ink:validate-gd` task uses a `run=[...]` array (sync → compile → run)
- [ ] `validate-ink-gd.py` replaced by `ink-gd-sync.py` (~10 lines) + `ink-gd-run.py` (~25 lines); no committed absolute paths
- [ ] `mise run ink:validate-gd` reproduces #235 behavior: L06 green, L05 red (until #236), skip-if-Godot-absent exit 0, import-failure exit 2
- [ ] `mise registry` checked before any `[tools]` entry (documented decision either way)

## Note
This is a refactor of WORKING infra (the wrapper caught the L05 bug), not new
capability. Payoff: no committed machine paths, declarative/portable tool discovery,
smaller imperative surface, less shell-blocking during harness runs.
