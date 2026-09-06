# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.0] — 2026-09-06

Three new hands-on domains (glTF, ink narrative scripting, and a full Godot toon-shader +
Blender-texture-prep track), a unified Tree/Map browser with private progress overlays, and a
validation-first pipeline that runs lesson code in its real runtime.

### New domains & lessons

- **glTF Format** — new 6-lesson track: anatomy of the standard, Blender authoring/export, engine import, materials & textures, animation/skins/morphs, extensions & optimization. Each lesson ships a runnable stdlib artifact.
- **Ink narrative scripting (ink + Godot)** — new 8-lesson track: flow & knots, choices & weave, variables & conditionals, functions & tunnels, Godot integration, tags-as-commands, state bridge, production patterns.
- **Godot toon shaders** — new 12-lesson shader track (spatial shader anatomy, banding, triplanar, outlines, color simplification, Gooch/wrapped/specular lighting, overlays).
- **Blender texture prep** — new 6-lesson subtrack: texture audit, albedo posterize, palette snap, control maps, bake & export, shader wiring.
- **Godot fundamentals** — nodes & scenes, GDScript, physics & collision.

### Features

- **Unified Tree | Map browser** — the index and global map are one two-view page; a forest map shows every domain as a node.
- **Per-domain landing pages** with a first-time orientation and a "resume where you left off" cue.
- **Private progress overlays** — completion + spaced-repetition state lives in a local `.user/` overlay merged in at render time; the committed library stays clean.
- **Honest Generate buttons** — quiz/lesson buttons open shipped content when it exists, and otherwise hand you the exact prompt to run with an agent instead of faking generation.
- **Concept extraction & hints** feeding glossary, quiz, and coverage checks.
- **Teach from a source document** — one-command ingest: chunk → classify → build map → enrich prerequisites, with source-attributed quiz questions.
- **Downloadable code files** with copy + download on every code block; **read-time estimates** on lessons.

### Tooling

- **Ink validation suite** — compile/lint, playthrough dead-end detection, golden-transcript output checks, and real headless-Godot runtime validation.
- **Property oracles** — Blender (posterize, palette-snap, control-maps, bake/export) and glTF (GLB/JSON structural + material color-space + skin/animation) oracles assert the math each lesson teaches; opt-in `verify:blender` runtime gate.
- **Language-aware code-compile gate** — lesson code blocks compile in `mise run verify`.
- **Single-source site deploy** — one `_site` assembler shared by the deploy workflow and a local dry-run; cross-platform reference-repo rehydrate.

### Fixes

- Deterministic index generation — per-domain pages no longer inherit an unrelated machine-local mission.
- Depth-aware breadcrumbs and quiz pages for lessons in domain subfolders.
- Mark-complete wires through to the map instead of silently failing.
- High-contrast focus ring in both themes; Windows UTF-8 stdout guards; ink line-drop/double-space/read-count fixes.

## [0.2.0] — 2026-08-15

### Interactive quizzes

- **Sequence questions** — reorder steps into the correct order with up/down/swap controls
- **Match questions** — click term then definition to pair them; color-coded pairs (A/B/C/D) show what's connected
- **Fill-in-the-blank** — type answers into gaps within a statement; immediate right/wrong feedback
- **Show all at once** — toggle between one-at-a-time and all-questions-visible mode
- **Answer criteria as numbered checklist** — "Should mention: (1)...(2)..." now renders as a proper list
- **"Another angle" explanation** — every answer can include a companion analogy or different perspective, shown alongside the criteria

### Navigation

- **Breadcrumb navigation** on every page: All Lessons › Domain › Lesson (or Quiz / Reference)
- **Consistent page template** — all generators (quiz, map, index, resources) use a single `page_template.py` for boilerplate
- **Completion toggle** — click the Complete button again to un-complete a topic

### Architecture

- **Page shell orchestrator** — single `page-shell.js` replaces 5 self-mounting components with explicit initialization order
- **Template contract** — Python generators produce data only; template handles all HTML boilerplate, scripts, and navigation
- **Pre-commit hooks** — `mise run verify` runs on every commit (links, lint, SVG vars, pytest, Playwright); no CI on push
- **Tagged releases** — GitHub Pages deploys on `v*` tags (stable example set)

### Quality

- **6 question archetypes** defined (explain-why, scenario, predict, debug, teach-back, connect) with enforcement in generation guidance
- **Criteria format enforced** — `sr:check` flags questions without numbered points
- **Interactive questions in all 4 example workspaces** — sequence, match, and fill for every domain
- **Accessibility** — `aria-live` announcements on all quiz feedback; keyboard navigable throughout

### Fixes

- `mise run verify` now passes end-to-end (venv pinned to mise Python + server-wait HTTPError handling)
- Button text colors readable in dark mode (explicit `color: var(--text)` on interactive elements)
- Quiz breadcrumb paths corrected (lessons/quiz/ → one level up, not two)
- Typography preferences applied on all page types (quiz, reference, map)
- Jargon HTML stripped from breadcrumb titles

## [0.1.0] — 2026-08-12

### What you can do

- **Learn any topic**: Tell the agent what you want to learn. It researches the domain, generates interactive lessons with diagrams, and tracks your understanding over time.
- **Browse 4 example domains**: Data engineering (Iceberg on AWS), security (OIDC in Rust), fitness (Workout Fundamentals), game development (Godot). Each has lessons, quizzes, and reference docs ready to explore.
- **Quiz yourself**: After lessons, reveal-and-rate quiz cards test whether you can explain concepts — not just recall definitions.
- **Track retention**: Spaced repetition schedules reviews at the right intervals. Export to Anki if you prefer a dedicated app.
- **Explore topic maps**: Interactive visual maps show what's available, what you've completed, and what to learn next.
- **Dark and light modes**: All pages including diagrams adapt to your theme preference.
- **Works in any AI assistant**: Open this project in Kiro CLI, Claude Code, Codex, Cursor, or any Agent Skills-compatible client — the agent knows what to do.

### For contributors

- MIT licensed, CI on push, `mise run verify` validates everything
- See CONTRIBUTING.md for setup and conventions
