---
id: "213"
title: "Ink Lesson 07: State Bridge"
status: open
blocked_by: ["212"]
priority: high
tags: [ink]
---

# Ink Lesson 07: State Bridge

External functions (binding game logic), variable observers (reactive state sync), save/load state serialization.

## Context (established by lessons 05–06 this session — inherit, don't rediscover)

This is the 3rd Phase-B (Godot integration) lesson. Lessons 05 (`0005-godot-ink-integration.html`)
and 06 (`0006-tags-as-commands.html`) established the pattern; follow it:

- **File:** `examples/ink-godot/lessons/0007-state-bridge.html`; reference code at
  `examples/ink-godot/reference/code/state-bridge/` (slug = filename without number — confirm
  against lesson 06's "What's Next" link, which points here).
- **story_player.gd extends the L05/L06 loop.** The runtime loop is a single-step
  `while _ink_player.can_continue: continue_story()` accumulate loop. DO NOT use
  `continue_story_maximally()` — through inkgd's InkPlayer it returns only the LAST line
  (the #236 bug). External-function binding + variable observers hook into this same loop.
- **inkgd API:** `bind_external_function(name, callable)`, `observe_variable(name, callable)`,
  `get_variable`/`set_variable`, `save_state`/`load_state` (verify exact signatures against
  `ink-test-project/addons/inkgd/ink_player.gd` as prior lessons did — it's inkgd 0.6.0 godot4 branch).
- **Reference story must be DETERMINISTIC** (no `{~shuffle}`/`RANDOM`) so it earns a golden
  transcript; needs an explicit top-level `-> start` divert (else it compiles to `done` with no output).
- **Runtime validation:** the shipped `story_player.gd` MUST run in the real inkgd runtime via
  `mise run ink:validate-gd` — add a per-lesson check to `ink-test-project/scenes/validate_runtime.gd`
  and its sync map in `tools/ink-gd-sync.py`. Compile+transcript (bink) does NOT cover the Godot
  integration code; the harness is the runtime gate.
- Follows visual-teaching + ink-authoring steering (SVG accessibility, glossary annotation,
  narrative code framing, exercise = Win misconception-probe).

## Acceptance criteria

- [ ] Lesson `examples/ink-godot/lessons/0007-state-bridge.html` (Win + key-concept + SVG + glossary + exercise)
- [ ] Reference `.ink` story: deterministic, compiles 0/0 via inklecate, top-level `-> start` divert
- [ ] Golden transcript captured + committed; `mise run ink:transcripts` passes
- [ ] `story_player.gd` (downloadable, `data-file`) uses the single-step loop; binds an external function + a variable observer; demonstrates save/load
- [ ] README.md in `reference/code/state-bridge/`
- [ ] `mise run ink:validate` passes (compile)
- [ ] `mise run ink:validate-gd` passes — harness check added for lesson 07 (asserts observable state: external fn called, observer fired, save/load round-trips)
- [ ] Glossary terms annotated (Q15) + `check-lesson.py` passes (target 12+/0)
- [ ] 5 criteria-based SR questions appended to `ink-godot.jsonl` (ig-07-*)
- [ ] Map + index regenerated (`generate_index_page.py` needs explicit `--output examples/ink-godot/lessons/index.html`)

## Out of scope
Multi-story architecture / SVs-as-bus / combat-in-ink → lesson 08 (#214).
