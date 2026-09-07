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

## Problem

The generated map page's `#page-data` JSON emits `leadsTo` as **one object per character** of the
target slug string instead of one object per target domain. Observed in
`library/gltf-format/lessons/gltf-format-map.html` (2026-09-06, during the #312 lesson work):

```json
"leadsTo": [{"slug": "[", "why": ""}, {"slug": "g", "why": ""}, {"slug": "o", "why": ""},
            {"slug": "d", "why": ""}, ...]   // spells out "[godot-asset-pipeline, godot-3d-animation]"
```

Expected:

```json
"leadsTo": [{"slug": "godot-asset-pipeline", "why": ""}, {"slug": "godot-3d-animation", "why": ""}]
```

The graph `edges` array is correct — only the cosmetic `leadsTo` list is mangled — so it doesn't break
navigation, but any UI that renders "leads to" text from `leadsTo` shows garbage. Looks like a
`leads_to` value is being iterated as a string (per-char) rather than parsed as a list of slugs.

## Where

`tools/generate_map_page.py` (the `leads_to` / `leadsTo` serialization) and/or `map_parser.py`'s
parse of the MAP.md `leads_to:` line (a bracketed list of slugs). Reproduce: regenerate any map whose
MAP.md has a `leads_to:` with 1+ targets and inspect the `#page-data` `leadsTo`.

## What to build

- Parse the MAP `leads_to:` value as a list of domain slugs (split on the list delimiter), not a string.
- Emit `leadsTo` as one `{slug, why}` per target.

## Acceptance criteria

- [ ] `generate_map_page.py` emits `leadsTo` as a list of `{slug, why}` objects, one per target domain
- [ ] The gltf-format map page-data `leadsTo` shows `[{slug: "godot-asset-pipeline"}, {slug: "godot-3d-animation"}]`, not per-character objects
- [ ] Regenerate affected committed map pages; `check-index-drift` / `mise run verify` pass
- [ ] Add a `map_parser` test for a multi-target `leads_to` (it's a library with consumers → warrants a test)

## Notes

- Discovered during #312 (consuming-glTF-engine-import) map regeneration; present in both the pre- and
  post-regen committed page, so it predates that work — not introduced by it.
