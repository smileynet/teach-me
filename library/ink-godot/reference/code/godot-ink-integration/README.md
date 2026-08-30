# Reference Code: First Godot Integration

Reference files for Lesson 05 of the Ink + Godot track — loading and running a
compiled ink story in Godot 4 with the [inkgd](https://github.com/ephread/inkgd)
GDScript runtime.

## Files

- `05_first_godot_integration.ink` — a small, deterministic cave-entrance story
  (one variable that changes, one branching choice, a clean END). Compile to
  `.ink.json` before loading it in Godot.
- `story_player.gd` — the full integration script: creates an `InkPlayer`, loads
  the compiled story, displays text, renders choices as buttons, and reads a
  story variable at the end. This is the validated reference implementation.

## The runtime loop (what the script does)

```
InkPlayerFactory.create()      → make the player
add_child(player)              → put it in the scene tree (InkPlayer is a Node)
player.ink_file = <.ink.json>  → assign the COMPILED story
connect("loaded", ...)         → wait for the story to build
call_deferred(create_story)    → build it (deferred so the runtime autoload is ready)

on loaded(true):
  continue_story_maximally()   → run to the next choice or the end
  read current_text            → the text produced
  if has_choices:              → render current_choices[i].text as buttons
      choose_choice_index(i)   → on button press, then continue again
  elif not can_continue:       → story ended
  get_variable("torch_lit")    → read ink state from GDScript
```

## The one rule that trips everyone up

**Never touch the story before `loaded(true)` fires.** `create_story()` reports
its result asynchronously through the `loaded` signal. Reading `current_text` or
calling `continue_story_maximally()` before then returns empty values (and pushes
an error) — it looks like "nothing happened" rather than a crash. Connect
`loaded` first, act inside the handler.

## Setup

1. Install the inkgd addon (`godot4` branch) into `addons/inkgd/` and enable the
   plugin (adds the `__InkRuntime` autoload).
2. Compile the story: `inklecate -o 05_first_godot_integration.ink.json 05_first_godot_integration.ink`
3. Attach `story_player.gd` to a `Control` node with `TextLabel` (RichTextLabel)
   and `ChoicesContainer` (VBoxContainer) children.

## How to run the story standalone

```bash
inklecate -p 05_first_godot_integration.ink   # play in the terminal
```
