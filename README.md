# teach-me

An AI teaching system that researches topics, writes interactive lessons, and helps you build lasting understanding through quizzes and spaced repetition.

## For Learners

Open this project in an AI coding assistant (Kiro CLI, Claude Code, Codex, Cursor, or any [Agent Skills-compatible](https://agentskills.io) client) and say what you want to learn. The agent will:

1. Ask about your goals and context
2. Research the domain from verified sources
3. Generate interactive HTML lessons with diagrams
4. Create quizzes that test understanding (not recall)
5. Track retention with spaced repetition

**Quick start:**
```bash
mise install && mise run setup
```
Then tell the agent: *"I want to learn about [topic]"*

**Browse examples:** Open `lessons/index.html` in a browser, or run `mise run open-lesson`.

---

## For Developers / Maintainers

This is a test bed for learning-oriented AI agent skills. The teaching system above is the product; the skills and tools below are the machinery.

### Architecture

```bash
mise install        # set up Python, Node, uv
mise run setup      # install dependencies
mise run verify     # check everything works
mise run open-lesson  # view the latest lesson
```

## Example Topics

| Topic | Domain | Tests |
|-------|--------|-------|
| [Iceberg on AWS](examples/iceberg-workspace/) | Cloud data engineering | Retrofitted legacy — proves pipeline upgradability |
| [OIDC in Rust](examples/oidc-rust/) | Security / protocols | Full pipeline output — protocol flows + implementation |
| [Workout Fundamentals](examples/workout-fundamentals/) | Fitness / exercise science | Boundary: physical skills vs knowledge |
| [Godot Game Dev](examples/godot-gamedev/) | Game development | Engine-specific — node architecture + scripting |

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
| `generate-topic` | Full pipeline: research → lesson → post-process → verify |
| `quiz-me` | Socratic dialog — learner explains, agent probes |
| `wait-what` | Re-explain when comprehension fails |
| `jargon` | Annotate domain terms with tooltips |
| `draw-diagram` | Generate inline SVG teaching diagrams |
| `visual-qa` | Exercise components, capture screenshots |
| `theme` | Preview and apply color palettes |
