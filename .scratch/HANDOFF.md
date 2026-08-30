---
created_at: 2026-08-30T07:21:00-07:00
base_commit: dc430c4
handoff_key: library-rename-unifying-root
---

# Handoff

> Supersedes `content-graph-schema`. This session finished the content-graph chain, shipped
> the global map, did a UX pass, and renamed examples/→library/ with a unifying-root fix.

## Objective
Make the committed library navigable end-to-end (aggregate index + forest map → domain
maps → lessons), served from one root. Tracked in tickets (NO PLAN.md — `tkt ready` is authoritative).

## Constraints
- `tkt` via `D:\code\tkt\target\release\tkt.exe`. Python via `.venv\Scripts\python.exe` (mise shim recursion). Windows-first.
- PowerShell mangles inline JSON / `->` / long `git -m` / `tkt close --resolution` — use a file (`--data @f`, `git commit -F`, temp resolution). Confirmed 3x (now in AGENTS.md Env).
- New tools MUST reconfigure stdout UTF-8 (cp1252 crash) — rule in `.memory/specs/environment-gotchas.md`; #265 will make it a verify gate.
- Pre-existing ink-test-project/test-scene working-tree churn is #234/#233's, NOT ours — exclude from commits (stage explicitly, never `git add .`).

## Prior Decisions
- **ADR-0015** (accepted): document-relative `../assets` + serve/assembly-provided unifying root.
  NEVER root-relative `/assets` (forces `<base>`, breaks in-page anchors/SVG on GitHub project pages).
- SR stays slug-keyed (re-keying resets FSRS state); node-id join at graph boundary only (#255).
- Cross-map prereqs are VALID (intentional sibling forks) — resolved at forest scope (#260, in #155).

## Current State
Clean stop, nothing mid-flight. Closed this session: #258, #255, #264, #155, #260, #183, #198
(+ UX #268/#269/#270). serve.py serves `library/` (fresh-clone default) with any-depth
`**/assets` + `**/index.html` normalize routes (multi-domain gated). `library/{index,global-map}.html`
committed with library-rooted hrefs. All verified via Playwright + `mise run verify` EXIT 0.

## Next Steps
Frontier (`tkt ready`, HIGH first): **#272** (Pages workflow stale — assembles nonexistent
examples/*/, ships only docs/index.html; must assemble `library/` into `_site/` at consistent
depth so `../assets` resolves — the STATIC half of ADR-0015; completes what #198 did dynamically).
Then **#271** (index primary-CTA/"what's next"), **#265** (cp1252 verify gate, ~21 tools),
**#266/#267** (global-map Phase 2 concept edges / Phase 3 lazy detection). #184 (private overlay) unblocked.

## Fog
- #272 base-path decision: project page (`smileynet.github.io/teach-me/`) — confirm document-relative
  survives the `/{repo}/` subpath in the assembled `_site/` (should, if depth is consistent) before
  adding any `<base>`. Test the ACTUAL subpath deploy, not just localhost.

## Recommended Updates
- [ ] #272 will need `docs/index.html` reconciled with the generated `library/index.html` landing (decide which is the deployed root).
