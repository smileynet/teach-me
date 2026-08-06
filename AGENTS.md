# AGENTS.md — teach-me

Test bed for learning-oriented agent skills. Refined here, then ported to crew-research for global deployment.

## Workspace Layout

```
.kiro/skills/     — kiro-cli skills (teach, quiz-me, wait-what)
.memory/          — persistent project knowledge (glossary, ADRs)
.memory/adr/      — architecture decision records
.scratch/         — ephemeral working notes (gitignored)
.references/      — reference repos for study (gitignored)
tools/            — project scripts and automation
```

## Skills

| Skill | Trigger | What it does |
|-------|---------|-------------|
| teach | `/teach`, "teach me", "next lesson" | Multi-session learning with stateful workspace |
| quiz-me | `/quiz-me`, "test me" | Retention testing via interview |
| wait-what | `/wait-what`, "I don't understand" | Re-explain when comprehension fails |

## Commands

| Task | Command | Expected |
|------|---------|----------|
| Start learning | `/teach <topic>` | Mission interview or next lesson |
| Test retention | `/quiz-me` | Knowledge verification round |
| Re-explain | `/wait-what` | Simpler re-pitch of last message |
| Render diagrams | `mise run render-diagrams` | .mmd/.d2 files → SVG in assets/generated/ |
| Open latest lesson | `mise run open-lesson` | Opens in browser |
| Install deps | `mise run install-deps` | drawsvg + playwright chromium |
| Browse/validate URL | Switch to `browser` agent | Specialist with Playwright MCP |

## Workflow

| Situation | Action |
|-----------|--------|
| New domain term resolved | Add to `.memory/CONTEXT.md` immediately |
| Significant technical decision | Write ADR in `.memory/adr/NNNN-slug.md` |
| Ephemeral notes / scratch work | Write to `.scratch/`, promote or delete later |
| Reference repo to study | Clone into `.references/`, use `study-reference` skill |
| Plan needs stress-testing | Use `/grill-with-docs` |
| Work on visual tooling | Check `.tickets/` for frontier (status: open, blocked_by all done) |

## Constraints

| Don't | Do instead |
|-------|-----------|
| Don't accumulate scratch files | Promote to `.memory/` or delete after use |
| Don't put implementation details in CONTEXT.md | Use ADRs for decisions with rationale |
| Don't commit .scratch/ or .references/ | Both are gitignored |
| Don't load Playwright MCP in default agent | Dispatch to `browser` specialist (40+ tools degrades selection) |
| Don't assume subagent tool trust inherits | Each specialist agent needs its own `allowedTools` or it stalls silently |

## Skill Format (kiro-cli)

Skills live in `.kiro/skills/<name>/SKILL.md`. Frontmatter:
```yaml
name: skill-name
description: "What it does. Trigger: trigger phrases."
metadata:
  type: process|protocol|reference
  invocation: user-only|both
  practice: null
```
Skills are auto-loaded via `skill://.kiro/skills/**/SKILL.md`. Reference files go alongside SKILL.md (relative paths work).

## When Blocked

1. Check `.memory/` for prior decisions and context
2. Check `.references/` for patterns in reference repos
3. If domain term is ambiguous — ask, then record in CONTEXT.md
4. If architecture choice needed — write ADR with options, propose to user
