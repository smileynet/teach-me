# Teach Me

Learn any topic through research-backed lessons, interactive diagrams, and spaced repetition — powered by your AI coding assistant.

## What it does

You tell the agent what you want to learn. It researches the domain from real sources, generates interactive HTML lessons with diagrams you can open in any browser, quizzes you on understanding (not recall), and schedules reviews so knowledge sticks long-term.

You name a topic. The agent researches it, breaks it into a map of subtopics, and generates lessons one at a time. Each lesson comes with a reference doc for quick lookup, a quiz that asks you to explain concepts (not recite definitions), and spaced repetition cards that surface again when you're about to forget. If something doesn't land, say so — it'll re-explain differently.

Between lessons, the agent offers Socratic dialog — you explain what you've learned, it probes gaps and deepens your understanding through conversation. As you go, ask for more topics, drill into subtopics, or follow connections to adjacent domains. Each map leads to the next, like an infinite Wikipedia-style rabbit hole where every page is written for you and your goals.

## Quick start

```bash
mise install && mise run setup
```

Then open this project in [Kiro CLI](https://kiro.dev), [Claude Code](https://claude.ai), [Codex](https://openai.com/codex), [Cursor](https://cursor.sh), or any [Agent Skills-compatible](https://agentskills.io) client and say:

> "I want to learn about [your topic]"

The agent will ask about your goals, research the domain, and generate your first lesson.

**Already have lessons?** Open `lessons/index.html` in a browser, or:
```bash
mise run open-lesson
```

## Example topics

| Domain | What's covered |
|--------|---------------|
| [Data Engineering](examples/iceberg-workspace/) | Apache Iceberg metadata, data ingestion, change capture |
| [OIDC in Rust](examples/oidc-rust/) | Auth flows, PKCE, token validation, JWT anatomy |
| [Fitness](examples/workout-fundamentals/) | Progressive overload, recovery science, program design |
| [Game Dev](examples/godot-gamedev/) | Godot node architecture, GDScript, scene composition |

Each has lessons, reference docs, quizzes, and spaced repetition cards ready to explore.

## How it works

1. **You say what to learn** → agent asks about your goals and context
2. **Agent researches** → finds and verifies sources (never teaches from memory)
3. **Lessons appear as HTML** → open in any browser, dark/light mode, inline diagrams
4. **Quizzes test understanding** → "explain to a colleague why..." not "what is the definition of..."
5. **Spaced repetition** → reviews scheduled at optimal intervals, exportable to Anki

## Spaced repetition commands

```bash
mise run sr              # what's due for review
mise run sr:review       # review due cards
mise run sr:export-anki  # export to Anki .apkg
```

---

## For developers

See [CONTRIBUTING.md](CONTRIBUTING.md) for setup, project structure, and conventions.

```bash
mise run verify     # links + lint + SVG theming check
mise run visual-qa  # Playwright component exercise
```

MIT licensed. Skills are [Agent Skills-compatible](https://agentskills.io) — works across 40+ AI coding clients.

---

Inspired by [Matt Pocock's teach-me skill](https://github.com/mattpocock/skills/tree/main/skills/teach-me).
