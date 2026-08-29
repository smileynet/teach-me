---
id: "256"
title: "Unify the three MAP.md parsers to one map_parser.load_map"
status: in_progress
blocked_by: []
priority: high
tags: ["platform"]
---

# Unify the three MAP.md parsers to one `map_parser.load_map`

## Why (risk reducer — do this FIRST)

Code review (2026-08-29) found **three independent parsers** of the same committed
MAP.md format:

1. `tools/map_parser.py` `load_map` — the canonical dataclass model.
2. `tools/generate_map_page.py` `parse_map_md` (~L73-146) — a DUPLICATE regex parser
   (reads `status`:138, `prereqs`:143, `slug`:133).
3. `tools/generate_index_page.py` `parse_map_meta` (~L64-99) — a regex SCRAPE (counts
   `**status:**` at L85-88 for the progress ring).

Any schema change (the upcoming ULID IDs + typed edges + status removal) must touch all
three or they silently drift and corrupt the map/index pages. Collapsing to one parser
is the prerequisite that makes #257/#258 a single-site change instead of a triple-edit.
Independent of the #183 rename — this is schema-plumbing, not paths.

## What to build

- Make `map_parser.load_map` the single source of truth for parsing a MAP.md into the
  `DomainMap`/`Topic` model.
- Replace `generate_map_page.py::parse_map_md` with a call to `map_parser.load_map`
  (consume the dataclasses instead of re-parsing). Preserve the map page's current
  output.
- Replace `generate_index_page.py::parse_map_meta`'s status-count scrape with counts
  derived from `load_map`'s model (still reads committed `status` for now — #258 moves
  that to the overlay; this ticket only de-duplicates parsing).
- If `load_map` lacks a field the shadow parsers exposed, add it to the model rather
  than re-parsing.

## Out of scope

- ULID IDs, typed edges (#257); removing `status` (#258). This ticket ONLY collapses the
  parsers behind the CURRENT schema — a pure refactor with identical output.

## Acceptance criteria

- [ ] `generate_map_page.py` and `generate_index_page.py` parse MAP.md ONLY via
      `map_parser.load_map` (no independent regex parsing of topic blocks/status)
- [ ] Generated map pages and index page are byte-identical (or diff-explained) before
      vs after for all committed maps
- [ ] `mise run verify` EXIT 0 (map/index generation + tests)
- [ ] `grep` shows no second `### ` / `**status:**` / `**prereqs:**` topic-block regex
      parser outside `map_parser.py`

## Validation

Regenerate all maps + index (`maps:regenerate` per-workspace + `index:generate`) and
diff against committed output; `mise run verify` green; grep confirms single parser.
