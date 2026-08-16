---
id: "140"
title: "Feature: provenance-tracked questions — source quote → objective → question chain"
status: open
blocked_by: ["139"]
---

# Feature: provenance-tracked questions

## What to build

Extend the JSONL question format with provenance fields that trace each question back to its source material:

```jsonl
{
  "type": "open",
  "topic": "schema-evolution",
  "prompt": "Why can Iceberg add columns without rewriting data files?",
  "criteria": "Should mention: (1) ...",
  "source_section": "§4.2 Schema Evolution",
  "source_page": 14,
  "source_quote": "Old data files keep their original schema; new files use the new spec. The engine handles translation at query time.",
  "objective": "Explain how schema evolution works without data rewrites",
  "blooms_level": "understand"
}
```

The "Could They Answer This?" gate: every question must trace to a passage that teaches the answer. If you can't cite the source, you're testing something the material doesn't cover.

## Acceptance criteria

- [ ] JSONL format extended with source_section, source_page, source_quote fields
- [ ] Generate-topic skill produces provenance fields when working from a source doc
- [ ] sr:check validates provenance fields exist on source-derived questions
- [ ] Quiz answer reveal can show "From: §4.2 Schema Evolution, p.14" attribution
- [ ] Backcompat: questions without provenance still work (fields optional)
