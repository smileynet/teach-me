> Recorded at eebded8, before adoption: paths cite the old `.memory/` layout.

# teach-me: staged glossary terms (STAGED, unconfirmed)

Inferred from code during adoption (2026-10-22). Not written to GLOSSARY.md. Confirm, correct,
or reject each one.

**Library** (STAGED):
The committed, public topic library under `library/` (one workspace per domain), served by default
on a fresh clone and deployed to GitHub Pages.
_Avoid_: "examples" (the pre-#183 name), conflating with the learner's private `workspace/`
Evidence: ADR 0012:1; AGENTS.md:22; README.md:34; `.kiro/agents/godot_editor.json:23` still says `examples/`.

**Learner profile** (STAGED):
The private `{workspace}/.user/learner-profile.md` holding the mission, pace, preferences, and
working notes; the teach skill's first-contact detection reads it.
_Avoid_: NOTES.md, root MISSION.md (legacy, pre-#361)
Evidence: teach SKILL.md:19,55,62; tools/init_workspace.py:120,205; contrast CLAUDE.md:11,15 and AGENTS.md:83 (NOTES.md).

**Topic / Domain / Track** (STAGED):
A *domain* is one library workspace and its map (`lessons/{domain-slug}/`); a *topic* is one map
node that `generate-topic` turns into a lesson + reference + quiz + SR set; a *track* is a
sequence of lessons with a shared reference project.
_Avoid_: using "topic" for a whole domain (e.g. "Topics generate sequentially", CLAUDE.md:44)
Evidence: AGENTS.md:25,81; generate-topic SKILL.md description, :140; tools/check-topic-completeness.py.

**Reference project** (STAGED):
The runnable companion project a lesson track builds artifacts into (`test-scene/`,
`ink-test-project/`), validated by its toolchain before lessons close.
_Avoid_: reference doc (lesson companion), `reference/code/` (per-lesson downloads), `.references/` (cloned prior art)
Evidence: ADR 0010:1; AGENTS.md:81; generate-topic SKILL.md:140.

**Oracle** (STAGED):
A stdlib property-assertion check that validates the claim a lesson teaches (the math or measured
contract), as distinct from a syntax linter; Tier-1 (Blender-free) in a Tier-1/2/3 ladder.
_Avoid_: linter, test (when meaning a property oracle)
Evidence: `.kiro/steering/code-validation-teaching.md:42`; tools/*-oracle.py in `mise run verify`; tools/gltf-format-oracle.py:4.
