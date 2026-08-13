# Contributing

Thanks for your interest in teach-me! This is a test bed for learning-oriented AI agent skills.

## Quick Start

```bash
git clone https://github.com/smileynet/teach-me.git
cd teach-me
mise install        # Python 3.12, Node 22, uv
mise run setup      # Install Python dependencies
mise run verify     # Confirm everything works
```

## Project Structure

```
.kiro/skills/       — Agent skills (teach, generate-topic, quiz-me, etc.)
.kiro/steering/     — Visual teaching guidelines
tools/              — CLI scripts (diagram generation, quiz pages, verification)
assets/             — Shared CSS, JS, scaffolds, SVG patterns
examples/           — 4 example workspaces (iceberg, oidc-rust, workout, godot)
lessons/            — Generated index page
```

## How to Contribute

### Report Issues

Open an issue describing:
- What you expected to happen
- What actually happened
- Steps to reproduce (if applicable)

### Suggest Features

Open an issue with:
- The problem you're trying to solve
- How you'd like it to work
- Any alternatives you considered

### Submit Changes

1. Fork the repository
2. Create a branch: `git checkout -b fix/your-change`
3. Make your changes
4. Run `mise run verify` — must pass
5. Commit with conventional format: `feat(scope): what changed`
6. Open a pull request

## Development Conventions

- **No build step**: Pages are self-contained HTML with shared CSS variables
- **SVG diagrams**: Use `var(--svg-*)` CSS custom properties (never hardcoded hex)
- **Page types**: Read the scaffold in `assets/scaffolds/` before creating a new page
- **Tools accept `--workspace`**: All generation tools work on any workspace path
- **Topic generation is sequential**: One topic completes fully before the next begins
- **Research before teaching**: Never generate lessons from memory — cite sources

## Running Tests

```bash
mise run verify           # Links + lint + SVG check
mise run visual-qa        # Playwright component exercise
mise run sr:check         # SR question quality
```

## Key Files

| File | Purpose |
|------|---------|
| `mise.toml` | Task runner configuration |
| `assets/style.css` | Theme variables (dark + light + SVG palette) |
| `assets/scaffolds/` | Page templates with annotations |
| `tools/check-topic-completeness.py` | Verify all artifacts exist for a topic |
| `.kiro/skills/generate-topic/SKILL.md` | Full generation pipeline documentation |
