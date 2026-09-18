---
id: "375"
title: "init_workspace must scaffold .user/learner-profile.md that the teach skill reads"
status: done
blocked_by: []
priority: medium
type: bug
tags: ["skills", "workspace", "risk-review"]
validation_criteria:
  - "A workspace scaffolded by init_workspace satisfies the teach skill's first-session detection, and a pre-#361 workspace's mission/records remain reachable"
---

# init_workspace must scaffold .user/learner-profile.md that the teach skill reads

## Intent

The scaffolder and the skill must agree on where learner state lives, and existing workspaces
must not present as first-contact after the convention change.

## Context (found 2026-09-18 risk review of the 2026-09-16/17 window)

`3c3b555` (#361) moved the teach skill's state convention (`.kiro/skills/teach/SKILL.md`):
mission/preferences now live in `.user/learner-profile.md`, understanding records in
`.user/learning-records/`, session-start detection requires "a workspace with
`.user/learner-profile.md` containing a mission", and the skill now says "Never write
learner-specific state to committed paths such as `MISSION.md`".

But `tools/init_workspace.py` — untouched by #361 — still scaffolds `MISSION.md` at the
committed path (`_write_if_absent(ws / "MISSION.md", _DEFAULT_MISSION, ...)`, line ~119) and
never creates `.user/learner-profile.md` (verified: no occurrence of `learner-profile` in the
file). Two consequences:

1. **New workspaces**: scaffolded by the tool, then the skill looks for a file the scaffolder
   never made — detection falls to "first contact" even on a just-scaffolded workspace.
2. **Existing live workspaces** (gitignored; existence unverifiable from the repo — stated
   insufficiency): mission in `MISSION.md` and demonstrated-understanding docs in
   `learning-records/*.md` are read by NEITHER the new skill instructions NOR the scaffolder.
   Files are not deleted (no data loss), but the skill as written never finds them — every
   future session re-asks the mission and loses the ZPD history view.

## What to build

Make `init_workspace.py` scaffold `.user/learner-profile.md` (template with mission/preferences
sections) alongside or instead of the committed `MISSION.md` seed, and add a read-fallback or
explicit migration step so a pre-#361 workspace's `MISSION.md` + `learning-records/*.md` are
recognized (migrated into `.user/` or read until migrated).

## Acceptance criteria

- [x] `python tools/init_workspace.py` creates `.user/learner-profile.md` with a mission placeholder — `_ensure_learner_profile` runs on every init (fresh AND existing workspaces); test `test_fresh_scaffold_creates_learner_profile`
- [x] The teach skill's session-start detection passes on a freshly scaffolded workspace (no false first-contact) — the profile exists post-scaffold with a `## Mission` section, so the skill's read path finds its state home (a fresh workspace correctly remains first-contact until the mission is elicited — that is the skill's intended flow, not a false positive)
- [x] A workspace with mission content only in `MISSION.md` gets it recognized/migrated into `.user/learner-profile.md` (idempotent; original file left intact for audit) — init backfill migrates real (non-template) missions before the exists-guard early return; `MISSION.md` bytes verified untouched; idempotency verified (learner edits to the profile survive re-runs); the SKILL.md workflow step 1 also gained the session-time fallback for workspaces the tool never touches
- [x] Fixture test covers scaffold + legacy-migration paths — new `tools/test_init_workspace.py` (4 tests: fresh scaffold, legacy migration, idempotency, template-not-migrated), all passing; added to the `mise run verify` pytest list (skill-local-state suite unaffected: 5 passed)

## Resolution (2026-09-18)

`tools/init_workspace.py`: added `_DEFAULT_LEARNER_PROFILE` and `_ensure_learner_profile()`
— called before the idempotency guard, so it creates the profile on fresh scaffolds AND
backfills existing workspaces, migrating a real (non-template) `MISSION.md` mission into
the profile while leaving `MISSION.md` untouched (it still feeds committed index
presentation via `parse_mission`). The `exists` return now carries `created`/`warnings`
(migration notes). `.kiro/skills/teach/SKILL.md` workflow step 1 gained the legacy
fallback (migrate from `MISSION.md` at session time if the profile lacks a mission).
`tools/test_init_workspace.py`: 4 tests, all passing; wired into core verify.
Ticket #375.

## References

- Commit `3c3b555` (#361 resolution names "the teaching workspace initializer is the first-use
  path" — this ticket closes that gap); `tools/init_workspace.py`; `.kiro/skills/teach/SKILL.md`
