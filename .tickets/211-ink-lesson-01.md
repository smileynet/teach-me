---
id: "211"
title: "Ink Lesson 05: First Godot Integration"
status: done
blocked_by: ["210"]
priority: high
tags: [ink]
---

# Ink Lesson 05: First Godot Integration

Loading ink stories via inkgd InkPlayer, displaying text, handling choices via signals, the runtime loop in GDScript.

## Acceptance criteria

- [x] Lesson HTML at examples/ink-godot/lessons/
- [x] Reference .ink story compiled via inklecate (0 errors, 0 warnings)
- [x] README.md in reference/code/ directory
- [x] mise run ink:validate passes
- [x] Glossary terms annotated (jargon pass)
- [x] check-lesson.py passes

## Findings-adjusted plan (2026-08-27, 4 subagents: 2 research + 2 review)

Raw: `.scratch/research/{inkgd-api,inkgd-pitfalls,integration-pedagogy,ink-godot-tutorials-prior-art}.md`,
`.scratch/review/{lesson05-conventions,gdscript-reference-review}.md`.

### Groundwork done
- Reference `.ink` story (deterministic) compiles 0/0, golden transcript committed, replays 3/3.
- Reference code dir + README + downloadable `story_player.gd` (GDScript review: API-correct, no drift).
- **Filename fixed:** lesson 04's What's Next links `0005-godot-ink-integration.html` → lesson file is
  `0005-godot-ink-integration.html`, slug `godot-ink-integration`. Reference dir renamed from
  `ink-first-godot-integration/` → `godot-ink-integration/` (old name would have 404'd downloads).

### Authoring changes from findings
1. **"Print before you paint" arc** (universal across all prior-art tutorials): stage the GDScript build
   console-print → Label text → choice buttons → advance+cleanup, with narrative framing between blocks.
2. **Exercise = the confirmed #1 misconception**: sequential-vs-event-driven — reading `current_text`
   before the `loaded` signal fires. Teaching device: log in the handler + at the call site, predict order.
3. **Validation-first bridge**: open by connecting back to lessons 01-04 (`ink:validate` + golden transcript)
   — a differentiator no existing tutorial has.
4. **Lean callouts**: brief addon-decision (inkgd/GDScript vs godot-ink/C#, one-line criterion), gotcha on
   `__InkRuntime`/`_ready()` timing → deferred `create_story()`, key-concept "never touch story before loaded(true)".
   Defer signal-vs-while-loop to a note.
5. **State 3 runtime prereqs** (from GDScript review): scene tree (TextLabel/ChoicesContainer direct children),
   `.ink.json` declares `torch_lit`, `bbcode_enabled=true` for [color] messages.

### Shell (confirmed from conventions review)
Head order (typography-prefs.js → style.css → glossary.css → 5-import importmap); breadcrumb
All Lessons › Ink + Godot › {current}; lesson-meta `Lesson 5 · Ink + Godot · ~M min read` + Win;
key-concept; box-drawing `═` section comments; glossary-data = flat `{"slug":"definition"}` strings;
`../assets/page-shell.js` module as last line; runtime-loop SVG follows visual-teaching (role/title/viewBox/var(--svg-*)).

## Resolution (2026-08-27)

Lesson 0005-godot-ink-integration.html authored (inkgd runtime loop, print-before-paint, SVG diagram, 7-term glossary, misconception exercise); deterministic reference .ink story + golden transcript; downloadable story_player.gd validated against spike; 5 SR questions; map+index regenerated


## Correction (2026-08-28, via #236) — a runtime bug shipped in this lesson, now fixed

#211 closed with story_player.gd validated by API-matching, not by running it in Godot.
The #235 headless harness (built after) caught a real bug: `_advance_story` used
`continue_story_maximally()` then read `_ink_player.current_text` — but through inkgd's
InkPlayer wrapper, maximal-continue returns (and current_text holds) only the LAST line
of a multi-line passage. So the Godot player silently dropped the opening narration
("You stand at the mouth of a cave...") and showed only the final line.

The golden transcript missed it because `play-ink.py` captures bink's continue RETURN
VALUE (the full concatenated text), which is correct — the divergence is specific to the
InkPlayer property/return through Godot.

Fixed in #236: switched _advance_story to a single-step `while can_continue:
continue_story()` accumulate loop (the only way to show a full passage through InkPlayer).
Mirrored into the lesson HTML complete-block, spike_story.gd, prose (walkthrough, glossary,
the maximal-continue gotcha note, SVG labels), and SR ig-05-003. Golden transcript unchanged
(story untouched). Re-validated: `mise run ink:validate-gd` L05 now GREEN, check-lesson 13/0,
links + transcripts pass.
