---
id: "333"
title: "Sweep doc drift and dead frontend code left by SSE removal"
status: open
priority: medium
blocked_by: []
type: fix
tags: ["arch-review"]
---

# Sweep doc drift and dead frontend code left by the SSE removal

## Why

#317/#318 removed the generation server and SSE machinery, but agent-facing docs still describe it and the deletion list from done ticket #106 was never fully executed. The primary agent doc (AGENTS.md) pointing at deleted infra misleads every future session.

## Findings (verified 2026-09-16)

1. `AGENTS.md:20` workspace layout documents `assets/services/ — signal services (generation.js SSE stream)` — the directory does not exist; repo-wide glob for `generation*.js` = 0 hits.
2. `AGENTS.md` command table describes `mise run verify` as "Links + lint + SVG var check" — it understates the actual 17-step gate.
3. `mise.toml:56` serve task description still says "Start **generation** server" (serve.py docstring was fixed; mise wasn't).
4. Dead files listed for deletion in #106 but still on disk, referenced by nothing: `assets/progressive-reveal.js`, `assets/quiz.js`, `assets/components/ProgressiveReveal.js`.

Out of scope here (already ticketed): bare-`python` serve tasks = #247; Windows-broken bash task loops = #304.

## What to build

- Correct the AGENTS.md layout entry and command descriptions to match reality (static + status server; accurate verify description)
- Fix the mise serve task description
- Delete the three dead JS files after a reference grep confirms zero HTML/JS consumers

## Acceptance criteria

- [ ] AGENTS.md contains no reference to `assets/services` or SSE generation; verify and serve are described accurately
- [ ] mise.toml serve task description matches the static + status reality
- [ ] The three dead JS files are deleted; grep for them over library/ HTML returns nothing
- [ ] `mise run verify` and `mise run visual-qa` pass after deletion

## Resolution

TBD
