---
id: "337"
title: "Recommended follow-up review areas"
status: open
priority: low
blocked_by: []
type: research
tags: ["arch-review"]
---

# Recommended follow-up review areas from the 2026-09-16 architecture review

## Why

The 2026-09-16 review covered four lanes (serving/library/deploy, frontend, map/graph, generation/ingest/validation infra) at the architecture level. These areas were out of its scope or only spot-checked, and each carries known drift signals.

## Recommended areas, with the signal that motivates each

1. **SR subsystem deep-dive** — `sm2.py`, the seven `sr:*` mise tasks, `tools/lib/overlay.py` lifecycle vs the #255 local-user-state model. Signals: open #170 (dedup never built) and #172 (stale-lesson report never built) suggest doc/plan drift between the SR design and shipped tooling; retention-correctness of the SM-2 implementation itself was never reviewed.
2. **serve.py security pass (defensive)** — LAN mode binds 0.0.0.0:8787. Review: static-mount path traversal, status-POST payload validation (slug → path interpolation), `/.user/` guard bypass, CORS/origin behavior when exposed on LAN. No known exploit; never audited.
3. **Lesson content quality audit vs `.kiro/steering/visual-teaching.md`** — the review verified page structure (heads, import maps, module scripts) for 1-2 pages per pattern, not pedagogical conformance across the 7 library domains (narrative framing, honest visual validation, no-silent-buttons in authored content).
4. **`.kiro/skills` effectiveness audit** — AGENTS.md calls this repo a test bed for agent skills; activation accuracy and non-redundancy of the 10+ skills have never been measured (e.g., 199/200/202/203 ink-skill family, teach vs generate-topic overlap).
5. **Regeneration matrix for all 7 domains** — re-run `maps:regenerate` + `index:generate` + `map:global` idempotence checks per the #278/#279/#316 gotchas. The two newest domains (gltf-format, godot-asset-pipeline) were never gate-verified (see #331) — their baked artifacts may carry other latent scaffold debt.
6. **CI absence decision** — verification is pre-commit-only (deliberate per #131/#229). Reconsider a lint-only or verify-subset CI on push, or accept and document the posture explicitly.

## Deliverable

A prioritized shortlist (max 3) with a ticket per accepted area and an explicit "not now" note for the declined ones.

## Acceptance criteria

- [ ] Each of the 6 areas triaged: ticket created, or declined with one-line rationale
- [ ] Accepted areas have tickets with verified findings (subagent claims checked against source per AGENTS.md)

## Resolution

TBD
