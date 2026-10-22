# AGENTS.md cut log (adoption 2026-10-22)

<!-- adoption cut log (2026-10-22)
- "## Skills" table (10 rows: trigger + what it does): cut. Canonical home: each `.kiro/skills/<name>/SKILL.md` `description` (triggers verified present for all 10); teach/generate-topic ownership: ADR 0019 + teach SKILL.md:19-20 + generate-topic SKILL.md:37, and the kept Workflow row "User names a topic to learn". `/teach`-style slash forms are harness invocation of the same names.
- "Closing a ticket": dropped "Edit frontmatter `status: done` directly — `tkt close` has a config validation bug that rejects valid tickets. Check all AC boxes in the same commit." Canonical home: the tkt block (`tkt close --check-all`, "Reach done only via tkt close"). Bug not reproduced: `tkt close 089 --dry-run` succeeds on tkt 0.3.1 (migration-finding ticket).
- "ported to crew-research": reworded (crew-research retired; migration-finding ticket).
- "global research-dispatch mandate" -> `research` skill; "global `skill-authoring`" -> `writing-for-agents` (crew-research retirements).
- `.memory/...` paths -> relocated homes (GLOSSARY.md, docs/adr/, docs/agents/).
-->
