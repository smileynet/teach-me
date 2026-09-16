---
id: "348"
title: "Deep-dive static-host and local-server capability consistency"
status: in_progress
priority: medium
blocked_by: ["331", "332", "338", "341"]
type: research
tags: ["arch-review", "platform"]
validation_criteria:
  - "A capability matrix covers file, static HTTP, Pages, single-domain, library-root, and LAN modes"
  - "Every intentional degradation is user-visible and documented"
  - "Every accidental inconsistency has a focused follow-up ticket"
---

# Deep-dive static-host and local-server capability consistency

## Intent source

Follow-up proposed by the architecture review. Static fallback and live local state are both
intentional, but their exact capability differences are scattered across ADRs and tickets.

## What to review

Execute a matrix for direct `file://`, simple static HTTP, GitHub Pages, single-domain serve,
library-root serve, and LAN serve. Cover reading, navigation, maps, quizzes, preferences,
progress, SR, generation prompts, private content, and offline behavior.

## Context

Read ADRs 0003/0012/0014/0015/0016, `tools/serve.py`, `tools/assemble-site.sh`,
`assets/page-shell.js`, and #279/#319/#331/#332/#338/#341.

## Acceptance criteria

- [ ] Matrix states supported, degraded, and unsupported behavior per environment
- [ ] Every degraded path gives an honest explanation rather than a silent no-op
- [ ] Direct deep links and JavaScript-disabled reading are exercised
- [ ] Progress respects the local-only rule in every environment
- [ ] Accidental inconsistencies receive tickets; intentional differences are documented

## Progress

The direct capability matrix is recorded in `.memory/research/2026-09-16-architecture-deep-dives.md`: static reading works, while Pages is blocked by #331, library-root behavior by #332/#338, and shared learner state by #341/#349. Direct-link and JavaScript-disabled browser probes still need specialist/browser evidence before closure.

## Resolution

TBD
