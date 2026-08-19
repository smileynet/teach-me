# Contributing

Thanks for your interest in teach-me! This is a test bed for learning-oriented AI agent skills.

## Quick Start

```bash
git clone https://github.com/smileynet/teach-me.git
cd teach-me
mise install        # Python 3.12, Node 22, uv
mise run setup      # Install deps + configure pre-commit hooks
mise run verify     # Confirm everything works
```

After setup, pre-commit hooks run `mise run verify` automatically on every commit. You don't need to remember to run it manually.

## Project Structure

```
workspace/          — Your live learning workspace (gitignored, auto-created on first serve)
.kiro/skills/       — Agent skills (teach, generate-topic, quiz-me, etc.)
.kiro/steering/     — Visual teaching guidelines
.memory/            — Persistent knowledge (glossary, ADRs)
tools/              — CLI scripts (diagram generation, quiz pages, verification)
tools/lib/          — Python helpers (page_template.py for HTML generation)
assets/             — Shared CSS, JS components, SVG patterns
assets/components/  — Preact components (mounted by page-shell.js)
assets/vendor/      — Vendored Preact + Signals + HTM + dagre
examples/           — 4 example workspaces (iceberg, oidc-rust, workout, godot)
.tickets/           — Local ticket tracking
.githooks/          — Pre-commit hooks (auto-wired by mise run setup)
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
4. Commit — pre-commit hooks run verification automatically
5. Use conventional format: `feat(scope): what changed`
6. Open a pull request

Bypass hooks for WIP commits: `git commit --no-verify`

## Development Conventions

- **No build step**: Pages are self-contained HTML with shared CSS variables
- **Single entry point**: Every lesson page loads `page-shell.js` — never import components individually
- **Page template**: Generators call `tools/lib/page_template.py` — don't assemble HTML boilerplate manually
- **SVG diagrams**: Use `var(--svg-*)` CSS custom properties (never hardcoded hex)
- **Tools accept `--workspace`**: All generation tools work on any workspace path
- **Topic generation is sequential**: One topic completes fully before the next begins
- **Domain subfolders**: Lessons go in `lessons/{domain-slug}/NN-slug.html` — per-domain numbering, not global
- **Narrative code framing**: Every code block in a lesson has surrounding text explaining what's changing, why, and how it connects to what came before (see visual-teaching.md § Code Block Pedagogy)
- **Research before teaching**: Never generate lessons from memory — cite sources
- **Question variety**: Use 3+ different archetypes per topic (see generate-topic skill)

## Running Tests

```bash
mise run verify           # Full pipeline: links + lint + SVG + pytest + Playwright
mise run visual-qa        # Playwright component exercise (auto-serves)
mise run sr:check         # SR question quality gate
```

Pre-commit hooks run `mise run verify` on every commit. Pre-push is not needed — everything gates on commit.

## Deployment

- **GitHub Pages** deploys on tagged releases (`v*` tags) via `.github/workflows/pages.yml`
- **Manual deploy**: trigger the workflow via GitHub Actions UI (workflow_dispatch)
- **Local preview**: `mise run serve` (port 8787) or `mise run serve:lan` (0.0.0.0:8787)

## Key Files

| File | Purpose |
|------|---------|
| `mise.toml` | Task runner configuration |
| `assets/page-shell.js` | Single entry point for all lesson page components |
| `assets/style.css` | Theme variables (dark + light + SVG palette) |
| `tools/lib/page_template.py` | HTML page generation (all page types) |
| `tools/check-topic-completeness.py` | Verify all artifacts exist for a topic |
| `.kiro/skills/generate-topic/SKILL.md` | Full generation pipeline documentation |
| `.githooks/pre-commit` | Verification hook (runs mise run verify) |
