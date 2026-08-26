---
id: "210"
title: "Ink Lesson 04: Functions and Tunnels"
status: open
blocked_by: ["209"]
priority: high
---

# Ink Lesson 04: Functions and Tunnels

Temp variables, knot parameters, pure functions (inline computation), tunnels (sub-scenes that return), INCLUDE for multi-file projects.

## Research Findings (2026-08-26)

### Bridge from lesson 03
- Learner saw `~ temp roll = RANDOM(1,6)` in a note that said "covered in lesson 04"
- Comfortable with VAR, logic lines (~), conditional choices, if/else blocks
- Functions and tunnels are cold introductions — need full motivation

### Key distinctions (from source material)
- **temp vs VAR**: temp dies at knot end, VAR persists. Temp is scratch paper.
- **function vs knot**: functions CANNOT contain diverts/choices but CAN be called inline in text
- **tunnel vs divert**: divert is one-way (->), tunnel goes and returns (-> knot ->)
- **parameters**: data passed at divert-time, typed as temp inside the target knot

### Common tunnel mistakes (6 documented)
1. Forgetting ->-> (no compile-time check — story silently stops)
2. Confusing tunnels with threads (different mechanism)
3. Stale call-stack from misplaced ->->
4. Nested tunnel complexity (valid but hard to follow)

### Production patterns (shipped games)
- Heaven's Vault: hundreds of conversation topics as independent tunnels, composed via threads
- 80 Days: per-route files with episodic isolation
- Overboard!: core spine + patchwork diversions via tunnels with read-count safety

### Source material (from .memory/ink-reference/)
- 3-04-temporary-variables.md — temp, params, recursive knots, divert target typing
- 3-05-functions.md — declaration, return, inline calling, ref params, no flow control allowed
- 4-01-tunnels.md — syntax, ->->, nested tunnels, advanced returns
- 1-06-includes-and-stitches.md — INCLUDE at file top, no namespacing

## Teaching Arc (8 sections)

1. **"Temp Variables: Scratch Paper"** — `~ temp`, scope, bridge from L03's note
2. **"Knot Parameters"** — `=== accuse(who) ===`, one knot serving multiple callers
3. **"Functions: Inline Computation"** — `=== function name() ===`, return, inline calling
4. **"Functions That Don't Return"** — text-producing functions, side-effect-free printing
5. **"Tunnels: Sub-Scenes That Return"** — `-> knot ->`, `->->`, full story features inside
6. **"When to Use What"** — decision framework: function vs tunnel vs stitch vs knot
7. **"INCLUDE: Splitting Into Files"** — `INCLUDE filename.ink`, organization patterns
8. **"The Complete Reference Story"** — function for damage, tunnel for shared camp scene, params for enemy names

## Deferred
- Threads (<-) → lesson 08 or expansion
- ref parameters — note callout only
- Recursive knots — note callout only
- Tunnel with variable target — note callout (advanced/risky)

## Acceptance criteria

- [ ] Lesson HTML at examples/ink-godot/lessons/0004-ink-functions-and-tunnels.html
- [ ] Reference .ink story compiled via inklecate (0 errors, 0 warnings)
- [ ] README.md in reference/code/ink-functions-and-tunnels/ directory
- [ ] mise run ink:validate passes
- [ ] Glossary terms annotated (jargon pass)
- [ ] check-lesson.py passes
- [ ] Exercise answer compiles clean
- [ ] Independent subagent review passes
