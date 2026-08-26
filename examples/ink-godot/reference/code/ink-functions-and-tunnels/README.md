# Reference Code: Functions & Tunnels

Reference story for Lesson 04 of the Ink + Godot track.

## File

- `04_functions_and_tunnels.ink` — A forest-and-cave adventure demonstrating reusable logic and portable scenes

## Concepts Demonstrated

- **Temp variables** — `~ temp result = base - armor` for scratch calculations within a knot
- **Knot parameters** — `=== battle(enemy, enemy_attack, enemy_armor) ===` passing data at divert-time
- **Functions with return** — `roll_dice(sides)`, `calculate_damage(base, armor)`, `describe_condition(hp)`
- **Functions without return** — `gold_text()` prints conditional prose inline
- **Inline function calling** — `{describe_condition(player_health)}` embedded in text
- **Tunnels** — `-> battle("wolf", 2, 1) ->` runs sub-scene and returns to caller
- **Tunnel return** — `->->` at end of camp and battle knots
- **Tunnel + parameters** — combining reusable scenes with caller-specific data
- **Nested function calls** — functions calling other functions (`battle` calls `roll_dice` and `calculate_damage`)

## How to Run

Open in [Inky](https://github.com/inkle/inky/releases) or compile with inklecate:

```bash
inklecate 04_functions_and_tunnels.ink
```

## Architecture

```
Functions (pure computation):
  roll_dice(sides)         → random integer
  calculate_damage(b, a)   → max(b-a, 0)
  describe_condition(hp)   → "strong"/"battered"/"barely standing"/"near death"
  gold_text()              → prints conditional prose (no return)

Tunnels (reusable scenes):
  camp                     → rest scene, heals HP, choices, returns via ->->
  battle(enemy, atk, arm)  → combat loop, uses functions, returns via ->->

Main story:
  forest_path → cave_entrance → victory/defeat
  (both locations call camp and battle as tunnels)
```

## Play Paths

| Strategy | Likely outcome |
|----------|---------------|
| Fight everything, no rest | Risk defeat from accumulated damage |
| Rest between fights | Survive but take longer |
| Avoid fights, pay troll | Need 15 gold (start with 20, may need to fight once) |
