# Mission: Script game narrative with ink and Godot

## Why

Ink (Inkle Studios) separates story logic from game code — writers work in plain-text
`.ink` files, programmers integrate via a runtime API. It powers 80 Days, Heaven's Vault,
and Esoteric Ebb. Learning ink plus its Godot integration (the inkgd addon, pure GDScript,
no .NET) lets you build branching, stateful, reactive narrative that scales — without
hand-rolling a dialogue system or coupling story content to engine code.

## Success looks like

- Can author engine-agnostic ink: knots and diverts, once-only vs sticky choices with
  stitches/weave/gathers, variables and read-count conditionals, and functions/tunnels for reuse
- Can load an ink story in Godot via the InkPlayer node — display text line-by-line and
  route player choices back into the story
- Can drive game systems from narrative using the tags-as-commands protocol and the
  two-way state bridge (external functions + variable observers) without coupling ink to
  engine code
- Can explain the production patterns (multi-story composition, story variables as a state
  bus, hub-and-spoke structure, combat-in-ink) that scale a prototype toward a shipped game

## Constraints

- Godot 4 with the inkgd addon (pure GDScript — no .NET/C# required)
- Phase A (lessons 01–04) is engine-agnostic ink authored in Inky; Phase B (05–08) integrates Godot
- Story logic is validated by compiling `.ink` and replaying golden transcripts; the Godot
  integration is validated in real headless Godot (`mise run ink:validate-gd`)
