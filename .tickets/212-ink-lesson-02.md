---
id: "212"
title: "Ink Lesson 06: Tags as Commands"
status: done
blocked_by: ["211"]
priority: high
tags: [ink]
---

# Ink Lesson 06: Tags as Commands

Tag protocol design, parsing tags for speaker/audio/camera/items, driving game systems from ink without coupling.

## Acceptance criteria

- [x] Lesson HTML at examples/ink-godot/lessons/
- [x] Reference .ink story compiled via inklecate (0 errors, 0 warnings)
- [x] README.md in reference/code/ directory
- [x] mise run ink:validate passes
- [x] Glossary terms annotated (jargon pass)
- [x] check-lesson.py passes

## Findings-adjusted plan (2026-08-27, 4 subagents: 2 research + 2 review)

Raw: `.scratch/research/{tag-protocols,protocol-teaching}.md`, `.scratch/review/{ebb-tagprocessor,inkgd-tags-continuity}.md`.

### CRITICAL technical finding — the loop must change
Lesson 05 uses `continue_story_maximally()`, which collapses multiple lines and leaves `current_tags`
reflecting only the LAST line — per-line tags are lost. Lesson 06 MUST use a single-step
`while can_continue: continue_story()` loop, reading `current_text` + `current_tags` each iteration
(or the `continued(text, tags)` signal). This IS a lesson beat: it's the concrete reason the
maximally-vs-single distinction (deferred in L05) matters now.

### Confirmed facts
- inkgd tag API (L2, addon source): `current_tags: Array` / `get_current_tags()` per line;
  `global_tags` / `get_global_tags()` story-level; `continued(text, tags)` signal. All null-guard → `[]`.
- Filename/slug CONFIRMED: `0006-tags-as-commands.html`, slug `tags-as-commands` (MAP + L05 What's Next agree).
  Reference dir: `reference/code/tags-as-commands/` (name correct from the start).
- Tag syntax (L2 inkle): `#` to EOL; `# key: value` colon is PLAIN TEXT the game splits, not ink syntax;
  multiple tags per line; scopes = per-line / knot / global.

### Pedagogy (pain-first + threshold misconception)
- Motivate by PAIN: show the coupled version (hardcode `if speaker == "Alfoz"`), then a change it can't
  absorb (rephrase/add speaker/localize). Name the cost. Then introduce the tag protocol as relief.
- Exercise misconception (Ink's own design philosophy): matching on DISPLAYED TEXT
  (`if text.begins_with("Alfoz:")`) instead of a STABLE PROTOCOL KEY (`# speaker: Alfoz`). Breaks silently on
  rephrase/localization. Handle: "display text is for humans; the protocol key is for the machine."

### Simplified vocabulary (from ebb L1 TagProcessor — teach core, cite the ~30-command production scale)
- `# speaker: Alfoz` — set name label (dispatch, no arg)
- `# sound: coin_drop` — command with value (dispatch + argument)
- `# hidden` — suppress line text while side effects still run (boolean-return contract)
Use colon `key: value` + GDScript `split(":")` + `match` dispatch. DEFER Ebb's consume-next-tag queue,
DC/FC checks, `.variable` ops (mention as production scale). Reference story deterministic (no RANDOM in
tags) → earns a golden transcript.

### Deliverables + validation (mirror #211)
Reference `.ink` (tagged, deterministic, golden transcript), `story_player.gd` (single-step loop) in
`reference/code/tags-as-commands/`, tags-flow SVG, ~7-term glossary, misconception exercise, 5 SR questions.
Validate: check-lesson (incl Q15), ink:validate, verify-links, browser render. Regenerate map + index
(index needs explicit `--output examples/ink-godot/lessons/index.html`).

## Resolution (2026-08-28)

Lesson 0006-tags-as-commands.html authored (tag protocol, pain-first, single-step-loop beat, dispatch SVG, suppress contract, misconception exercise); deterministic tagged reference .ink + golden transcript; story_player.gd single-step loop + match dispatcher; 5 SR questions; map+index regenerated
