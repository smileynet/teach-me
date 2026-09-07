---
id: "320"
title: "Fix MAP leads_to rendered char-by-char in map page-data (leadsTo array of single chars)"
status: done
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

- [x] `generate_map_page.py` emits `leadsTo` as a list of `{slug, why}` objects, one per target domain
- [x] The gltf-format map page-data `leadsTo` shows `[{slug: "godot-asset-pipeline"}, {slug: "godot-3d-animation"}]`, not per-character objects
- [x] Regenerate affected committed map pages; `check-index-drift` / `mise run verify` pass
- [x] Add a `map_parser` test for a multi-target `leads_to` (it's a library with consumers → warrants a test)

## Notes

- Discovered during #312 (consuming-glTF-engine-import) map regeneration; present in both the pre- and
  post-regen committed page, so it predates that work — not introduced by it.

## Resolution

Root cause: `_parse_yaml_value` in `tools/map_parser.py` had no bracketed-list branch, so the inline
frontmatter `leads_to: [godot-asset-pipeline, godot-3d-animation]` was returned as a raw string;
`load_map`'s `for item in raw_leads` then iterated that string character-by-character, producing the
per-character `leadsTo` objects in the page-data. (A "parse, don't validate at the boundary" failure —
the loose `str|int|list|None` return let a downstream site re-interpret the value.)

Fix: added an inline flow-sequence branch to `_parse_yaml_value` (parse `[a,b]` → `list[str]` at the
single parse boundary, with an empty-`[]` guard). `list[str]` was already in the function's return union,
so no caller sees a new shape and no downstream guards changed.

Scope held by 3 research/review passes (root-cause trace, blast-radius, data-modeling): gltf-format is the
only MAP using the inline form → only its map page regenerated; the other 9 maps use block-style and were
already correct. `Edge.type: str` deliberately NOT tightened (closed parser-set vocabulary, already
`validate()`-checked — fails the "when NOT to model harder" gate; reflexive over-modeling avoided).

**Verified:**
- `tools/test_map_parser.py` → 22/22 pass, incl. 2 new regression tests (`test_leads_to_inline_list_not_char_split`, `test_leads_to_empty_inline_list`).
- Regenerated `gltf-format-map.html`: `leadsTo` = `[{slug:"godot-asset-pipeline"}, {slug:"godot-3d-animation"}]`.
- Repo sweep for single-char slugs across all map pages + `library/index.html` → none.
- `mise run verify` green, committed through the pre-commit hook (no `--no-verify`).

Committed dc13c40. Research/review: `.scratch/{research/320-yaml-flowlist,research/320-parse-boundary,review/320-parser-blast-radius,review/320-test-and-maps,review/320-parser-return-types}.md`.
