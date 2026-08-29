---
domain: ink-godot
description: "Master ink narrative scripting and integrate it with Godot 4 — from basic story flow through production-scale game architecture"
generated: 2026-08-24
depth: 0
parent: null
leads_to:
  - interactive-fiction
  - game-narrative-design
---

# Ink + Godot: Narrative Scripting

## Orientation

Ink is a narrative scripting language by Inkle Studios — the engine behind 80 Days, Heaven's Vault, and Esoteric Ebb. It separates story logic from game code: writers work in plain-text `.ink` files, programmers integrate via a runtime API. This track teaches ink from zero, then wires it into Godot using the inkgd addon (pure GDScript, no .NET required).

Phase A (lessons 01–04) is engine-agnostic — you write ink in the Inky editor and learn the language itself. Phase B (lessons 05–08) integrates with Godot, building a playable narrative prototype that demonstrates production patterns from a shipped 500K-word game.

## Topics

### ink-flow-and-knots
- **id:** 01M174TQPVJ8DXJ9XHG6PYVSJC
- **title:** Flow & Knots
- **why:** Stories in ink are built from named sections (knots) connected by diverts — understanding this flow is the foundation for everything that follows
- **scope:** substantial
- **prereqs:** []
- **lesson_file:** 0001-ink-flow-and-knots.html

### ink-choices-and-weave
- **id:** 01M174TQPVXSXEVPRYM5QNNWT3
- **title:** Choices, Stitches & Weave
- **why:** Choices are how players interact with ink — once-only vs sticky, nested branches, stitches for organizing within knots, and the gather pattern that prevents spaghetti convergence
- **scope:** substantial
- **prereqs:** [ink-flow-and-knots]
- **lesson_file:** 0002-ink-choices-and-weave.html

### ink-variables-and-conditionals
- **id:** 01M174TQPV20MTTGH29SMYCZ24
- **title:** Variables & Conditionals
- **why:** Tracking state across knots lets stories remember what the player did — conditional content, read counts, and variable types make stories reactive
- **scope:** substantial
- **prereqs:** [ink-choices-and-weave]
- **lesson_file:** 0003-ink-variables-and-conditionals.html

### ink-functions-and-tunnels
- **id:** 01M174TQPVTPB3VFTCRBX3KJFG
- **title:** Functions & Tunnels
- **why:** Reusable logic keeps large ink projects manageable — pure functions for computation, tunnels for scene templates that return to the caller
- **scope:** substantial
- **prereqs:** [ink-variables-and-conditionals]
- **lesson_file:** 0004-ink-functions-and-tunnels.html

### godot-ink-integration
- **id:** 01M174TQPVDXGR1JFAHZ15J7XH
- **title:** First Godot Integration
- **why:** Loading an ink story in Godot, displaying text line-by-line, and handling player choices via the InkPlayer node — the bridge from writing to playing
- **scope:** substantial
- **prereqs:** [ink-functions-and-tunnels]
- **lesson_file:** 0005-godot-ink-integration.html

### tags-as-commands
- **id:** 01M174TQPV6FWNWQJS1JRC5ADW
- **title:** Tags as Commands
- **why:** Ink tags become structured game commands (speaker, audio, camera, items) — a protocol that drives game systems from narrative without coupling ink to engine code
- **scope:** substantial
- **prereqs:** [godot-ink-integration]
- **lesson_file:** 0006-tags-as-commands.html

### state-bridge
- **id:** 01M174TQPV2FBSAMEKC0Z5DWGH
- **title:** State Bridge (External Functions & Variable Observers)
- **why:** Binding game logic to ink and observing state changes reactively — the two-way communication between story and game that makes narrative-driven gameplay possible
- **scope:** substantial
- **prereqs:** [tags-as-commands]
- **lesson_file:** 0007-state-bridge.html

### production-patterns
- **id:** 01M174TQPV2WJXAXZGWJ2TJ0Q0
- **title:** Production Patterns (Multi-Story, Hub Architecture, Combat-in-Ink)
- **why:** Scaling from one story to hundreds requires architecture — stateless-per-dialog, story variables as a state bus, hub-and-spoke flow, and combat as conversation are patterns from a shipped 500K-word game
- **scope:** deep
- **prereqs:** [state-bridge]
- **lesson_file:** 0008-production-patterns.html

## Expansion Opportunities

Subtopics that could become full topics if the track grows:

- **ink-lists** — the advanced state mechanism (bitfield sets, state machines, quest tracking) used by Heaven's Vault and Esoteric Ebb
- **ink-localization** — multi-language support patterns, string extraction, translation workflows
- **ink-testing** — automated story testing, branch coverage, regression detection at scale
- **storylets** — quality-based narrative (Jon Ingold's pattern) for dynamic content selection
- **save-load-architecture** — ink state serialization, multi-slot saves, state migration between versions
