---
id: "033"
title: "Feature: export SR questions to Anki format"
status: open
priority: low
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

## Design sketch

```bash
python tools/sr-export.py <topic> --format anki --output deck.apkg
python tools/sr-export.py <topic> --format anki --output deck.apkg --exclude-suspended
```

Uses `genanki` Python library (well-maintained, MIT license):
- Maps explain-to-colleague cards to "Basic (and reversed)" note type
- Maps quick-check cards to cloze or multiple-choice note type
- Tags from our cards → Anki tags
- Provenance metadata in a "Source" field (lesson reference)

## Open questions

- Include review history/scheduling in export, or just content? (Anki will reschedule anyway)
- How to map our "explain to a colleague" format to Anki? (Front: prompt, Back: expected answer + explanation)
- Should quick-check multiple-choice export as Anki's native cloze or a custom note type?

## Acceptance criteria

- [ ] `sr-export.py` produces valid `.apkg` file via genanki
- [ ] Cards preserve: prompt, expected answer, tags, source lesson
- [ ] Exported deck importable into Anki desktop and AnkiDroid
- [ ] Suspended/mastered cards optionally excluded
- [ ] Provenance preserved in a "Source" field on each note
