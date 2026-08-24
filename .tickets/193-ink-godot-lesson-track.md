---
id: "193"
title: "Explore: ink + Godot narrative scripting lesson track"
status: open
blocked_by: []
priority: medium
type: exploration
---

# Explore: ink + Godot narrative scripting lesson track

## Summary

Propose a lesson track teaching the ink narrative scripting language integrated with Godot 4 — from basic flow/choices through production-scale game integration patterns. Draws on Esoteric Ebb's reverse-engineered architecture (ebb-analyzer tutorials) as the "shipped game" reference, similar to how the MKToon track uses Ebb's shaders.

## Research completed (2026-08-24)

8 subagent passes produced findings at `.scratch/subagent-raw/`:
- `review-ebb-ink-godot.md` — Ebb's Godot integration tutorial (10 sections, tags-as-commands)
- `review-ebb-ink-unity.md` — Ebb's gameplay loop tutorial (7 novel production patterns)
- `review-inkgd.md` — inkgd repo analysis (GDScript, no Godot 4 release)
- `review-godot-ink.md` — godot-ink repo analysis (C#, gold standard, v1.1.2)
- `research-ink-language.md` — ink core features, comparison to alternatives, ecosystem
- `research-ink-godot-ecosystem.md` — 3 Godot options, community consensus
- `research-ink-teaching.md` — learning progression, stumbling points, time to productivity
- `research-ink-advanced.md` — external functions, observers, save/load, multi-story, lists, scale

## Key findings

### The tool decision

| Option | Language | Godot 4 | Maturity | Tradeoff |
|--------|----------|---------|----------|----------|
| **godot-ink** (paulloz) | C# wrapper | ✅ v1.1.2 | Production | Requires .NET Godot build |
| **inkgd** (ephread) | GDScript native | ⚠️ Unreleased branch | Stable for 3.x | No official Godot 4 release |
| **GDRS Ink** | Rust GDExtension | ✅ v0.2.1 | Too new | Best architecture, immature |

**Recommendation for teaching:** Use **godot-ink** (C#) as the primary integration. It's the community gold standard, uses the official ink runtime, has editor integration (preview panel), and full GDScript interop via signals. The .NET requirement is a tradeoff worth teaching (it's what production teams choose).

**Alternative lesson path:** A "pure ink" track that teaches ink language first (in Inky editor, no engine), then integrates. This removes the engine dependency from early lessons.

### What makes this track unique (vs generic ink tutorials)

The ebb-analyzer tutorials document **7 production patterns** not found in standard ink teaching resources:

1. **Tags as command protocol** — ink tags become structured game commands (speaker, audio, camera, items, VFX) rather than just metadata
2. **Stateless per dialog** — each ink file starts fresh; game state lives outside ink (contradicts standard tutorials)
3. **Story Variables as state bus** — 1,825 SVs communicate between 286 stories without shared state within stories
4. **Combat as dialog** — combat encounters run IN ink (choices = actions, tags = resolution), not as separate systems
5. **Choice text as protocol** — choice text contains structured data (dice checks, conditions) parsed by the runtime
6. **Sequential tag parameters** — tags encode ordered parameters for game systems (like command-line args)
7. **Hub-and-spoke dominance** — 87% of stories use hub architecture (talk-until-done pattern)

These are what separate "learned ink from a tutorial" from "shipped a game with ink at scale."

### Proposed lesson progression (8 lessons)

Two phases: ink language fundamentals (engine-agnostic, in Inky), then Godot integration.

#### Phase A: Pure Ink (in Inky editor, no engine)

| # | Topic | Core concept | Win statement |
|---|-------|-------------|---------------|
| 01 | Flow & Knots | Knots, diverts, basic narrative flow | "You can structure a branching story with named sections and explain how diverts control flow" |
| 02 | Choices & Weave | Once-only vs sticky, nested choices, gathers | "You can design choice structures that converge without spaghetti — and explain the gather pattern" |
| 03 | Variables & Conditionals | VAR, temp, conditional content, read counts | "You can track state across knots and show different content based on what the player has done" |
| 04 | Functions & Tunnels | Pure functions, tunnels (->knot->), reusable content | "You can extract reusable logic into functions and create scene templates with tunnels" |

#### Phase B: Godot Integration (godot-ink, C#/GDScript)

| # | Topic | Core concept | Win statement |
|---|-------|-------------|---------------|
| 05 | First Integration | godot-ink setup, running a story, displaying text + choices | "You can load an ink story in Godot, display text line-by-line, and handle player choices via signals" |
| 06 | Tags as Commands | Tag protocol, parsing tags for speaker/audio/camera | "You can design a tag protocol that drives game systems from ink without coupling ink to engine code" |
| 07 | State Bridge | External functions, variable observers, save/load | "You can bind game logic to ink, observe state changes reactively, and persist story state across sessions" |
| 08 | Production Patterns | Hub architecture, multi-story, SVs as bus, combat-in-ink | "You can architect a multi-story ink game using Ebb's patterns — stateless dialogs, variable bus, and combat as conversation" |

### Open design decisions

1. **GDScript vs C# for lesson code?** godot-ink has GDScript interop, but the primary API is C#. Do we teach C# (follows the tool) or show GDScript wrappers (matches the rest of teach-me)?

2. **Separate domain or child of godot-gamedev?** ink is a cross-engine skill — the language lessons (01-04) are engine-agnostic. Option: two MAPs (ink-language as root, ink-godot as child).

3. **Prerequisites?** Phase A needs nothing. Phase B needs basic Godot (nodes, scenes, signals) — possibly prereqs `nodes-and-scenes` + `gdscript-fundamentals` from the godot-gamedev map.

4. **Inky editor requirement?** Lessons 01-04 use Inky (free, cross-platform). Should we document installation or treat it as assumed?

5. **Reference project?** Should we build a small narrative game alongside the lessons (like test-scene for shaders), or keep it abstract exercises?

### References cloned

- `.references/inkgd/` — ephread's GDScript native ink runtime
- `.references/godot-ink/` — paulloz's C# wrapper (primary recommendation)
- `D:\code\ebb-analyzer\docs\tutorial-ink-godot-integration.md` — Ebb's Godot integration patterns
- `D:\code\ebb-analyzer\docs\tutorial-ink-unity-gameplay-loop.md` — Ebb's gameplay loop patterns

### Comparison to MKToon track approach

| Aspect | MKToon (shaders) | Ink+Godot (narrative) |
|--------|-----------------|----------------------|
| Reference source | Ebb's shaders (reverse-engineered) | Ebb's ink architecture (reverse-engineered) |
| "Build from zero" | ✅ Each lesson adds one shader layer | ✅ Each lesson adds one ink concept |
| "Shipped game" comparison | MKToon lite as reference shader | Ebb's 286 stories as reference architecture |
| Engine dependency | Godot only (spatial shaders) | Phase A: none (Inky). Phase B: Godot |
| External tool | None | Inky editor + inklecate compiler |
| Code language | GDShader only | ink + C# (or GDScript via interop) |

## Next steps

1. **Decision:** Resolve the 5 open design decisions above
2. **Spike:** Set up godot-ink in a test project, verify it works with Godot 4.7.1
3. **MAP creation:** Write `ink-godot.MAP.md` (or split into `ink-language.MAP.md` + `ink-godot.MAP.md`)
4. **First lesson:** Generate lesson 01 (Flow & Knots) in Inky — no engine dependency

## Acceptance criteria (for this exploration ticket)

- [x] References cloned and reviewed
- [x] Research completed (ink language, ecosystem, teaching, advanced patterns)
- [x] Proposed lesson arc documented with win statements
- [x] Open decisions identified
- [ ] Design decisions resolved (separate session)
- [ ] Spike: godot-ink running in test project
- [ ] MAP file(s) created
