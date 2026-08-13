---
id: "105"
title: "Update teach skill + AGENTS.md for Preact conventions"
type: docs
status: open
priority: medium
blocked_by: ["095", "096"]
work_order: 9
---

# Update teach skill + AGENTS.md for Preact conventions

## What to build

Document the Preact conventions so the agent (and future developers) know how to:
- Add a new component
- Generate a new page type from Python
- Use the data island pattern
- Wire SSE into a component
- Test a Preact page

## Deliverables

- `.kiro/skills/teach/SKILL.md` — update "Before Publishing" checklist for Preact pages
- `AGENTS.md` — add Preact commands (vendor update, component scaffold) and conventions
- `.memory/CONTEXT.md` — add terms: data island, import map, signal, HTM, dagre
- `assets/components/README.md` — component catalog + patterns

## Acceptance Criteria

- [ ] Agent can generate a new Preact page without checking research files
- [ ] Conventions documented: file naming, import patterns, signal usage, testing
- [ ] Commands table in AGENTS.md updated
- [ ] Glossary terms added to CONTEXT.md
