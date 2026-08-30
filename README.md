# Teach Me

A learning workspace that turns any topic into research-backed lessons, interactive quizzes, and spaced repetition — driven by your AI coding assistant.

- **Lessons from real sources** — never from parametric memory
- **Dependency maps** — shows how subtopics connect
- **Understanding quizzes** — tests "explain why..." not "what is the definition of..."
- **Spaced repetition** — schedules reviews at optimal intervals
- **Anki export** — take cards mobile
- **Dark/light themes** — customizable typography

## Quick Start

```bash
git clone https://github.com/smileynet/teach-me && cd teach-me
mise install && mise run setup
```

Open in [Kiro CLI](https://kiro.dev), [Claude Code](https://claude.ai), [Codex](https://openai.com/codex), or any skills-compatible client:

> "I want to learn about distributed systems"

The agent researches the domain, generates an interactive HTML lesson, and opens it in your browser:

```bash
mise run open-lesson
# → opens lessons/0001-cap-theorem.html
```

## Usage

### Learning a new topic

Tell the agent what you want to learn. It asks about your goals, researches from real sources, then generates lessons one at a time — each with a reference card, a quiz, and SR cards.

### Reviewing what you've learned

```bash
mise run sr              # see what's due
mise run sr:review       # review due cards interactively
mise run sr:analytics    # knowledge retention stats
mise run sr:export-anki  # export to Anki .apkg
```

### Navigating your workspace

Open `workspace/lessons/index.html` in any browser for the full dashboard — lessons, maps, quizzes, and progress tracking.

```bash
mise run serve           # start local server at http://localhost:8787
mise run serve:lan       # serve on LAN for other devices
```

### Teaching from source documents

```bash
python tools/ingest_source.py paper.pdf --workspace workspace --domain "machine-learning" --title "Attention"
# → chunks, classifies, builds a topic map, enriches with prerequisites
```

### Quiz types

- **Open-ended** — explain concepts to a colleague
- **Sequence** — reorder steps correctly
- **Match** — pair terms to definitions
- **Fill-in-the-blank** — complete statements with key terms

## Example Workspaces

| Domain | Topics |
|--------|--------|
| [Data Engineering](library/iceberg-workspace/) | Apache Iceberg metadata, ingestion, change capture |
| [OIDC in Rust](library/oidc-rust/) | Auth flows, PKCE, token validation, JWT anatomy |
| [Fitness](library/workout-fundamentals/) | Progressive overload, recovery science, program design |
| [Game Dev](library/godot-gamedev/) | Godot nodes, GDScript, scene composition |

## Agent Skills

Works with any client that supports [Agent Skills](https://agentskills.io):

| Skill | What it does |
|-------|-------------|
| `/teach` | Multi-session learning with stateful workspace |
| `/quiz-me` | Socratic dialog — you explain, agent probes gaps |
| `/wait-what` | Re-explain when something doesn't click |
| `/generate-topic` | Full pipeline: research → lesson → quiz → SR cards |
| `/draw-diagram` | Generate inline SVG teaching diagrams |
| `/jargon` | Annotate domain terms with hover tooltips |

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for setup, project structure, and conventions.

```bash
mise run verify     # links + lint + SVG theming + tests
mise run visual-qa  # Playwright component exercise
mise run doctor     # check tool/venv health
```

## License

[MIT](LICENSE)

---

Inspired by [Matt Pocock's teach-me skill](https://github.com/mattpocock/skills/tree/main/skills/teach-me).
