---
id: "008"
title: "Feature: backfill lesson 1 with inline SVG"
status: open
priority: medium
blocked_by: ["001"]
type: feature
---

# Feature: backfill lesson 1 with inline SVG

## What to build

Replace the ASCII art in `lessons/0001-iceberg-metadata-tree.html` with a proper inline SVG diagram. Use whatever approach spike 001 validates (drawsvg, raw SVG, or D2-generated).

## Diagram content

Layered stack showing:
1. AWS Glue Data Catalog (blue) — "where is the current version?"
2. Metadata files in S3 (amber) — "schema, partitions, snapshots"
3. Manifest files (amber) — "which files, with column stats"
4. Data files in S3 (green) — "the actual rows (Parquet)"

Arrows between layers with brief annotations.

## Acceptance criteria

- [ ] ASCII diagram replaced with inline SVG
- [ ] Colors follow visual teaching steering
- [ ] One-line verbal summary above diagram
- [ ] Renders correctly in browser
