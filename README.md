# teach-me

A test bed for learning-oriented AI agent skills. The agent teaches topics through stateful lessons, reference docs, spaced repetition, and Socratic dialog — grounded in researched sources, not parametric memory.

## Quick Start

```bash
mise install        # set up Python, Node, uv
mise run setup      # install dependencies
mise run verify     # check everything works
mise run open-lesson  # view the latest lesson
```

## What It Does

You tell the agent what you want to learn and why. It:

1. Researches the domain (dispatches subagents, verifies claims)
2. Writes lessons as self-contained HTML pages with inline diagrams
3. Generates reference docs (scannable lookup companions)
4. Creates spaced repetition questions (criteria-based, not recall)
5. Reviews your understanding via Socratic conversation

## Teaching Workspaces

Each topic lives in its own workspace:

```
MISSION.md          — why you're learning this
RESOURCES.md        — verified sources with trust ratings
lessons/*.html      — self-contained lessons (one concept each)
reference/*.html    — lookup companions to each lesson
learning-records/   — demonstrated understanding + SR question bank
assets/             — shared CSS, JS components, scaffolds
```

## Example Topics

| Topic | Domain | Tests |
|-------|--------|-------|
| [Iceberg on AWS](lessons/0001-iceberg-metadata-tree.html) | Cloud data engineering | Core fixture — diagrams, glossary, SR, all components |
| [Roguelike in Rust](examples/roguelike-rust/) | Game dev + programming | Code-heavy cards, research-first correction |
| [Workout Fundamentals](examples/workout-fundamentals/) | Fitness / exercise science | Boundary: what SR can/can't cover for physical skills |

## Key Commands

```bash
mise run sr              # what's due for review
mise run sr:review       # review due cards (or: mise run sr:review -- topic-slug)
mise run sr:quick-check  # generate quick-check review page (MC + diagram cards)
mise run sr:export-anki  # export cards to Anki .apkg
mise run sr:check        # validate question quality
mise run sr:analytics    # knowledge state + what's decaying
mise run map:generate    # generate interactive map pages from MAP.md files
mise run index:generate  # regenerate the All Lessons dashboard
mise run draw -- --type graph --backend graphviz --data '{...}'  # complex diagrams
mise run visual-qa       # exercise all UI components
mise run verify          # smoke test + link verification + source URL check
```

## Design Decisions

- **Research-first** (ADR 0002): Every lesson requires domain research before writing. Prevents teaching from memory.
- **Agent-complete pages** (ADR 0003): No build step. HTML pages with shared CSS variables for theming.
- **Informal posture** (ADR 0001): Knowledgeable colleague at a whiteboard, not course instructor.
- **MAP.md domain scaffolding** (ADR 0004): Big topics decompose into 5-9 subtopic maps with soft prerequisites.

## Skills

| Skill | What it does |
|-------|-------------|
| `teach` | Multi-session learning with stateful workspace |
| `quiz-me` | Socratic dialog — learner explains, agent probes |
| `wait-what` | Re-explain when comprehension fails |
| `jargon` | Annotate domain terms with tooltips |
| `draw-diagram` | Generate inline SVG teaching diagrams |
| `visual-qa` | Exercise components, capture screenshots |
| `theme` | Preview and apply color palettes |
