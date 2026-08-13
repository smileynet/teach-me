---
created_at: 2026-08-12T18:35:00-07:00
base_commit: 5a3382f
handoff_key: teach-me-v010
---

# Handoff

## Objective
teach-me is a public, released AI teaching system. v0.1.0 shipped with 4 example workspaces, full generate-topic pipeline, cross-harness compatibility, and CI. Next work is feature expansion (quiz types, navigation, Socratic depth).

## Constraints
- Lessons are static HTML with CSS variables — no build step, no SSR
- SVG diagrams must use `var(--svg-*)` (enforced by `mise run verify`)
- Topics generate sequentially via generate-topic pipeline (never batch)
- Research-first: never teach from parametric memory
- Repo is PUBLIC: https://github.com/smileynet/teach-me

## Prior Decisions
- ADR 0001: informal colleague posture (not course instructor)
- ADR 0002: research-first (no lesson from memory)
- ADR 0003: agent-complete pages (shared CSS contract, no build)
- ADR 0004: MAP.md domain scaffolding (5-9 topics, soft prereqs)
- Topics sequential, parallel within (research/verify fan out subagents)
- Iceberg workspace kept as "retrofitted legacy" — proves upgradability

## Current State
- v0.1.0 released, GitHub release + tag at `5a3382f`
- All HIGH tickets closed (079-088, 072). 13 LOW/MEDIUM remain.
- 4 workspaces fully passing `check-topic-completeness --all`
- CI running on push (`.github/workflows/verify.yml`)
- Cross-harness: `.agents/skills/` symlinks + `CLAUDE.md`
- Onboarding: teach skill has "Session Start (new learner)" flow
- Tools: `release.sh` (5-gate), `jargon-annotate.py`, `check-topic-completeness.py`, `check-svg-vars.py`, `migrate-svg-vars.sh`

## Next Steps
1. Ticket 089 [MED] — Socratic dialog depth (read lesson context before quiz dialog)
2. Ticket 078 [MED] — Quiz question type system (MC, open-answer, interactive SVG)
3. Ticket 045 [MED] — Zoom in/out recursive subtopic navigation
4. Ticket 063 [MED] — Research free-form topic generation from map page
5. Any LOW ticket from the backlog (13 available)

## Fog
- How should map pages handle dark mode? (Graphviz SVG uses hardcoded hex — known limitation, no clear fix without post-processing)
- Should quiz completion auto-mark a topic done? (ticket 070 — research needed)

## Evidence
- `mise run verify` passes (links + lint + SVG vars)
- `python3 tools/check-topic-completeness.py --workspace examples/oidc-rust --all` → all pass
- GitHub release: https://github.com/smileynet/teach-me/releases/tag/v0.1.0
- `tkt ready` shows 13 open tickets (all LOW/MEDIUM, no blockers)
