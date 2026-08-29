# State Bridge — Lesson 07 code files

Reference code for [Lesson 07: State Bridge](../../../lessons/0007-state-bridge.html). The two-way
channel between an ink story and the Godot game: ink calls out, the game reacts, and the whole story
persists.

| File | Purpose |
|------|---------|
| `07_state_bridge.ink` | The market story. Declares `EXTERNAL discount_for(rep)`, exposes an observed `VAR gold`, and reaches a clean END. Deterministic (no shuffle/RANDOM). Compile to `.ink.json` with inklecate. |
| `story_player.gd` | The player wiring all three bridges: `bind_external_function` (external), `observe_variable` + a seed call (observer), and `get_state`/`set_state` (save/load). Single-step accumulate loop from lessons 05/06. |

## The three bridges

1. **External function** — `EXTERNAL discount_for(rep)` in ink, bound to `_discount_for` in GDScript.
   Bound *after* `create_story()`, *before* the first continue. Pure, so `lookahead_safe = true`
   (a side-effecting external would need `false`).
2. **Variable observer** — `observe_variable("gold", self, "_on_gold_changed")` pushes each change of
   `gold` to the HUD. Fires on *change*, not on registration — so the player seeds the HUD once from
   `get_variable("gold")` right after registering.
3. **Save / load** — `get_state()` serializes the whole story (variables, visit counts, callstack, seed)
   to one JSON string; `set_state()` restores it. Never hand-save individual variables.

## Running it

Attach `story_player.gd` to a `Control` with children `SpeakerLabel` (Label), `TextLabel`
(RichTextLabel, BBCode on), `GoldLabel` (Label), and `ChoicesContainer` (VBoxContainer). Place the
compiled `07_state_bridge.ink.json` at `res://stories/`.

## Validation

- `mise run ink:validate` — compiles the story (0 errors, 0 warnings).
- `mise run ink:validate-gd` — runs this player in real Godot 4 and asserts all three bridges: the
  observer syncs the HUD, the external discount applies (price 9 from reputation 2), and a save/load
  round-trip restores `gold`.

## No golden transcript (by design)

`07_state_bridge.ink` declares an unbound `EXTERNAL` with no ink `function` fallback, so bink (the
golden-transcript runtime) cannot run it — it has no external-binding API. Output correctness is
covered instead by `mise run ink:validate-gd`, where real Godot binds `discount_for`. This is the
same exclusion the transcript tooling applies to shuffle/RANDOM stories.
