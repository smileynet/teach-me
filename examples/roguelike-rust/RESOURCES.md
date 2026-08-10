# Resources

## Primary sources

| Resource | Type | Trust | Status | Notes |
|----------|------|-------|--------|-------|
| [Rust Roguelike Tutorial (bfnightly)](https://bfnightly.bracketproductions.com/) | Book | High | ⚠️ Uses bracket-lib (unmaintained since 2022) + specs (inactive) | Concepts are excellent; rendering stack and ECS library are outdated. Read for architecture understanding, not for stack choice. |
| [Hands-on Rust (Wolverson, 2021)](https://pragprog.com/titles/hwrust/hands-on-rust/) | Book | High | ⚠️ Same caveat — bracket-lib + Legion | Commercial book, well-written. Author has since moved to Bevy. |
| [Advanced Hands-on Rust (Wolverson, Oct 2025)](https://pragprog.com/titles/hwrust2/) | Book | High | ✅ Current — uses Bevy v0.15.1 | Sequel updated to modern stack. Acknowledges bracket-lib era is over. |
| [Bob Nystrom — Game Programming Patterns](https://gameprogrammingpatterns.com/) | Book (free) | High | ✅ Evergreen | Language-agnostic architecture (game loop, component, observer). Best intro to game architecture for non-game-devs. |
| [RogueBasin](http://www.roguebasin.com/) | Wiki | Medium | ✅ Active | Algorithms (map gen, FOV, pathfinding), design articles. Community-maintained. |
| [gridbugs.org — Roguelike Architecture](https://www.gridbugs.org/) | Blog | High | ✅ Active Rust roguelike dev | Practitioner perspective: "ECS systems don't map well to turn-based games — actions+rules pattern works better." |

## Libraries (current as of 2026)

| Library | Purpose | Status | Recommendation |
|---------|---------|--------|----------------|
| `ratatui` + `crossterm` | Terminal rendering | ✅ Very active | **Start here** for ASCII roguelikes. Simple, well-documented. |
| `macroquad` | 2D graphical rendering | ✅ Active | Best for tile-based or when you want graphics without a full engine. Fast compiles. |
| `hecs` | Minimal ECS | ✅ Active | If you choose ECS — smallest API, easy to understand. |
| `shipyard` | Fast ECS (sparse-set) | ✅ Active | Good for dynamic add/remove (status effects). |
| `slotmap` / `thunderdome` | Generational arenas | ✅ Active | **Pragmatic alternative to ECS** — simpler entity management for <1000 entities. |
| `bevy` | Full game engine | ✅ Very active | Overkill for a learning roguelike. Unstable API, long compiles. |
| `bracket-lib` | Roguelike toolkit | ❌ Frozen (Oct 2022) | Do NOT use for new projects. CI broken, deps outdated. |
| `specs` / `legion` | ECS libraries | ❌ Inactive | Do NOT use. Unmaintained. |
| `rand` + `rand_xoshiro` | Random number generation | ✅ Active | Standard choice. Use fixed-width types for cross-platform reproducibility. |

## Architecture approaches (from community)

| Approach | When to use | Tradeoff |
|----------|------------|----------|
| **Plain structs + enums** | First roguelike, 7DRL, <500 entities | Simplest. 90% of composition with 10% of ECS complexity. |
| **Generational arena** (slotmap) | Medium project, stable entity references needed | Lightweight entity management without full ECS overhead. |
| **ECS** (hecs/shipyard) | Large scope, many entity types, data-driven content | Powerful composition but adds indirection and cognitive overhead. Cache benefits unmeasurable at roguelike scale. |
| **Actions+rules pattern** | Turn-based games specifically | Each turn produces actions; rules evaluate them in order. Maps better to turn-based than ECS systems. |

## Communities

| Community | Why | Link |
|-----------|-----|------|
| r/roguelikedev | Weekly Sharing Saturday, beginner-friendly, architecture discussions | https://www.reddit.com/r/roguelikedev/ |
| Roguelike Discord | Real-time help | https://discord.gg/9pmFGKx |
| 7DRL Challenge | Annual jam — forces you to finish | https://7drl.com/ |

## What experienced devs warn newcomers about

1. **Overengineering** — building an engine before building a game. Start with the simplest thing that works.
2. **Wrong tool for the job** — ECS for a 200-entity turn-based game is organizational overhead with no performance benefit.
3. **Scope creep** — build @ → movement → map → FOV → monsters → combat FIRST. Everything else is polish.
4. **Following outdated tutorials blindly** — the bracket-lib tutorial teaches concepts well but its stack is dead. Adapt, don't copy.
5. **Not playing roguelikes** — you can't design a good one without playing DCSS, Brogue, Cogmind, or similar.
