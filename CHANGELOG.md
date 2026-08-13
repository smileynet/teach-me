# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] — 2026-08-12

### Added

- **Teaching system**: Multi-session lessons with stateful workspaces (MISSION, RESOURCES, MAP, lessons, reference docs, quiz pages, SR questions)
- **4 example workspaces**: Iceberg on AWS, OIDC in Rust, Workout Fundamentals, Godot Game Dev
- **Skills**: teach, generate-topic, quiz-me, wait-what, jargon, draw-diagram, visual-qa, theme, browse-and-verify
- **generate-topic pipeline**: 4-phase orchestration (research → generate → post-process → verify) with parallel subagent dispatch for research and verification
- **Interactive map pages**: SVG graph visualization of topic relationships with status coloring
- **All Lessons index**: Dashboard showing all domains with progress rings
- **Quiz system**: Per-topic quiz pages with reveal/rate cards, 4 question types (explain, apply, predict, quick-check)
- **Spaced repetition**: JSONL question bank, review scheduling, analytics, Anki export
- **SVG diagram system**: draw-diagram.py with CSS custom properties for dark/light theming
- **Page scaffolds**: Annotated templates for lesson, reference, quiz, and quick-check pages
- **Glossary system**: Inline term tooltips via glossary.js + glossary-data JSON
- **Theme system**: Dark-first (Purple Night) with light mode toggle + localStorage persistence
- **Verification tooling**: Link checker, HTML linter, SVG variable checker, topic completeness checker
- **Workspace tools**: init-workspace.sh, generate-quiz-page.py, generate_map_page.py, generate_index_page.py, jargon-annotate.py — all with `--workspace` flag for flexible paths

### Design decisions

- Research-first: every lesson requires domain research before writing (ADR 0002)
- Agent-complete pages: no build step, HTML with shared CSS variables (ADR 0003)
- Informal posture: colleague at whiteboard, not course instructor (ADR 0001)
- MAP.md domain scaffolding: 5-9 subtopics with soft prerequisites (ADR 0004)
