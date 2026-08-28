---
id: "235"
title: "Headless Godot validation harness for lesson GDScript"
type: feature
status: in_progress
priority: high
blocked_by: []
tags: ["ink", "validation"]
---

# Headless Godot validation harness for lesson GDScript

## Why

Lessons 05 (#211) and 06 (#212) ship downloadable `story_player.gd` files, but
they were validated only by API-line-number matching against the inkgd addon +
the spike — never actually run in Godot. The project's `code-validation-teaching`
steering requires validating code with the learner's real tool. For GDScript that
means Godot. No harness exists yet; this builds it so lessons 05–08 can all be
runtime-validated the same way.

## Environment (confirmed available)

- Godot `4.7.1.stable` via mise shim (`C:\Users\uosmi\AppData\Local\mise\shims\godot.exe`).
- inkgd addon present at `ink-test-project/addons/inkgd/`.
- `ink-test-project/mise.toml` already has a `godot-import` task
  (`godot --headless --editor --import --quit --path .`).
- inklecate at `D:/tools/inklecate/inklecate.exe`.

## What to build

### Layer 1 — parse/import check (the floor)
Compile the lesson's reference `.ink` to `.ink.json` in `ink-test-project/stories/`,
copy the lesson `story_player.gd` into the project under a distinct name, create a
minimal `.tscn` with the exact node tree the script expects, then run
`godot --headless --editor --import --quit --path ink-test-project`. This parses
every GDScript and fails on syntax errors, unresolved API calls, and parse-time
`@onready` path issues.

### Layer 2 — headless playthrough (the real check)
A `SceneTree` script (run via `godot --headless --script`) that instantiates the
player scene, drives it through a fixed choice sequence, and asserts observable
outcomes: story reaches END, speaker label updated (L06), `# hidden` line text
suppressed (L06), text accumulated (L05). Exits 0 on pass, non-zero on failure.

**Known risk to resolve:** headless Godot may not pump frames like the editor, so
`call_deferred("_create_story")` → `loaded` signal may need a manual frame step or
`await get_tree().process_frame` in the harness. If the async load can't be
exercised headless, document that Layer 2 covers `_process_tags` logic directly
(unit-style) and Layer 1 covers parse — and say so honestly rather than claim full
runtime coverage.

### Layer 3 — promote to a repeatable task
Add a `mise` task (e.g. `ink:validate-gd`) that runs Layers 1–2 over the lesson
players. Note the mechanism in `code-validation-teaching` steering so lessons 07/08
reuse it.

## Acceptance criteria

- [ ] Layer 1: headless import parses lesson GDScript, fails loudly on a syntax error (prove with a deliberately-broken copy, then revert)
- [ ] Layer 2: headless playthrough drives a player scene to END and asserts at least one observable side effect
- [ ] `call_deferred`/`loaded` timing under headless resolved OR documented as a coverage boundary
- [ ] `ink:validate-gd` mise task added and runs green
- [ ] Mechanism documented in `.kiro/steering/code-validation-teaching.md` (or ink-authoring.md)
- [ ] Harness scenes/scripts live in `ink-test-project` (gitignored artifacts excluded per #233 policy)

## Notes

Keep test scenes minimal and clearly named (`lesson05_player.tscn`, etc.). Do NOT
disturb `spike_story.tscn`. Confirm GDScript specifics the shipped code relies on:
`String.split(":", false, 1)` maxsplit semantics, ternary `a if cond else b`,
`current_choices[i].text` on the GDScript runtime (not just bink).


## Findings-adjusted design (2026-08-27, 4 subagents: 2 research + 2 review)

Raw: `.scratch/research/{headless-gdscript-test,gdscript-string-api}.md`,
`.scratch/review/{spike-and-config,shader-validation-pattern}.md`.

### Corrections to the original plan
1. **Scope = inkgd-runtime gate, NOT story logic.** bink already covers reaches-END +
   correct-output (`ink:play`, `ink:transcripts`). The GDScript harness validates only
   what bink can't: that the story runs inside Godot's real inkgd runtime and the lesson
   `InkPlayer` integration code works (create_story/loaded/continue/current_tags/
   choose_choice_index/get_variable). This is the GDScript analogue of the shader visual gate.
2. **`--headless --editor --import --quit` is UNRELIABLE for parse errors** (Godot bug
   #83449: false exit-1 on clean first import until 4.3; also targets import/resource
   errors, not GDScript compile). Use the `validate_claims.gd` EditorScript/scene-runner
   pattern instead — load + exercise the code with a REAL exit code (validate_claims.gd
   only prints; fix that gap: tally failures → quit(0/1)).
3. **Async load needs `await`, not frame-counting.** `loads_in_background=false` removes
   the thread but there are TWO call_deferred hops (player + inkgd ink_player.gd:343);
   `loaded` never fires synchronously. Use `await _ink_player.loaded`. Only PROCESS frames
   needed (no render) → headless works.
4. **Prefer the SCENE form over `--script`.** EditorScript._run() has no frame loop and
   `__InkRuntime` autoload may not be ready there. Use a headless scene (`extends Node`,
   `_ready()` + await, `get_tree().quit(code)`), run via `godot --headless <scene> --path`.

### Confirmed API facts (also feed #236)
- `String.split(":", false, 1)` = `(delimiter, allow_empty=true, maxsplit=0)`, left-to-right,
  ≤2 elements. My usage is correct. RESIDUAL: allow_empty=false × maxsplit=1 on adjacent
  colons is underspecified in docs — harness confirms empirically (matters if a tag value
  contains a colon).
- Ternary `a if cond else b` valid. `_mcp_game_helper` autoload inert headless
  (guarded by EngineDebugger.is_active()). `__InkRuntime` autoload IS required.

### Design
- Scene `ink-test-project/validate_runtime.tscn` + `validate_runtime.gd` (`extends Node`).
  `_ready()`: per story → create InkPlayer, `await loaded`, drive choices, assert, tally,
  `get_tree().quit(fails>0)`. Reads current_text/current_tags/has_choices/current_choices
  directly — no UI tree needed.
- Asserts: L05 reaches END + text present; L06 speaker set + `# hidden` suppressed +
  mid-story tag observed (proves single-step preserves per-line tags).
- Prove-it-fails: break a copy, confirm non-zero exit, revert.
- `mise` task `ink:validate-gd` (skip-guard like inklecate — Godot not on every machine;
  dedicated task, not a hard verify dep). Document in code-validation-teaching.md.
- Reuse validate_claims.gd tagged-stdout `[id] Confirmed/ERROR` + spike InkPlayer usage.
- Hygiene: harness source named clearly; keep .godot/.uid byproducts out of commits (#233);
  don't touch spike_story.tscn or main_scene; inkgd first-import SVG-icon error is harmless.
