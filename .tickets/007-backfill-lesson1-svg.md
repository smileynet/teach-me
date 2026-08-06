---
id: "007"
title: "Backfill lesson 1 with inline SVG diagram"
status: open
priority: high
blocked_by: []
---

# Backfill lesson 1 with inline SVG diagram

## What to build

Update `lessons/0001-iceberg-metadata-tree.html` to replace the ASCII art architecture diagram with a proper inline SVG using the visual teaching patterns.

## Specifically

The current lesson has a `<pre><code>` block showing the metadata tree:
```
Glue Data Catalog → metadata/ (JSON, Avro) → data/ (Parquet)
```

Replace with an inline SVG layered-stack diagram showing:
1. AWS Glue Data Catalog (top, blue)
2. Metadata files in S3 (middle, amber — JSON + Avro)
3. Data files in S3 (bottom, green — Parquet)

With arrows between layers and brief annotations on each arrow ("points to current metadata", "lists data files with stats").

## Guidelines

- Follow `assets/svg-patterns.md` layered stack pattern
- Use color vocabulary from `.kiro/steering/visual-teaching.md`
- Add one-line verbal summary above the diagram
- Keep to 5-7 elements total

## Acceptance criteria

- [ ] ASCII diagram replaced with inline SVG
- [ ] Colors follow the steering vocabulary
- [ ] Verbal summary above the diagram
- [ ] Lesson still renders correctly in browser
