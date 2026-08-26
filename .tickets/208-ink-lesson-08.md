---
id: "208"
title: "Ink Lesson 02: Choices, Stitches and Weave"
status: done
blocked_by: []
priority: high
---

# Ink Lesson 02: Choices, Stitches and Weave

Once-only vs sticky choices, text suppression brackets, stitches as sub-sections, gathers for inline convergence, nested choices, fallback choices.

## Research Findings (2026-08-25)

### Teaching sequence (Unofficial Ink Cookbook + pedagogy research)
- Ink Cookbook order: choices → weaves → selective output → gathers → sticky/once-only → stitches
- Critical insight: teach convergence (gathers) BEFORE complex branching — prevents "combinatorial explosion" fear
- Funnel pattern (choices → same outcome) is the best first exercise shape for beginners
- "Choices ≠ branching" — micro-decisions are legitimate and should be shown early

### Production patterns (80 Days, Heaven's Vault)
- 80 Days written "almost exclusively in weave" — validates weave as the core tool
- Architecture: scene = knot, beat = stitch, dialogue branch = weave
- 2-3 nesting levels is practical maximum; escape hatch: divert to stitch
- Gathers for local/cosmetic convergence; diverts for major scene transitions

### Common beginner mistakes to address
- Combinatorial explosion fear (every choice doubles content)
- Once-only choices vanishing in loops (need sticky `+`)
- Missing space after `*` (syntax trap)
- Mismatched gather nesting levels
- Deep nesting becoming unreadable

### Source material (from .memory/ink-reference/)
- 1-02-choices.md — bracket zones (before/inside/after)
- 1-06-includes-and-stitches.md — stitch syntax, local diverts, header content gotcha
- 1-07-varying-choices.md — once-only, sticky, fallback, conditional preview
- 2-01-gathers.md — gather syntax, weave philosophy, chained gathers
- 2-02-nested-flow.md — nested **/ -- levels, when to escape to stitches

## Teaching Arc (8 h2 sections + complete file)

1. Your First Choice — basic `*`, funnel pattern (converges immediately)
2. Bracket Tricks — `[text]` zones for dialogue
3. Once-Only vs Sticky — `*` vs `+`, loop problem, fallback safety net
4. Stitches: Rooms Inside Rooms — `= name`, local diverts, extending lesson 01 metaphor
5. Gathers: Where Branches Rejoin — `-` gather, the Fogg example, core payoff
6. Weave: Choices + Gathers Together — chained gathers, multi-beat sequences
7. Nested Choices (and When to Stop) — `**`/`--`, 2-3 level rule, escape hatch
8. The Complete Reference Story — full assembled file

## Deferred to later lessons
- Conditional choices → lesson 03 (Variables & Conditionals)
- INCLUDE multi-file → mentioned but not demonstrated
- Labelled gathers/options → lesson 03 or later (tracking a weave)

## Acceptance criteria

- [ ] Lesson HTML at examples/ink-godot/lessons/0002-ink-choices-and-weave.html
- [ ] Reference .ink story compiled via inklecate (0 errors, 0 warnings)
- [ ] README.md in reference/code/ink-choices-and-weave/ directory
- [ ] mise run ink:validate passes
- [ ] Glossary terms annotated (jargon pass)
- [ ] check-lesson.py passes
