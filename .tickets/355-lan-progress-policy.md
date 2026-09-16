---
id: "355"
title: "Define and enforce LAN access policy for private learner progress"
status: open
priority: high
type: research
blocked_by: ["354"]
tags: ["arch-review", "server", "privacy", "security"]
validation_criteria:
  - "The documented LAN threat model matches enforced behavior"
---

# Define and enforce LAN access policy for private learner progress

## Intent

Choose and enforce a safe policy for exposing a local learning server on a LAN without exposing mutable private learner progress to every reachable peer.

## Context

`serve --lan` currently exposes unauthenticated status reads and writes to reachable clients. Loopback behavior is safer; the project has not selected whether LAN is presentation-only, authenticated collaboration, or a trusted-home-network convenience.

## What to build

Document the threat model and select an explicit LAN mode. Implement the smallest matching access policy, including safe defaults, visible warnings, and regression coverage.

## Acceptance criteria

- [ ] An ADR records the supported LAN use case, trust assumptions, and rejected alternatives.
- [ ] Loopback remains the default and the LAN opt-in explains its progress-data behavior.
- [ ] LAN mode cannot expose mutable private progress beyond the selected policy.
- [ ] Browser/API tests prove anonymous LAN-equivalent requests have exactly the documented access.
- [ ] Documentation distinguishes local progress, shareable lesson content, and any collaboration mechanism.
