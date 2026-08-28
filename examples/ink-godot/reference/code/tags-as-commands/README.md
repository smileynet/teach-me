# Reference Code: Tags as Commands

Reference files for Lesson 06 of the Ink + Godot track — driving game systems
from ink by attaching `# tags` to lines and dispatching them in GDScript.

## Files

- `06_tags_as_commands.ink` — a village-well scene where every line carries a
  command tag (`# speaker:`, `# sound:`, `# hidden`). Compile to `.ink.json`.
- `story_player.gd` — extends Lesson 05's player with a single-step continue
  loop and a `_process_tags()` dispatcher.

## The tag protocol

A tag is a **command to a game subsystem**, written as `# key: value`. The colon
is not ink syntax — it's plain text this parser splits. The story declares intent;
the engine decides how to carry it out.

| Tag | Kind | Effect |
|-----|------|--------|
| `# speaker: Alfoz` | key + value | Set the name label above the text |
| `# sound: coin_drop` | key + value | Play a sound effect |
| `# hidden` | bare | Run the line's side effects but do NOT show its text |

Add a new command by teaching the parser one new `key` in the `match` — never by
editing the story. That is the whole point: the writer and the engine share a
contract, not code.

## Why a single-step loop (not `continue_story_maximally()`)

Lesson 05 ran the story with `continue_story_maximally()`, which advances through
several lines at once. That collapses their tags: `current_tags` ends up holding
only the **last** line's tags, so the intermediate commands are lost. To dispatch
per-line tags you must step one line at a time:

```gdscript
while _ink_player.can_continue:
    var text = _ink_player.continue_story()   # one line
    var show = _process_tags(_ink_player.current_tags)
    if show and text.strip_edges() != "":
        _text_label.text += text + "\n"
```

## The suppress contract

`_process_tags()` returns a bool. Only `# hidden` flips it false. Tags always run
for their side effects (speaker, sound) — the return value decides only whether
the line's **text** is shown. This is how a production story shows one line on a
passed check and a different line on a failure while both fire their effects.

## Node setup

Attach `story_player.gd` to a `Control` with three direct children:
`SpeakerLabel` (Label), `TextLabel` (RichTextLabel, BBCode enabled),
`ChoicesContainer` (VBoxContainer).

## Production scale

Esoteric Ebb's real `TagProcessor` dispatches ~30 command families this way —
speaker voices, skill checks (`# DC14`), variable ops (`# .flag=1`), audio,
camera, items, combat. This lesson teaches the core (speaker + one command +
suppress); those all extend the same drain-and-dispatch loop.
