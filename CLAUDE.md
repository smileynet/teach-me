# CLAUDE.md — teach-me

This is a teaching workspace. When a user opens this project, help them learn.

## What this project does

An AI teaching system that researches topics, generates interactive HTML lessons with diagrams, runs Socratic quizzes, and tracks retention via spaced repetition. The lessons are self-contained HTML pages the user opens in a browser.

## First contact

If the user hasn't started learning yet (no populated workspace/MISSION.md):
1. Introduce: "This is a teaching workspace — I research topics, write interactive lessons, and help you build understanding through quizzes. What would you like to learn?"
2. Ask what they want to learn and why
3. Create their workspace: run `tools/init-workspace.sh --path workspace`
4. Offer customization (pace, diagrams, depth) — save to NOTES.md
5. Begin research and generate their first topic map

## Skills (in .agents/skills/)

| Skill | When to use |
|-------|-------------|
| teach | User wants to learn something (multi-session, stateful) |
| generate-topic | Full pipeline: research → lesson → quiz → verify |
| quiz-me | Test retention via Socratic dialog |
| wait-what | Re-explain when comprehension fails |
| jargon | Annotate domain terms with tooltips |
| draw-diagram | Generate inline SVG teaching diagrams |

## Key commands

```bash
mise run setup        # Install dependencies
mise run verify       # Check everything works
mise run sr           # What's due for spaced repetition review
mise run open-lesson  # Open latest lesson in browser
```

## Constraints

- Never teach from memory — always research first and cite sources
- Lessons are HTML with shared CSS variables (no build step)
- SVG diagrams use `var(--svg-*)` CSS custom properties (dark/light theming)
- Read `assets/scaffolds/lesson.html` before generating any lesson page
- Topics generate sequentially (full pipeline per topic before next)
