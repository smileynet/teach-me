---
created_at: 2026-08-25T07:01:00-07:00
base_commit: 8743709
handoff_key: ink-godot-lessons
---

# Handoff

## Objective
Generate 7 remaining ink+Godot lessons (#208-214) after completing infrastructure gates (#201, #205, #206).

## Constraints
- inkgd (godot4 branch, v0.6.0) is the runtime — no .NET required. Standard Godot 4.7.1 works.
- inklecate at `D:\tools\inklecate\inklecate.exe` (downloaded from GitHub releases).
- `mise run ink:validate` validates all .ink stories (tool built this session, #200 done).
- serve.py serves one workspace at a time (`--workspace examples/ink-godot` for ink content). #198 tracks the multi-workspace fix.
- `examples/*/lessons/` is gitignored — use `git add -f` for lesson HTML.
- WritingWithInk.md (124KB) at `.references/ink/Documentation/` is the authoritative reference.

## Prior Decisions
- ADR 0009: MKToon as sibling MAP (fork from toon-banding). ADR 0010: always build reference projects.
- ink track uses GDScript (not C#). C# remix deferred to #194 (tests remix feature #160).
- Separate MAP domain (`ink-godot.MAP.md`), not child of godot-gamedev.
- Stitches placement: recommended for lesson 02 (#206 — decision ticket open, recommendation is "add to lesson 02").

## Current State
- MKToon track COMPLETE (6 lessons, 0009-0014, all shaders validated).
- Ink track: lesson 01 done + validated (godot_editor + ink:validate + check-lesson + jargon pass).
- Ink-test-project spike working (inkgd loads stories, choices work, variables update).
- 4 high-pri gates before lesson generation: #201 (index docs), #205 (fix warning), #206 (stitches), #207 (lesson 01 rewrite).
- Tickets #208-214 created for lessons 02-08 with correct dependency chain.

## Next Steps
1. **#201** — Index `WritingWithInk.md` + `RunningYourInk.md` in knowledge base (unblocks all lesson generation)
2. **#206** — Decide stitches placement (quick decision: add to lesson 02 title, update MAP)
3. **#205/#207** — Fix lesson 01 warning + fallthrough framing (may be same fix)
4. **#208** — Generate lesson 02 (Choices, Stitches & Weave) — first in the chain
5. Continue #209-214 sequentially

## Fog
- #207 ("Lesson 01 falsely teaches knot fallthrough") appeared on the ready list but wasn't created this session — investigate its content and whether it conflicts with #205.
- Whether inkgd's godot4 branch will receive future maintenance is unknown — pin to current commit in the reference project if stability is needed.

## Evidence
- ink:validate passes: `mise run ink:validate` → 2 files, 0 errors, 0 warnings
- Godot editor validation: spike story plays through (confirmed via godot_editor agent)
- Visual QA: browser agent confirmed map page (8 cards, correct badges, DAG arrows) and lesson page (code blocks, exercise, glossary tooltips, dark theme)
- tkt validate: pass (after cleanup)
