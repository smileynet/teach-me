---
id: "320"
title: "Fix MAP leads_to rendered char-by-char in map page-data (leadsTo array of single chars)"
status: open
blocked_by: []
validation_criteria:
  - "generate_map_page.py emits leads_to as a list of {slug,why} objects (one per target domain), not one object per character"
  - "the gltf-format map page-data leadsTo shows [{slug: 'godot-asset-pipeline'}], not [{slug:'['},{slug:'g'}...]; check-map / verify still pass"
tags: ["platform"]
---

# Fix MAP leads_to rendered char-by-char in map page-data (leadsTo array of single chars)

## What to build

TBD

## Acceptance criteria

- [ ] TBD
