---
id: "111"
title: "Fix topic state logic — status must reflect actual generated content"
type: fix
status: done
priority: high
blocked_by: []
---

# Fix topic state logic — status must reflect actual generated content

## Problem

The index page shows "0/7" and map page shows all topics as "not started" even though we have a generated lesson (0001-esoteric-ebb-breakdown), a reference doc, a quiz page, and 4 SR questions for the first topic. The state logic is disconnected from reality.

## Root cause investigation needed

Where does topic status come from?
1. MAP.md `status:` field — manually set, never auto-updated after generation
2. `generate_map_page.py` reads the MAP.md status field verbatim
3. Nothing updates MAP.md when a lesson is generated
4. The index page reads topic counts from MAP.md via `parse_map_meta()`

The system SHOULD detect:
- Lesson file exists → topic is at least "in-progress"
- Lesson + reference + quiz all exist → topic is "complete"
- No content exists → "not-started"

## Acceptance Criteria

- [ ] Topic status derives from actual files on disk, not just MAP.md text
- [ ] If `lessons/0001-esoteric-ebb-breakdown.html` exists, that topic shows "in-progress" or "complete"
- [ ] Index page progress ring reflects real completion
- [ ] Map page card badges reflect real status
- [ ] Status detection runs at page generation time (in Python generators)
- [ ] MAP.md status field is updated as a side effect of generation (keeps it in sync for other tools)
- [ ] Document the status lifecycle: not-started → in-progress (lesson exists) → complete (lesson + quiz + reference)

## Investigation areas

1. `tools/generate_map_page.py` — where does it read status? Does it cross-check files?
2. `tools/map_parser.py` — does `update_status()` get called anywhere in the generation flow?
3. `tools/check-topic-completeness.py` — this tool already knows what's missing per topic; can its logic feed status?
4. The teach skill — after generating a lesson, does it call `update_status()`?

## Context

- MAP.md: `workspace/maps/blender-godot-shaders.MAP.md` — all topics say `not-started`
- But lesson exists: `workspace/lessons/0001-esoteric-ebb-breakdown.html`
- Reference exists: `workspace/reference/0001-esoteric-ebb-breakdown.html`
- Quiz exists: `workspace/lessons/quiz/0001-esoteric-ebb-breakdown-quiz.html`
- Questions exist: `workspace/learning-records/questions/blender-godot-shaders.jsonl` (4 cards)
- `tools/map_parser.py` has `update_status(path, slug, new_status)` — it's just never called

## Resolution (2026-08-13)

TBD
