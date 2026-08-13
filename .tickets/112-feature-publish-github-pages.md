---
id: "112"
title: "Publish examples on GitHub Pages as live demo"
type: feature
status: done
priority: medium
blocked_by: []
---

# Publish examples on GitHub Pages as live demo

## What to build

Deploy the example workspaces to the repo's GitHub Pages site (smileynet.github.io/teach-me) so people can see what the tool produces without cloning the repo.

## Deliverables

- GitHub Actions workflow (`.github/workflows/pages.yml`) that builds and deploys on push to main
- Landing page at root with links to each example workspace
- Each example workspace browsable: index → map → lessons → quizzes
- Static-only (no server needed) — the Preact components load vendored deps from relative paths

## Implementation Plan (from research)

**Strategy:** Copy examples + shared assets into a flat `_site/` directory, resolving all symlinks. Deploy via official `actions/deploy-pages`.

**Deploy structure:**
```
_site/
  .nojekyll
  index.html                          ← landing page (links to examples)
  assets/                             ← copied (not symlinked) shared assets
    style.css
    vendor/                           ← preact, signals, htm, dagre
    components/                       ← MapView, QuizView, etc.
    services/
  examples/
    iceberg-workspace/
      assets/                         ← COPY of shared assets (symlink resolved)
      lessons/
      reference/
      maps/
    godot-gamedev/
    oidc-rust/
    workout-fundamentals/
```

**Key decisions:**
1. Symlinks resolved via `cp -rL` (GitHub Pages forbids symlinks)
2. `.nojekyll` at root (bypass Jekyll processing)
3. All paths already relative (no base-path issue)
4. Import maps in each page already use `../assets/vendor/` which resolves correctly
5. Generate buttons get a graceful fallback (no server = show "Clone to generate" message)

**Workflow:** `.github/workflows/pages.yml` with `actions/upload-pages-artifact` + `actions/deploy-pages`

**Landing page:** Simple HTML listing the 4 example workspaces with descriptions, linking to each one's `lessons/index.html`

## Acceptance Criteria

- [x] GitHub Pages deploys automatically on push to main
- [x] Landing page lists all example workspaces with descriptions
- [x] Each example's index, map, lessons, quizzes are browsable
- [x] Dark theme renders correctly
- [x] No broken asset links (style.css, vendor JS, components)
- [x] Generate buttons show graceful fallback (no server = no generation)
- [x] README links to the live demo

## Context

- Example workspaces: `examples/iceberg-workspace/`, `examples/godot-gamedev/`, `examples/oidc-rust/`, `examples/workout-fundamentals/`
- Assets: `assets/` (style.css, vendor/, components/, services/)
- Existing CI: `.github/workflows/verify.yml`

## Resolution (2026-08-13)

TBD
