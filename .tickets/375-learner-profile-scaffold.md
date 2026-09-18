---
id: "375"
title: "init_workspace must scaffold .user/learner-profile.md that the teach skill reads"
status: in_progress
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

- [ ] `python tools/init_workspace.py` creates `.user/learner-profile.md` with a mission placeholder
- [ ] The teach skill's session-start detection passes on a freshly scaffolded workspace (no false first-contact)
- [ ] A workspace with mission content only in `MISSION.md` gets it recognized/migrated into `.user/learner-profile.md` (idempotent; original file left intact for audit)
- [ ] Fixture test covers scaffold + legacy-migration paths (extend `tools/test_skill_local_state.py` or the initializer's tests)

## References

- Commit `3c3b555` (#361 resolution names "the teaching workspace initializer is the first-use
  path" — this ticket closes that gap); `tools/init_workspace.py`; `.kiro/skills/teach/SKILL.md`
