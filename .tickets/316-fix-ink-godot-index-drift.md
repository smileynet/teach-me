---
id: "316"
title: "Fix ink-godot index drift (stale mission vs generator; MISSION.md missing)"
status: open
blocked_by: []
priority: medium
validation_criteria:
  - "check-index-drift.py reports library/ink-godot/lessons/index.html as [ok] (no drift)"
  - "Root cause resolved: either restore ink-godot/MISSION.md so the generator re-emits the real mission, or accept the generic mission + regenerate; decided + documented"
  - "mise run verify passes the index-drift gate without --no-verify"
tags: ["platform"]
---

# Fix ink-godot index drift (stale mission vs generator; MISSION.md missing)

## Problem

`tools/check-index-drift.py` reports **`library/ink-godot/lessons/index.html` as `[DRIFT]`** — the
committed page differs from `generate_index_page.py`'s current output. This has been forcing
`git commit --no-verify` across the gltf-format lesson work (2026-09-05/06 session, ~8 commits) and
fails the `mise run verify` index-drift gate.

## Root cause (diagnosed 2026-09-06)

The drift is in the embedded `#page-data` JSON `mission` block:
- **Committed page** carries a rich mission: `"Mission: Blender → Godot Shader Pipeline (Esoteric
  Ebb Style)"` with 4 shader-pipeline criteria.
- **Generator now emits** the generic `{"title": "Learning Workspace", "why": null, "criteria": []}`.

Because **`library/ink-godot/MISSION.md` does not exist** (confirmed: `No such file or directory`),
the generator has no mission source to read, so it falls back to the generic placeholder — while the
committed artifact still has an older, hand-embedded mission. (The committed mission is also *wrong*
for ink-godot — it's a Blender/shader mission, not a narrative-scripting one — so it looks like a
copy/paste from another domain's page at some earlier point.)

Everything else in the page-data (domains, topicIds, demoOverlay, stats) matches — the diff is
4 lines, mission-only.

## Resolution options (decide, don't blind-regen)

1. **Author a correct `ink-godot/MISSION.md`** (narrative-scripting mission), then regenerate → the
   page gets a real, correct mission and drift clears. **Preferred** — restores lost content with the
   right mission.
2. Accept the generic mission: regenerate + commit (drift clears, but the page loses a mission block).
   Weaker — throws away the (wrong-but-present) mission rather than fixing it.

A blind regen (option 2 by default) would *silently drop* the mission — so this needs a decision +
a written MISSION.md, not just a regenerate-and-commit.

## Acceptance criteria

- [ ] `library/ink-godot/MISSION.md` authored (correct narrative-scripting mission) OR a documented decision to drop it
- [ ] `library/ink-godot/lessons/index.html` regenerated from the generator (not hand-edited)
- [ ] `tools/check-index-drift.py` reports it `[ok]`
- [ ] `mise run verify` passes the index-drift gate without `--no-verify`
- [ ] Check whether other library domains have the same missing-MISSION.md drift (sweep `check-index-drift.py`)

## Notes

- Discovered during the gltf-format lesson work; the recurring `--no-verify` reason across that
  session's commits. Not owned by #198/#272/#276/#278/#279 (those are multi-workspace/overlay/unify
  concerns, not this mission-source drift).
- `check-index-drift.py` is non-destructive (snapshots + restores), so it's safe to run repeatedly.
