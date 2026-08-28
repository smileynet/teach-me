---
id: "249"
title: "Harden #244: prune dead import guard, verify fresh-import + reinstall, document mise.local.toml"
type: bug
status: in_progress
priority: high
blocked_by: []
tags: ["ink", "validation", "tooling"]
---

# Harden #244 mise-native validation

Self-audit of #244 (shipped) found gaps. Two are already closed by inspection/test
this session; the rest are real follow-ups.

## Already closed (evidence captured 2026-08-28)
- ✅ mise.lock cross-platform: inklecate has correct per-platform entries
  (windows/linux/mac zips + pinned sha256; mise handled the `mac` naming). Verified
  by reading mise.lock.
- ✅ mise.local.toml override works: `mise env` showed a local GODOT override winning
  over `{default}`. Tested then removed the test file.

## Remaining fixes

### 1. Prune the dead import guard in ink-gd-run.py (MUST)
Parse errors in a lesson player surface at scene-INSTANTIATION during the harness
run, NOT at `godot --import` (which returns 0 anyway). So the `imp_out` parse-error
check never fires — misleading dead code. Remove it (or reduce the import step to pure
registration) and rely on the harness-output guard that actually works. Re-verify with
a clean break-test (separate break/run/restore shell calls) → exit 2 from the harness
guard alone.

### 2. Verify import-guard does NOT false-positive on the benign inkgd warning (MUST)
inkgd's first import logs "plugin could not be initialized" (SVG icon; documented
harmless in AGENTS.md). The guard matches SCRIPT ERROR / Parse Error / Failed to load
script — different words, so it SHOULD be fine, but untested. Force a fresh import
(delete ink-test-project/.godot/) and run the pipeline; confirm no false exit 2. This
also exercises the fresh-import path.

### 3. Verify reinstall from the lockfile (SHOULD)
Everything ran where tools already existed. Prove the lockfile drives a real install:
`mise uninstall github:inkle/ink && mise install` in place; confirm inklecate resolves
+ `ink:validate` passes without the manual `mise install github:inkle/ink@1.2.1`.

### 4. Document the mechanism (SHOULD)
Not written anywhere a contributor would find: (a) `mise.local.toml` to point GODOT at
a local install, (b) `ink:validate-gd` needs Godot while `ink:validate` doesn't,
(c) inklecate now comes from mise [tools]. Add a short note to AGENTS.md or
code-validation-teaching.md steering.

## Acceptance criteria
- [ ] ink-gd-run.py import-guard pruned to only what fires; break-test still → exit 2 (harness guard)
- [ ] Fresh import (deleted .godot/) → no false exit 2 from the benign inkgd warning
- [ ] `mise uninstall && mise install` reinstalls inklecate from lockfile; ink:validate passes
- [ ] mise.local.toml + ink:validate-gd Godot requirement documented (AGENTS.md or steering)
- [ ] `mise run ink:validate-gd` still: L06 green / L05 red (until #236)


## Findings-adjusted plan (2026-08-28, 4 subagents: 2 research + 2 review)

Raw: `.scratch/research/{godot-parse-error-ci,inkgd-plugin-warning}.md`,
`.scratch/review/{ink-gd-run-guard,test-scene-godot-ci}.md`.

### Confirmed: import guard is dead code (AC1)
Lesson players are `load()`ed at scene-INSTANTIATION (validate_runtime.gd:47), not at
`--import` — which only eagerly parses autoloads/class_name/@tool scripts. So imp_out
never contains a lesson player's parse error. Keep the import RUN (primes .godot/ cache
on cold checkout, keeps output clean); delete the GUARD on its output.

### NEW BUG A — harness guard false-positives on interpolated story text
ink-gd-run.py greps harness output for "Parse Error" as a free substring, BUT the
harness interpolates arbitrary story text into its `[Lxx] ERROR:` messages
(validate_runtime.gd:96,109,128,138 — e.g. "got: <story text>"). A future story
containing "Parse Error" would misclassify a check-failure (exit 1) as setup-error
(exit 2). FIX: anchor on Godot's line-leading prefix:
```python
if any(line.startswith(("SCRIPT ERROR", "ERROR: Failed to load script"))
       for line in out.splitlines()):
    return 2
```

### NEW BUG B — benign inkgd warning DOES contain matchable error strings (AC2 is a real bug)
On a COLD .godot/ cache (fresh checkout), first import emits
`SCRIPT ERROR: Parse Error: Could not preload resource file "res://icon.svg"` and
`ERROR: Failed loading resource...` (Godot #68615/#89879 — generic plugin+icon load-order,
harmless, clears on 2nd import). An anchored startswith("SCRIPT ERROR") guard would STILL
match the icon-preload line. FIX: DOUBLE-IMPORT before the harness run (warm cache → 2nd
pass + harness run are clean), then the anchored guard is safe. Double-import is the
research-recommended mitigation.

### Confirmed: stay with runtime-grep; no --check-only / gdtoolkit
`--check-only` is single-file + unreliable whole-project (autoloads/class_name false
errors, #78587). Runtime exit codes unreliable both directions (#94957 exit 0 on error;
#83449 exit 1 on clean first import). Project convention = run in real runtime + grep
stderr (shader visual-gate philosophy). The ink harness is already the reference impl;
test-scene lags it (exit-code-only, no parse detection). Keep the 0/1/2 contract.

### Revised fix set
1. Delete dead import guard (imp_out/parse_errors); keep import run.
2. Double-import before harness run (cold-cache benign icon errors don't reach the guard).
3. Anchor harness guard on line.startswith(("SCRIPT ERROR","ERROR: Failed to load script")).
4. Validate: clean break-test (SEPARATE calls) → exit 2; fresh import (rm .godot/) → no
   false exit 2; `mise uninstall && mise install` → ink:validate passes; document
   mise.local.toml + Godot requirement in AGENTS.md.

### Already closed (evidence this session)
- mise.lock cross-platform inklecate entries verified (win/linux/mac + sha256).
- mise.local.toml GODOT override tested working via `mise env`.
