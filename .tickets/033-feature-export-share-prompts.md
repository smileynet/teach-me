---
id: "033"
title: "Feature: export SR questions to Anki format"
status: open
priority: medium
blocked_by: []
type: feature
---

# Feature: export SR questions to Anki format

## What to build

Export a topic's question bank to Anki `.apkg` format so learners can share curated question sets or use Anki's mobile app for on-the-go review.

## Why

Anki has the largest flashcard ecosystem — exporting to `.apkg` lets learners:
- Review on their phone (AnkiDroid / AnkiMobile)
- Share decks with colleagues studying the same topic
- Use Anki's superior mobile UX for quick daily reviews

## Approved Design

### Two Note Models

1. **TeachMe — Explain** (for explain/compare/apply/predict cards)
   - Front: prompt (+ code block if prompt_code)
   - Back: expected_answer (+ code block if answer_code)
   - Source: rendered HTML links from `sources` field
   - Context: lesson_id, section_heading

2. **TeachMe — QuickCheck** (for multiple-choice cards)
   - Front: prompt (+ code block if prompt_code)
   - Back: correct option highlighted + explanation
   - Source: rendered HTML links from `sources` field
   - Context: lesson_id, section_heading

### Key Decisions

- **Library**: `genanki` (only dependency)
- **GUID strategy**: `genanki.guid_for(card.id)` — deterministic from our UUID, so re-exports update rather than duplicate
- **Tags**: hierarchical — `topic::iceberg-on-aws`, `type::explain`, `tier::apply`, `lesson::0001-iceberg-metadata-tree`
- **Sources**: rendered as `<a href>` links in Source field (answer side only)
- **Scheduling**: NOT exported — Anki reschedules on import; we export content only
- **Media**: v1 = text only; v2 = SVG diagrams as media files (deferred)
- **No cloze conversion** — quick-check stays as explicit Q&A, not synthetic clozes

### What NOT to do

- No markdown parsing pipeline (genanki takes raw HTML)
- No bidirectional sync with Anki
- No custom JS/theme system
- No AnkiConnect API integration
- No scheduling data export (different algorithm, different intervals)

### CLI

```bash
mise run sr:export-anki                          # all topics
mise run sr:export-anki -- iceberg-on-aws        # one topic
mise run sr:export-anki -- --output ~/deck.apkg  # custom output path
mise run sr:export-anki -- --exclude-suspended   # skip suspended cards
```

### Implementation

~150 lines in `tools/export_anki.py`:
1. Define two genanki Models with stable IDs and HTML templates
2. Read cards from JSONL, map to notes
3. Generate stable GUIDs
4. Build deck, package, write .apkg

## Acceptance criteria

- [x] Design approved (proposal reviewed 2026-08-10)
- [ ] `genanki` added as dependency
- [ ] `tools/export_anki.py` produces valid `.apkg` file
- [ ] Both note types work (Explain + QuickCheck)
- [ ] Cards preserve: prompt, expected answer, tags, source links
- [ ] Exported deck importable into Anki desktop
- [ ] Re-export updates cards (stable GUIDs), not duplicates
- [ ] Suspended/mastered cards optionally excluded
- [ ] `mise run sr:export-anki` task wired up
