# Reference Code: Variables & Conditionals

Reference story for Lesson 03 of the Ink + Godot track.

## File

- `03_variables_and_conditionals.ink` — A shop-and-crossroads scene demonstrating state tracking and reactive prose

## Concepts Demonstrated

- **Read counts** — `{shop == 1:` greeting changes based on visit number
- **Conditional text** — `{condition: text | else text}` inline and multiline
- **Alternatives** — cycle `{&...|...}` for ambient description, shuffle `{~...|...}` for random travelers
- **Global variables** — `VAR gold = 15`, `VAR has_compass = false`
- **Variable modification** — `~ gold = gold - 5`, `~ has_compass = true`
- **Printing variables** — `{gold}` interpolation in prose
- **If/else blocks** — multiline `{- condition:` for branched advice and endings
- **Conditional choices** — `+ {not has_compass}` gates choices on state
- **Logical operators** — `||` (OR), `&&` (AND), `not`
- **Combined conditionals** — `{has_compass:compass|map}` inline ternary-style

## How to Run

Open in [Inky](https://github.com/inkle/inky/releases) or compile with inklecate:

```bash
inklecate 03_variables_and_conditionals.ink
```

## Architecture

```
shop (knot) — hub with conditional choices
  ├── Buy compass (gated: not owned + enough gold)
  ├── Buy map (gated: not owned + enough gold)
  ├── Ask about journey (gated: owns compass or map)
  └── Leave → crossroads
journey_advice (knot) — branched on inventory state
crossroads (knot) — route choices gated on items
ending (knot) — outcome varies by preparation level
```

## Play Paths

| Items bought | Journey outcome |
|-------------|-----------------|
| Both compass + map | Swift, confident passage |
| One item only | Uncertain but survivable |
| Neither | Two days of wandering |
