---
id: "112"
title: "Publish examples on GitHub Pages as live demo"
type: feature
status: done
priority: medium
blocked_by: []
tags: [platform]
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

- [x] GitHub Pages deploys on demand — as built: the workflow builds only for a `v*` tag
      push or manual `workflow_dispatch`; a plain push to main skips the build job
      (`.github/workflows/pages.yml:28-40`). "Automatically on push to main" as
      originally written was overstated; amended 2026-09-17 (#335).
- [x] Landing page lists all example workspaces with descriptions
- [x] Each example's index, map, lessons, quizzes are browsable
- [x] Dark theme renders correctly
- [x] No broken asset links (style.css, vendor JS, components)
- [x] Generate buttons show graceful fallback (no server = no generation)
- [ ] README links to the live demo — never shipped: no demo URL exists in README.md
      (verified 2026-09-17, #335). Left unchecked honestly rather than faked; pick this
      up if/when a public demo link is wanted.

## Context

- Example workspaces: `examples/iceberg-workspace/`, `examples/godot-gamedev/`, `examples/oidc-rust/`, `examples/workout-fundamentals/`
- Assets: `assets/` (style.css, vendor/, components/, services/)
- Existing CI: `.github/workflows/verify.yml`

## Resolution (2026-08-13; corrected 2026-09-17 per #335)

Shipped the GitHub Pages pipeline: `.github/workflows/pages.yml` builds a flat
`_site/` (symlinks resolved, `.nojekyll`, relative paths) and deploys via the official
Pages actions, with a landing/index page linking each workspace. Two records corrected
by the 2026-09-16 architecture review, verified against source: (1) deploys are gated
on a `v*` tag or manual dispatch — not every push to main; (2) no README live-demo link
was ever added (AC left unchecked above).
