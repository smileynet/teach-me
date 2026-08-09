---
id: "033"
title: "Feature: export/share SR question sets"
status: open
priority: low
blocked_by: []
type: feature
---

# Feature: export/share SR question sets

## What to build

Export a topic's question bank into a portable format that another learner (or another teaching workspace) can import.

## Why

When the teach-me system matures and skills deploy globally, learners working on the same topic shouldn't need to regenerate all cards from scratch. A curated question set is a reusable artifact.

## Design sketch

Formats to consider:
- **JSONL (native)** — just copy the file; simplest
- **Markdown (repeater-compatible)** — `Q:/A:/C:` syntax for interop with repeater CLI
- **Anki .apkg** — broadest ecosystem reach (via genanki Python library)

Export: `python tools/sr-export.py <topic> --format jsonl|markdown|anki`
Import: `python tools/sr-import.py <file> --topic <slug>`

Import should:
- Assign new UUIDs (avoid collisions)
- Set schedule to "new" (recipient hasn't reviewed these)
- Preserve provenance metadata

## Open questions

- Which format(s) to support first? JSONL is trivial, Anki has ecosystem value
- Should export include review history or just content?
- How to handle cards that reference lesson sections the recipient doesn't have?

## Acceptance criteria

- [ ] Export command produces portable file from a topic's JSONL
- [ ] Import command adds cards to a topic with fresh schedule state
- [ ] At least one format beyond native JSONL (markdown or Anki)
- [ ] Provenance preserved (original lesson_id, generated_by)
- [ ] No UUID collisions on import
