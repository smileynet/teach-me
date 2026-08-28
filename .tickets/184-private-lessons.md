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

## Acceptance criteria

- [ ] User can generate a lesson marked as "private"
- [ ] Private lessons are gitignored
- [ ] Private lessons appear in the local map/index view
- [ ] Private lessons are visually distinguished from shared lessons
- [ ] MAP.md files do not contain references to private lessons
- [ ] Private lessons can reference shared prerequisites
- [ ] Shared lessons never depend on private lessons
- [ ] Optional: promote a private lesson to shared (move + commit)
