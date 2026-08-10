# ADR 0002: Research-First Teaching + Agent-Complete Page Templates

## Status

Accepted (2026-08-09)

## Context

Two problems surfaced during this session:

1. **Teaching from parametric memory produces errors.** The original Iceberg lesson had 8 factual issues (wrong layer count, missing delete files, dead library recommendations). The roguelike example had its entire premise overturned (ECS is NOT the consensus for roguelikes; bracket-lib is dead). These only surfaced when we researched the domain properly.

2. **Generated pages drift in styling.** The quick-check review page used hardcoded hex colors while lessons used CSS variables. Without a template contract, every new page type reinvents its styling.

## Decision

### Research-First Teaching

Every lesson requires a research phase BEFORE writing:
1. Identify 3-6 subtopics an expert would consider
2. Dispatch research per subtopic (2+ sources, practitioner perspectives, warnings)
3. Populate RESOURCES.md with verified sources
4. Write the lesson grounded in findings — every claim traces to research

This is a hard gate in the teach skill, not a suggestion.

### Agent-Complete Pages + Shared Asset Contract

The agent generates complete, standalone HTML documents. Consistency comes from a **shared asset contract**, not a build system:

- **One shared `style.css`** with CSS custom properties — the single source of visual truth
- **Documented page scaffolds** (in `assets/scaffolds/`) that the agent copies and fills
- **Custom Elements** for interactive behavior (glossary, quiz, reveal, theme-toggle)
- **No build step, no bundler, no SSG** — pages work from `file://` and simple HTTP servers
- **Regeneration over synchronization** — when structure changes, regenerate affected pages (cheap for 10-30 files)

## Alternatives Considered

| Alternative | Why rejected |
|-------------|-------------|
| Static site generator (Eleventy, Hugo) | Adds build step, template language, and tooling the agent doesn't need — the agent IS the template engine |
| Web Components for everything | Over-engineering for static content; Custom Elements only worthwhile for genuinely interactive widgets |
| Client-side includes (fetch + inject) | Adds JS dependency for basic page structure; breaks `file://`; slower initial render |
| Markdown source → HTML build | Loses control over precise HTML structure; agent already outputs HTML natively |

## Consequences

- Agent must read scaffold files before generating a new page type
- New page types (review, reference, lesson) each get a scaffold in `assets/scaffolds/`
- All styling uses CSS variables — hardcoded hex is a linting violation
- The "look around corners" test applies to every lesson: "Would a domain expert approve this?"
- Research findings live in `.scratch/research/` (ephemeral) but RESOURCES.md persists the verified sources
