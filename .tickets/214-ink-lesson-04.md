---
id: "214"
title: "Ink Lesson 08: Production Patterns"
status: in_progress
blocked_by: ["213"]
priority: high
tags: [ink]
---

# Ink Lesson 08: Production Patterns

Multi-story architecture, stateless-per-dialog, SVs as state bus, hub-and-spoke, combat-as-dialog. From Esoteric Ebb (286 stories, 500K words).

## Context
Final Phase-B lesson. Inherit the established pattern from lessons 05–07 (see #213's Context
block): file `examples/ink-godot/lessons/0008-production-patterns.html`, reference code at
`reference/code/production-patterns/`, single-step `continue_story()` accumulate loop (NEVER
maximal — #236), deterministic reference story with top-level `-> start` + golden transcript,
runtime-validated via `mise run ink:validate-gd` (add a lesson-08 harness check + sync-map entry).
Source material: the ebb-analyzer patterns (`.scratch/subagent-raw/review-ebb-*.md` from #193) —
tags-as-commands (#212) is the foundation this builds on. This is the capstone: multi-story
architecture where each dialog is stateless and Story Variables are the cross-story bus.

## Findings (2026-08-28 — research + review subagents; see .scratch/subagent-raw/214-findings.md)

- **Source note:** the `.scratch/subagent-raw/review-ebb-*.md` from #193 are GONE (ephemeral). PRIMARY
  source re-read fresh from disk: `D:\code\ebb-analyzer\docs\tutorial-ink-godot-integration.md` +
  `tutorial-ink-unity-gameplay-loop.md` [L4].
- **Teaching arc (chosen):** SV bus → stateless-per-dialog → hub-and-spoke (state-model → persistence →
  runtime). Combat-as-dialog DEPENDS on all three → OPTIONAL payoff demo, not a core beat.
- **Capstone = ~ZERO new syntax**, composing L01-L07 with explicit callbacks. SV bus = get_variable/
  set_variable (L07); hub-and-spoke = sticky choices + gathers (L02/L04); drain loop = L06 single-step.
- **Exercise = threshold misconception:** beginners make the .ink file OWN world state (read counts/self-
  loops). Threshold: ink is middleware; durable state lives in the HOST ENGINE. Multi-requirement NPC spec
  + embed the "store the flag inside the ink file" misconception, ask why it fails.
- **RISK:** Ebb tutorials are godot-ink (C#); our track is inkgd (GDScript). TRANSLATE, don't copy; keep
  GDScript minimal; validate every snippet against the real inkgd API.
- **Golden transcript OPPORTUNITY:** design the reference story PURE-INK (SV bus via VAR, hub via sticky
  choices, no unbound EXTERNAL, no RNG) so it CAN have a golden transcript — stronger than L07.
- **Conventions:** breadcrumb `›` (U+203A), lesson-meta `·` (U+00B7) — two glyphs, don't conflate. FINALE:
  What's Next → MAP Expansion Opportunities (ink-lists, storylets, localization), NOT a lesson 09 (confirmed
  no lesson-09 node). Harness template = _validate_lesson07 (validate_runtime.gd:149-192); add await after L07.

## Acceptance criteria

- [x] Lesson `examples/ink-godot/lessons/0008-production-patterns.html` (Win + key-concept + SVG + glossary + exercise)
- [x] Reference `.ink` story(ies): deterministic, compile 0/0, top-level `-> start`; golden transcript(s) committed
- [x] README.md in `reference/code/production-patterns/`
- [x] `mise run ink:validate` + `mise run ink:transcripts` pass
- [x] `mise run ink:validate-gd` passes — harness check added for lesson 08
- [x] `mise run verify` passes incl. `check-lesson-code.py` (compiles the .ink + validates story_player.gd) — #231 gate
- [x] Glossary terms annotated (Q15) + `check-lesson.py` passes
- [x] 5 SR questions (ig-08-*); map + index regenerated (explicit `--output`)

## Resolution (2026-08-28) — TRACK CAPSTONE, completes the 8-lesson ink+Godot arc

Lesson 08 "Production Patterns" authored. Capstone teaching architecture (not a new primitive) via three
patterns, arc SV bus → stateless-per-dialog → hub-and-spoke, with combat-as-dialog as an optional payoff.
Framed against Esoteric Ebb (286 stories). Threshold-misconception exercise: a dev stores a cross-
conversation fact as a read count inside one ink file → why it fails (ink files are stateless views;
durable state lives on the engine-owned bus).

Deliverables: `0008-production-patterns.html` (Win + "After this lesson" key-concept + multi-story/SV-bus
SVG + 4-term glossary + synthesis exercise + Code Files, finale What's Next → MAP Expansion Opportunities);
reference `08_production_patterns.ink` (PURE ink — state-bus VARs gating a re-enterable tavern hub,
deterministic, compiles 0/0) + `story_player.gd` (unchanged L06 drain loop + read_flag helper) + README;
`lesson08_player.tscn` + sync-map entries; `_validate_lesson08()` harness; 5 ig-08 SR cards; MAP status →
complete; map + index regenerated.

**Stronger validation than L07:** pure-ink design earned a real GOLDEN TRANSCRIPT (ink:transcripts 5/5,
including 08 — the state bus gating content is regression-tested). Runtime-validated in real Godot
(ink:validate-gd PASS): state-bus flags start false with 3 hub choices (gated content hidden), then
asked_name=true unlocks a gated choice (4 choices). Handled the godot-ink(C#)→inkgd(GDScript) risk by
translating patterns and keeping the player identical to L06.

Note: transcript file must be written UTF-8 via Python (PowerShell `>` redirection mangled an em-dash to
cp1252 0x97 — the tool reads UTF-8 and choked; re-captured with Python open(encoding='utf-8')).

Evidence: `mise run verify` EXIT 0 (check-lesson-code 5 compiled/0 failed, transcripts 5/5, verify-links);
`ink:validate-gd` PASS (L05/06/07/08); `check-lesson.py --workspace examples/ink-godot` 0008 = 12 pass/0
fail. **This completes the entire ink+Godot lesson track (01–08).**
- [ ] `mise run verify` passes incl. `check-lesson-code.py` (compiles the .ink + validates story_player.gd) — #231 gate
- [ ] Glossary terms annotated (Q15) + `check-lesson.py` passes
- [ ] 5 SR questions (ig-08-*); map + index regenerated (explicit `--output`)
