---
id: "209"
title: "Ink Lesson 03: Variables and Conditionals"
status: open
blocked_by: ["208"]
priority: high
---

# Ink Lesson 03: Variables and Conditionals

VAR/temp declarations, types, conditional content (curly braces), read counts, variable text (sequences, cycles, shuffle).

## Research Findings (2026-08-26)

### Teaching sequence (Toronto Met textbook + consensus)
- **Conditionals FIRST using read counts**, variables SECOND when learners need custom state
- Bridge concept: "Read counts are implicit variables you don't declare. VAR is the general-purpose version."
- This matches ink's own design: `{knot_name}` works without any VAR declaration
- The `{}` syntax is heavily overloaded — lesson must unify it ("curly braces = the story reacting to state")

### Common beginner mistakes to address
1. Forgetting to initialize (silent logic bugs — ink defaults to 0)
2. Accidental re-initialization on revisit
3. Naming drift/misspelling (creates silent new variable)
4. Missing fallback in conditional text (gaps in prose)
5. Boolean proliferation (20 flags when a number suffices)

### Source material (from .memory/ink-reference/)
- 3-01-global-variables.md — VAR, 4 types, printing, divert targets, sticky string gotcha
- 3-02-logic.md — `~` marker, arithmetic, RANDOM, INT/FLOOR, string queries
- 3-03-conditional-blocks-if-else.md — if/else, switch, multiline alternatives, no-gathers-inside-blocks
- 3-04-temporary-variables.md — temp, knot parameters, recursive knots, divert targets as params
- 1-08-variable-text.md — sequences, cycles, shuffles, conditional text, multiline alternatives

### Key teaching examples identified
- "accuse" parameterized knot (combines multiple concepts)
- RANDOM dice roll (intuitive game-dev hook)
- The 4-type VAR declaration example (all types in one block)
- Multiline stopping sequence for NPC greetings

## Teaching Arc (8 sections)

1. **"Stories That Remember"** — read counts: `{knot_name}` as lightweight memory (no new syntax)
2. **"Conditional Content"** — `{visited_market: "Welcome back!"}` — prose reacts to state
3. **"Variables: Custom State"** — `VAR has_map = false` + `~ has_map = true`
4. **"Printing and Math"** — `{gold}` prints, `~ gold = gold - 5`, RANDOM
5. **"If/Else Blocks"** — multi-line `{- condition:` syntax
6. **"Variable Text"** — sequences `{a|b|c}`, cycles `{&a|b}`, shuffles `{~a|b}`
7. **"Temp Variables and Parameters"** — `~ temp x = 5`, knot params
8. **"The Complete Reference Story"** — reactive NPC shopkeeper

## Deferred
- Constants (CONST) — one-line mention
- INT/FLOOR/FLOAT — note callout
- Game-side logic / EXTERNAL → lesson 07
- String queries (? operator) — note callout
- Lists → expansion track

## Acceptance criteria

- [ ] Lesson HTML at examples/ink-godot/lessons/0003-ink-variables-and-conditionals.html
- [ ] Reference .ink story compiled via inklecate (0 errors, 0 warnings)
- [ ] README.md in reference/code/ink-variables-and-conditionals/ directory
- [ ] mise run ink:validate passes
- [ ] Glossary terms annotated (jargon pass)
- [ ] check-lesson.py passes
- [ ] Exercise answer compiles clean
- [ ] Independent subagent review passes
