---
id: "193"
title: "Explore: ink + Godot narrative scripting lesson track"
status: done
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

### Design decisions (resolved 2026-08-24)

1. **GDScript vs C# → GDScript first.** Use godot-ink's GDScript interop for all lessons. Backlog a C# remix of the same lessons (ticket #194) — this is a good first test case for the planned lesson remix feature (#160).

2. **Separate domain MAP → Yes.** `ink-godot.MAP.md` as a standalone domain (not child of godot-gamedev). Cross-domain relationships will be expressed via graph/tags once the global map feature (#155) is implemented.

3. **Prerequisites → Godot fundamentals domain (new, ticket #195).** Phase B needs nodes, scenes, and signals. Rather than prereq specific godot-gamedev lessons, create a "Godot fundamentals" domain that covers just the prereqs needed by all current topic tracks. This domain becomes the shared foundation.

4. **Inky editor → No installation docs in lessons.** Assume learners can install Inky (it's a single download). Create a backlog ticket for a Godot fundamentals domain that covers tooling setup as needed.

5. **Reference project → Always.** Build a small interactive narrative alongside the lessons (ADR 0010). Each lesson produces runnable artifacts. The final project demonstrates all 8 lessons' concepts working together.

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

1. ~~Decision: Resolve the 5 open design decisions above~~ → Resolved (see above)
2. **Spike:** Set up godot-ink in a test project, verify GDScript interop works with Godot 4.7.1
3. **MAP creation:** Write `ink-godot.MAP.md` as standalone domain
4. **Reference project:** Scaffold `ink-test-project/` alongside test-scene
5. **First lesson:** Generate lesson 01 (Flow & Knots) in Inky — no engine dependency

## Related tickets

- #194 — C# ink lesson remix (tests #160 remix feature)
- #195 — Godot fundamentals domain (shared prereqs)
- ADR 0010 — Always build reference projects alongside lessons

## Acceptance criteria (for this exploration ticket)

- [x] References cloned and reviewed
- [x] Research completed (ink language, ecosystem, teaching, advanced patterns)
- [x] Proposed lesson arc documented with win statements
- [x] Open decisions identified
- [x] Design decisions resolved
- [x] Spike: inkgd (godot4 branch) installed in ink-test-project, hello.ink compiled, scene scaffolded, headless import passes
- [x] Full interactive validation (open editor, confirm story plays through choices) — validated via godot_editor agent 2026-08-24
- [x] MAP file created (`ink-godot.MAP.md`)
- [x] First lesson generated (01: Flow & Knots)
