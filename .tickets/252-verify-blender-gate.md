---
id: "252"
title: "Opt-in verify:blender gate — run bpy --check artifacts (skip if Blender absent)"
status: done
blocked_by: []
priority: high
tags: ["mktoon", "blender"]
---

# Opt-in verify:blender gate — run bpy --check artifacts (skip if Blender absent)

## Why

The Blender lesson track (#218 posterize, #219 palette-snap, #220 control-maps) ships
diffable bpy artifacts that each have a `--check` Tier-2 validator (assert the node group
builds with correct sockets/wiring). Today those `--check`s are run ONCE by hand during
authoring — nothing re-runs them. A future edit to a bpy artifact (or a Blender version
bump) could silently break the node wiring and no gate would catch it. The Tier-1 math
oracles ARE in `mise run verify`, but they validate the math, not the Blender node graph.

Mirror the `ink:validate-gd` pattern: an opt-in task that runs the real-runtime checks and
**skips gracefully when the runtime is absent**, so core `verify` stays fast and Blender-free.

## What to build

A `mise run verify:blender` task that:
1. Detects Blender (full path per AGENTS.md — the mise `blender` shim is broken; resolve
   via an env var like `BLENDER` with a sensible default, overridable in mise.local.toml).
2. If Blender is absent → print a skip message, exit 0 (like ink:validate-gd skips without Godot).
3. If present → run each bpy artifact's `--check`:
   - `reference/code/albedo-posterize/posterize_rgb.py --check`
   - `reference/code/palette-snap/palette_snap.py --check`
   - `reference/code/toon-control-maps/control_maps.py --check`
   Aggregate exit codes; any non-zero → fail.
4. Do NOT add it to the core `verify` run list (keep verify Blender-free + fast). It's a
   separate opt-in gate, run before closing Blender-track tickets and in the pre-commit
   hook only if Blender is present.

Document the Godot A/B visual capture as explicitly manual (not CI-able — needs GPU/window),
with the re-capture recipe in the reference README, so the visual tier isn't mistaken for gated.

## Implementation plan (corrected by research + code audit, 2026-08-28)

CRITICAL findings that change the naive plan:
- **`blender -b --python X.py` swallows Python exceptions and exits 0 by default**
  (Blender tracker T82494). A `--check` that raises — or even one whose `sys.exit(1)`
  is dropped — would silently PASS. Fix: run `blender -b --python-exit-code 1 --python X.py
  -- --check` (flag BEFORE `--`) AND dual-gate on exit==0 AND the artifact's success
  sentinel line present in stdout. Never trust the exit code alone.
- **`control_maps.py --check` needs cwd=examples/godot-gamedev** (it opens the ARM texture
  by a relative path) or it FAILs spuriously.
- **Artifact paths:** examples/godot-gamedev/reference/code/{albedo-posterize/posterize_rgb.py,
  palette-snap/palette_snap.py, toon-control-maps/control_maps.py}. All use `blender -b
  --python X -- --check`; `-- --check` required (args parsed after `--`). Success = one-line
  "OK" to stdout + exit 0; FAIL = "FAIL:" stderr + exit 1; not-in-Blender = exit 2.
- **Skip pattern to mirror (tools/ink-gd-run.py):** resolve via env var
  `os.environ.get("BLENDER","blender")`, accept absolute path (Path.exists()) or
  shutil.which(); None → `print("SKIP: ...")` stdout + exit 0. Convention 0=pass/skip,
  1=check failed, 2=setup error. verify-blender AGGREGATES 3 subprocesses (any non-zero → 1).
- **AGENTS.md does NOT document the Blender path / broken shim** (it's only in #218 ticket)
  — this ticket must ADD that note, not just reference it.

Build:
1. `tools/verify-blender.py` — resolve_blender() skip-if-absent; run the 3 `--check`s with
   `--python-exit-code 1`, cwd=examples/godot-gamedev, dual gate (exit 0 + sentinel);
   aggregate; exit 0/1/2. Mirror ink-gd-run.py.
2. mise.toml: `[env] BLENDER = { default = "blender" }`; `[tasks."verify:blender"]` →
   `run=["python tools/verify-blender.py"]`, depends=["setup"]. NOT in [tasks.verify], NOT
   in pre-commit hook (hook runs only `mise run verify`; keep core Blender-free + fast).
3. AGENTS.md: Commands-table row for verify:blender + Constraints note (broken blender shim →
   set BLENDER to full path in mise.local.toml; Godot A/B capture is manual/not-CI-able).

Validation (prove teeth): (a) present → 3 pass exit 0; (b) tamper logical FAIL → exit 1
naming artifact; (c) tamper Python EXCEPTION into a --check → still caught via
--python-exit-code + missing sentinel (validates the exit-0 trap fix); (d) BLENDER=bogus
path → SKIP + exit 0; (e) core verify byte-unchanged. Mutate-then-restore in SEPARATE shell
calls (back-up → break → run → restore) so a cancelled run doesn't strand a broken artifact.

## Acceptance criteria

- [x] `mise run verify:blender` runs all three bpy `--check`s when Blender is present, fails on any broken node group
- [x] Skips cleanly (exit 0 + message) when Blender is absent — does not block a Blender-less machine
- [x] Blender path resolves via env var with mise.local.toml override (not hardcoded)
- [x] Core `mise run verify` is unchanged (still Blender-free, still fast)
- [x] AGENTS.md Commands table documents `verify:blender` + notes Godot A/B is manual
- [x] Verified: break a node group on purpose → verify:blender fails; restore → passes

## Resolution (2026-08-28)

tools/verify-blender.py: resolves BLENDER env var (skip if absent), runs 3 bpy --check artifacts with --python-exit-code 1 + success-sentinel dual gate (never trusts exit code alone — Blender T82494 swallows exceptions). [env] BLENDER added, [tasks.verify:blender] wired, NOT in core verify. AGENTS.md Commands + Constraints updated.
