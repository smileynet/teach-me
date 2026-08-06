# AGENTS.md — teach-me

Agent-assisted learning platform. Skills and tools that help users learn about topics through structured, AI-guided sessions.

## Workspace Layout

```
.memory/          — persistent project knowledge (glossary, ADRs)
.memory/adr/      — architecture decision records
.scratch/         — ephemeral working notes (gitignored)
.references/      — reference repos for study (gitignored)
tools/            — project scripts and automation
```

## Commands

No build tools detected yet. Update this section when a language/framework is chosen.

| Task | Command | Expected |
|------|---------|----------|
| (none yet) | — | — |

## Workflow

| Situation | Action |
|-----------|--------|
| New domain term resolved | Add to `.memory/CONTEXT.md` immediately |
| Significant technical decision | Write ADR in `.memory/adr/NNNN-slug.md` |
| Ephemeral notes / scratch work | Write to `.scratch/`, promote or delete later |
| Reference repo to study | Clone into `.references/`, use `study-reference` skill |
| Plan needs stress-testing | Use `/grill-with-docs` |

## Constraints

| Don't | Do instead |
|-------|-----------|
| Don't accumulate scratch files | Promote to `.memory/` or delete after use |
| Don't put implementation details in CONTEXT.md | Use ADRs for decisions with rationale |
| Don't commit .scratch/ or .references/ | Both are gitignored |

## When Blocked

1. Check `.memory/` for prior decisions and context
2. Check `.references/` for patterns in reference repos
3. If domain term is ambiguous — ask, then record in CONTEXT.md
4. If architecture choice needed — write ADR with options, propose to user
