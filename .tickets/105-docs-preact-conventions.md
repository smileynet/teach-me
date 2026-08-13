---
id: "105"
title: "Update teach skill + AGENTS.md for Preact conventions"
type: docs
status: done
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

- [x] Agent can generate a new Preact page without checking research files
- [x] Conventions documented: file naming, import patterns, signal usage, testing
- [x] Commands table in AGENTS.md updated
- [x] Glossary terms added to CONTEXT.md

## Context & Sources

- **Research:** `.scratch/research/preact-no-build-patterns.md` — project structure, dev workflow
- **Research:** `.scratch/research/preact-component-library-cdn.md` — individual files, signal stores
- **Research:** `.scratch/research/testing-preact-no-build.md` — Playwright e2e strategy
- **Research:** `.scratch/research/asset-management-no-bundler.md` — vendoring, cache busting
- **Components catalog:** `assets/components/` — all components live here
- **Existing conventions:** AGENTS.md, `.kiro/skills/teach/SKILL.md`
