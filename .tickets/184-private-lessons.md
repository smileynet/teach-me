---
id: "184"
title: "Optional private lessons (uncommitted, linked to shared map)"
status: open
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

## Implementation plan

- **A. `find_maps` private overlay** — new `find_private_maps(scan_dirs)` returns
  `.user/maps/*.MAP.md`; `build_domain_graph` merges private topics into the owning domain
  record (marks them `private: true`, adds `private_topic_ids`). Wholly-private domain → its
  own record flagged private.
- **B. Never committed** — `.gitignore` already has `**/.user/*`; private maps + lessons land
  there. Add `.user/maps/` + `.user/lessons/` to the private-lesson generation path. Verify no
  `git add -f` needed and MAP.md-under-library stays clean.
- **C. Index/map integration** — `build_page_data` carries `private` through to each
  domain/topic; `UnifiedView`/`IndexView` render the badge. Private counts fold into the local
  view only (never into committed demo-status).
- **D. No MAP.md pollution** — committed `{domain}.MAP.md` files never gain private topic
  entries (they live only in `.user/maps/`). Regen of a committed page must not bake private
  content (private is a serve/local-render overlay, like the user status overlay).
- **E. Forest-prereq guard** — extend `check-maps-forest.py` to reject shared→private prereqs.

## Acceptance criteria

- [ ] User can generate a lesson marked as "private"
- [ ] Private lessons are gitignored
- [ ] Private lessons appear in the local map/index view
- [ ] Private lessons are visually distinguished from shared lessons
- [ ] MAP.md files do not contain references to private lessons
- [ ] Private lessons can reference shared prerequisites
- [ ] Shared lessons never depend on private lessons
- [ ] Optional: promote a private lesson to shared (move + commit)
