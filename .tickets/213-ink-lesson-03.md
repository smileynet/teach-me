---
id: "213"
title: "Ink Lesson 07: State Bridge"
status: in_progress
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

## Findings (2026-08-28 — research + review subagents; see .scratch/subagent-raw/213-findings.md)

- **Identifiers locked:** L06 forward-links `0007-state-bridge.html` (title "State Bridge"). Reference dir
  `reference/code/state-bridge/`; files `story_player.gd` + `07_state_bridge.ink`. MAP node `state-bridge`
  + `prereqs: [tags-as-commands]` ALREADY EXIST (status not-started) — only flip status.
- **inkgd API (VERIFIED, ticket paraphrase was wrong):** `bind_external_function(name, object, method_name,
  lookahead_safe=false)` — (object, method_name), NOT a Callable; bind AFTER create_story, BEFORE first
  continue. `observe_variable(name, object, method_name)` — push-on-change. `get_variable`/`set_variable`.
  `get_state()->String` / `set_state(String)` = WHOLE-state JSON (vars+visit counts+callstack+seed).
- **lookahead_safe is the deep concept:** externals fire during CHOICE LOOKAHEAD; a side-effecting external
  must be `lookahead_safe=false` or it double-fires. Gotcha callout material.
- **Pedagogy arc:** external functions → observers → save/load (pain→fix→pain→better-fix→persist).
  EXERCISE (decision-boundary near-transfer): colleague binds a `giveGold` external but the HUD never
  updates and keeps adding EXTERNAL calls — why won't that fix it, what should they use? (An OBSERVER on the
  var, not another external.)
- **Convention corrections:** lesson-meta uses middle-dot `·` not `/`; top key-concept opens
  `<strong>After this lesson:</strong>`; complete-block uses TAB indent + escapes `->` as `-&gt;`.
- **Harness (deterministic):** assert via `get_state`/`set_state` STRING round-trip (no user:// I/O). Template =
  `_validate_lesson06` (validate_runtime.gd:87-135). Add `await _validate_lesson07()` after line 19. Scene
  `lesson07_player.tscn` mirrors L06 + a HUD Label matching the observer target. Sync-map: 2 entries.
- **MAP/index regen (Windows):** bash for-loop task fails — use manual `.venv\Scripts\python.exe
  tools/generate_map_page.py ... --output .../ink-godot-map.html` + `generate_index_page.py --output .../index.html`.

## Acceptance criteria

- [x] Lesson `examples/ink-godot/lessons/0007-state-bridge.html` (Win + key-concept + SVG + glossary + exercise)
- [x] Reference `.ink` story: deterministic, compiles 0/0 via inklecate, top-level `-> start` divert
- [x] Golden transcript — N/A: story declares unbound `EXTERNAL discount_for` (no ink fallback), so bink can't run it. Handled like shuffle/RANDOM: `detect_unbound_externals()` + capture-refusal/replay-skip in play-ink.py. Output correctness covered by `ink:validate-gd`. `ink:transcripts` still passes (4/4, L07 correctly absent).
- [x] `story_player.gd` (downloadable, `data-file`) uses the single-step loop; binds an external function + a variable observer; demonstrates save/load
- [x] README.md in `reference/code/state-bridge/`
- [x] `mise run ink:validate` passes (compile)
- [x] `mise run ink:validate-gd` passes — harness check added for lesson 07 (asserts observable state: external fn called, observer fired, save/load round-trips)
- [x] `mise run verify` passes incl. `check-lesson-code.py` (compiles the .ink + validates story_player.gd extraction) — the #231 gate
- [x] Glossary terms annotated (Q15) + `check-lesson.py` passes (target 12+/0)
- [x] 5 criteria-based SR questions appended to `ink-godot.jsonl` (ig-07-*)
- [x] Map + index regenerated (`generate_index_page.py` needs explicit `--output examples/ink-godot/lessons/index.html`)

## Out of scope
Multi-story architecture / SVs-as-bus / combat-in-ink → lesson 08 (#214).

## Resolution (2026-08-28)

Lesson 07 "State Bridge" authored — 3rd Phase-B lesson, teaching the two-way ink<->Godot channel via
three bridges (pain-first arc): external functions (ink calls out, `bind_external_function`,
`lookahead_safe` gotcha), variable observers (game reacts, push-not-poll, seed-on-register gotcha),
save/load (`get_state`/`set_state` whole-state blob). Exercise = external-vs-observer decision boundary.

Deliverables: `0007-state-bridge.html`; reference `07_state_bridge.ink` (deterministic, `-> start`,
EXTERNAL + observed VAR gold, compiles 0/0) + `story_player.gd` (single-step `+= text` loop, all 3
bridges) + README; `lesson07_player.tscn` + sync-map entries; `_validate_lesson07()` harness check;
5 ig-07 SR cards; MAP status → complete; map + index regenerated.

Runtime-validated in real Godot (`ink:validate-gd` PASS): observer syncs HUD on load (seeded) + on
mutation (gold 10→1), external discount applies (price 9 from reputation 2), save/load round-trips
(set_state restores gold to 10). Bug caught + fixed: observer does NOT fire on registration — player
seeds the HUD explicitly (now taught as a gotcha).

Golden transcript N/A (documented): unbound EXTERNAL means bink can't run it. Added
`detect_unbound_externals()` + refusal/skip in play-ink.py (mirrors shuffle/RANDOM exclusion); output
correctness covered by ink:validate-gd.

Evidence: `mise run verify` EXIT 0 (check-lesson-code 5 compiled/0 failed, transcripts 4/4, verify-links);
`ink:validate-gd` PASS; `check-lesson.py --workspace examples/ink-godot` 0007 = 12 pass / 0 fail.
Unblocks #214.
