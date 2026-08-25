# Reference Code: Choices, Stitches & Weave

Reference story for Lesson 02 of the Ink + Godot track.

## File

- `02_choices_and_weave.ink` — A market-and-tavern exploration scene demonstrating all lesson 02 concepts

## Concepts Demonstrated

- **Once-only choices** (`*`) — conversation options that disappear after use (tavern talk)
- **Sticky choices** (`+`) — browsing options that persist (market stalls)
- **Fallback choices** (`* ->`) — auto-selected when no visible options remain (tavern exit)
- **Bracket text suppression** (`[text]`) — controlling choice display vs output text
- **Stitches** (`= name`) — sub-locations within the market_square knot
- **Local diverts** — `-> weapons` instead of `-> market_square.weapons` within the same knot
- **Gathers** (`-`) — branches reconverging after each stall visit
- **Chained weave** — multiple choice-gather pairs in sequence (tavern scene)
- **Nested choices** (`**`) and nested gathers (`--`) — sub-decisions within the map stall
- **Conditional choices** (`{weapons || potions || maps}`) — option appears after visiting stalls

## How to Run

Open in [Inky](https://github.com/inkle/inky/releases) or compile with inklecate:

```bash
inklecate 02_choices_and_weave.ink
```

## Architecture

```
market_square (knot)
  ├── = weapons (stitch) — sticky, revisitable
  ├── = potions (stitch) — sticky, revisitable
  └── = maps (stitch) — nested choices within
tavern (knot)
  ├── chained weave (seat → drink → conversation)
  └── = tavern_end (stitch) — final decision
rest (knot) — ending A
night_road (knot) — ending B
```
