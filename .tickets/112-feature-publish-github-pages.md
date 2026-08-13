---
id: "112"
title: "Publish examples on GitHub Pages as live demo"
type: feature
status: in_progress
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

## Considerations

- The examples use `../assets/` symlinks — GitHub Pages needs real files (resolve symlinks or copy assets into each example)
- Map pages use dagre from `assets/vendor/dagre.min.js` — must be included
- No `/api/generate` endpoint — "Generate this topic" buttons should degrade gracefully (show a message like "Clone the repo to generate lessons")
- Quiz/review pages work fully client-side (data island + Preact)

## Acceptance Criteria

- [ ] GitHub Pages deploys automatically on push to main
- [ ] Landing page lists all example workspaces with descriptions
- [ ] Each example's index, map, lessons, quizzes are browsable
- [ ] Dark theme renders correctly
- [ ] No broken asset links (style.css, vendor JS, components)
- [ ] Generate buttons show graceful fallback (no server = no generation)
- [ ] README links to the live demo

## Context

- Example workspaces: `examples/iceberg-workspace/`, `examples/godot-gamedev/`, `examples/oidc-rust/`, `examples/workout-fundamentals/`
- Assets: `assets/` (style.css, vendor/, components/, services/)
- Existing CI: `.github/workflows/verify.yml`
