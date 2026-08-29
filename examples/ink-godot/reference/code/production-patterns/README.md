# Production Patterns — Lesson 08 code files (capstone)

Reference code for [Lesson 08: Production Patterns](../../../lessons/0008-production-patterns.html), the
finale of the ink + Godot track. How a shipped multi-story game (Esoteric Ebb, 286 files, ~500K words)
composes the primitives from lessons 01–07 into an architecture.

| File | Purpose |
|------|---------|
| `08_production_patterns.ink` | A tavern hub in pure ink. `VAR asked_name`/`helped_cook` are a **state bus**; spokes write them, gated choices read them; the hub is re-enterable (**hub-and-spoke**). Deterministic — earns a golden transcript. |
| `story_player.gd` | The **unchanged** lesson 06 single-step drain loop. The capstone adds no engine API — the architecture lives in the story. Includes a `read_flag()` helper showing how a game harvests bus variables with `get_variable`. |

## The three patterns

1. **State-bus variables** — a flat namespace of `VAR` flags as shared cross-story state. One file writes
   a flag, any file reads it. Replaces bespoke quest/faction/inventory systems.
2. **Stateless-per-dialog** — no ink file owns the save. The engine keeps the flags; each conversation is
   a fresh `InkPlayer` seeded via `set_variable` and harvested via `get_variable`. Any-order entry, flat
   patch-safe saves. Trade-off: no mid-conversation save (use lesson 07's `get_state` if you need that).
3. **Hub-and-spoke** — a re-enterable hub knot lists topics; each spoke diverts *back* to the hub (never a
   self-loop — read counts advance on fresh entry and gated choices re-evaluate); one choice exits.

**Payoff — combat as dialog:** with these three, combat needs no separate system — a turn is a hub,
actions are choices, resolution is a tag the engine acts on. The reference story stays deterministic; a
shipped game rolls dice in the engine behind the tag and reads the result off the bus.

## Running it

Attach `story_player.gd` to a `Control` with children `SpeakerLabel` (Label), `TextLabel` (RichTextLabel,
BBCode on), and `ChoicesContainer` (VBoxContainer). Place the compiled `08_production_patterns.ink.json`
at `res://stories/`.

## Validation

- `mise run ink:validate` — compiles 0 errors, 0 warnings.
- `mise run ink:transcripts` — replays the committed golden transcript (the state bus gating content).
- `mise run ink:validate-gd` — runs this player in real Godot 4 and asserts the state bus works: gated
  content hidden initially (3 hub choices), then `asked_name = true` unlocks a gated choice (4 choices).

Unlike lesson 07, this story is **pure ink** (no unbound EXTERNAL, no RNG), so it has a real golden
transcript — the strongest output-correctness gate in the track.
