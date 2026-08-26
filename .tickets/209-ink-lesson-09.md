---
id: "209"
title: "Ink Lesson 03: Variables and Conditionals"
status: open
blocked_by: ["208"]
priority: high
tags: [ink]
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

## Teaching Arc (8 sections) — REVISED 2026-08-26

Reordered: alternatives before VAR (text decoration before programming).
Temp variables/parameters moved to lesson 04 (function concept, not state concept).
Opens with retroactive bridge from L02's unexplained `{weapons || potions || maps}`.

1. **"The Story Reacts"** — read counts as implicit state; `{knot_name}` truthy if visited; `||` for OR
2. **"Conditional Content"** — `{condition: text}` and `{condition: text | else text}` inline
3. **"Text That Varies"** — sequences `{a|b|c}`, cycles `{&a|b}`, shuffles `{~a|b}`
4. **"Variables: Custom State"** — `VAR gold = 10`, 4 types, `~ gold = gold - 5`
5. **"Printing and Math"** — `{gold}` interpolation, arithmetic, RANDOM
6. **"If/Else Blocks"** — multiline `{- condition:` syntax, else, switch
7. **"Conditional Choices"** — `* {condition} [text]` guards on choices
8. **"The Complete Reference Story"** — reactive shopkeeper (read counts + VAR + alternatives + conditional choices)

## Deferred
- Temp variables and knot parameters → lesson 04 (Functions & Tunnels)
- Constants (CONST) — one-line mention
- INT/FLOOR/FLOAT — note callout only
- Game-side logic / EXTERNAL → lesson 07
- String queries (? operator) — note callout only
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
