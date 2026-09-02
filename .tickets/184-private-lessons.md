---
id: "184"
title: "Optional private lessons (uncommitted, linked to shared map)"
status: done
blocked_by: ["183"]
priority: high
tags: [platform]
---

# Optional private lessons (uncommitted, linked to shared map)

## Context

With #183, lessons default to shared/committed. But sometimes a user wants to generate a lesson just for themselves — personal exploration, work-specific context, or topics they don't want to contribute. These private lessons should still integrate with the map and navigation but never get committed.

**Decided by ADR 0012 (accepted 2026-08-28):** this ticket implements the
private-overlay half of the two-tier model. The private path is **`.user/`**
(gitignored), generalized to topic granularity (a whole topic can be private, not
just individual lessons). Public library content lives under `library/` (#183);
private content overlays it locally at render time.

## What to build

1. **Private lesson flag** — when generating a lesson, the user can mark it as private. Private lessons are written to a gitignored location (e.g., `.user/lessons/{domain}/`).

2. **Map integration** — private lessons appear on the user's local map view (distinguished visually — maybe a different badge or subtle indicator). They link from the same topic nodes but only exist locally.

3. **Navigation** — private lessons show up in the index and map for the local user but don't pollute the shared tree. If a user opens the map without the private lessons present, those nodes show as "available to generate" or are hidden.

4. **No shared map pollution** — the MAP.md files in the repo don't reference private lessons. The map page overlays private content at render time from local config.

## Design questions
- How does the map page discover private lessons? Scan `.user/lessons/` at serve time? A manifest in local config?
- Should private lessons be promotable to shared (move from `.user/` to committed tree)?
- What visual distinction on the map — different color, icon, border?
- Can a private lesson depend on a shared lesson's prerequisites (yes, obviously) — can a shared lesson depend on a private one (no)?

## Design resolution (2026-09-02) — answered against current architecture

Grounded in the shipped overlay infra (`tools/lib/overlay.py`, #279), the domain-graph
derivation (`tools/lib/domain_graph.py`: `find_maps` + `build_domain_graph`), and the
unified index generator (`tools/generate_index_page.py`).

1. **Discovery — private MAP overlay under `.user/maps/`, scanned at generate/serve time.**
   Mirror `find_maps`: alongside the committed `{domain}.MAP.md`, look for
   `.user/maps/{domain}.MAP.md` (private topics) and merge topics into the same domain
   record. Rationale: reuses the MAP.md topic model (ULID ids, prereqs) the whole graph
   already speaks; no new manifest format. A wholly-private domain = a `.user/maps/*.MAP.md`
   with no committed sibling. Private lesson HTML lives at `.user/lessons/{domain}/`.
2. **Promotable — yes, optional AC.** `git mv .user/maps/{d}.MAP.md → {d}.MAP.md` +
   `.user/lessons/{d}/* → library/{d}/lessons/` then commit. Ship as a `--promote` flag on a
   small tool; keep it OUT of the core path (optional AC).
3. **Visual distinction — a `private` flag on the topic/domain record + a badge.** Reuse the
   existing `dc-sub-badge` / `is-child` CSS patterns in `generate_index_page._CSS_EXTRA`; add a
   `.dc-private-badge` ("private" pill) and mark private nodes. Color is NOT the only signal
   (WCAG — visual-teaching.md): text badge + border.
4. **Prereq direction — private→shared allowed, shared→private forbidden.** Enforce at
   generation: a private topic MAY list a committed topic id as a prereq; a committed MAP.md
   MUST NOT reference a `.user/` topic id. Add a check (extend `check-maps-forest.py`): fail if
   any committed map's prereq/leads_to resolves only within `.user/`.

## Data model — visibility (locked 2026-09-02, data-modeling lens)

Single source of truth: a topic's visibility is its **discovery provenance**, not a stored
flag. Do NOT add `private: bool` to `Topic`/`DomainMap` (`map_parser.py`) — those parse
committed MAP.md content and must stay visibility-agnostic; a committed MAP.md is
unconditionally shared, so a flag beside a `.user/`-sourced path would be a second source
that can drift.

Tag visibility ONCE, at the domain-graph record level, from where the map was discovered
(`find_maps` = shared, `find_private_maps` = private). Model it as a small carried-data
variant, not a bare bool — it gates THREE behaviors (badge render, prereq-direction rule,
never-bake-into-committed-page), so it clears the "don't over-model a lone binary" bar:

    source = Shared(committed_path) | Private(overlay_path, promote_target)

Discovery is the single parse point that assigns it (parse-at-boundary); nothing downstream
re-derives or re-checks. Aligns with `serve.py::_block_private_overlay` (serve already treats
`.user/` as never-leak).

## Implementation plan

- **A. `find_private_maps` + graph merge** — new `find_private_maps(scan_dirs)` returns
  `.user/maps/*.MAP.md`; `build_domain_graph` tags each record's `source` variant and merges
  private topics into the owning domain record, adding `private_topic_ids`. Wholly-private
  domain → its own record with a `Private` source.
- **B. Never committed** — `.gitignore` already has `**/.user/*`; private maps + lessons land
  there. Add `.user/maps/` + `.user/lessons/` to the private-lesson generation path. Verify no
  `git add -f` needed and MAP.md-under-library stays clean.
- **C. Index/map integration** — `build_page_data` carries the visibility variant through to
  each domain/topic; `UnifiedView`/`IndexView` render the badge. Private counts fold into the
  local view only (never into committed demo-status).
- **D. No MAP.md pollution** — committed `{domain}.MAP.md` files never gain private topic
  entries (they live only in `.user/maps/`). Regen of a committed page must not bake private
  content (private is a serve/local-render overlay, like the user status overlay).
- **E. Forest-prereq guard** — extend `check-maps-forest.py` to reject shared→private prereqs.

## Acceptance criteria

- [x] User can generate a lesson marked as "private"
- [x] Private lessons are gitignored
- [x] Private lessons appear in the local map/index view
- [x] Private lessons are visually distinguished from shared lessons
- [x] MAP.md files do not contain references to private lessons
- [x] Private lessons can reference shared prerequisites
- [x] Shared lessons never depend on private lessons
- [x] Optional: promote a private lesson to shared (move + commit)

## Resolution (2026-09-02)

Implemented steps A–E on the locked visibility model (provenance, not a stored flag).

- **A. Discovery + merge** (`tools/lib/domain_graph.py`): added the `Shared | Private`
  carried-data variant, `find_private_maps()` (scans `.user/maps/*.MAP.md`), and made
  `build_domain_graph(paths, private_paths)` tag each record's `source`, merge a private
  overlay into its committed domain (`private_topic_ids` + `has_private`), or create a
  wholly-`Private` domain record. `find_maps` now excludes `.user/`.
- **B. Never committed**: `.gitignore`'s `**/.user/*` already covers `.user/maps/` +
  `.user/lessons/` (verified via `git check-ignore`). Generating a private lesson writes
  there; no `git add -f`, so it can't be committed accidentally. (Lesson generation itself
  is skill-driven, per AGENTS.md "don't script creative work".)
- **C. Index/map integration** (`generate_index_page.py` + components): `build_page_data`
  carries `private`/`hasPrivate`/`privateTopicIds`; `IndentedTreeView`, `DomainCard`,
  `IteratedMapView` render a `.dc-private-badge` ("private" pill, amber, text-labeled — not
  color-alone, WCAG). Private counts fold into the local view only.
- **D. No MAP.md pollution**: private topics live ONLY in `.user/maps/`; committed maps
  never gain them, and `demo_status` is empty for private records so regen never bakes
  private content. Verified: with no overlay, generated pages contain zero private refs.
- **E. Prereq guard** (`check-maps-forest.py`): `_maps_dirs` excludes `.user/`, so the
  committed forest never sees private topics — a committed topic prereq-ing a private one
  fails as an 'undefined prereq' (structurally bans shared→private). private→shared is fine
  (the private overlay resolves against committed topics at merge time).
- **Optional promote**: `tools/promote-private-topic.py` moves `.user/maps` + `.user/lessons`
  for a domain into the committed tree; refuses to overwrite an existing committed map; never
  auto-commits (git-safety). `--dry-run` supported.

**Tests**: `tests/test_private_lessons.py` (13) — visibility variant, discovery isolation,
merge, wholly-private record, shared→private ban, index-generation integration (badge +
count merge + no-overlay-no-pollution), promote (move/refuse-overwrite/dry-run). Full suite
254 passed; `mise run verify` EXIT 0 (regenerated all 6 committed index pages to absorb the
badge CSS; drift guard clean).
