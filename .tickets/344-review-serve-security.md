---
id: "344"
title: "Deep-dive serve.py trust boundaries and LAN exposure"
status: done
priority: medium
blocked_by: ["332", "339"]
type: research
tags: ["arch-review", "security"]
validation_criteria:
  - "Review exercises path traversal, overlay disclosure, cross-origin writes, and malformed status input"
  - "LAN-mode behavior is tested separately from loopback mode"
  - "Every confirmed security gap has a focused fix ticket"
---

# Deep-dive serve.py trust boundaries and LAN exposure

## Intent source

Follow-up proposed by the 2026-09-16 architecture review. LAN mode binds the local state API
to `0.0.0.0`, but its trust model has not been systematically reviewed.

## What to review

Exercise traversal, nested asset normalization, `/.user` disclosure bypasses, domain/slug
resolution, malformed writes, CSRF/origin behavior, host exposure, error leakage, and
denial-of-service-sized inputs. Separate localhost assumptions from LAN promises.

## Context

Read `tools/serve.py`, `tools/lib/overlay.py`, `tools/lib/serve_harness.py`, ADR 0015,
#163, #198, #332, and #339. Do not claim a vulnerability without reproducible impact.

## Acceptance criteria

- [x] Assets, state, and network trust boundaries are documented
- [x] Automated probes cover traversal, hidden state reads, invalid writes, and cross-origin mutation
- [x] LAN and loopback exposure are assessed separately
- [x] Findings include severity, evidence, and specific mitigation
- [x] Confirmed gaps receive tickets; clean areas are reported without manufactured findings

## Resolution

Completed the reproducible trust-boundary review in `.scratch/research/344-serve-security.md`. Loopback traversal and hidden-state checks were clean, while the report reproduces overlay write loss under concurrency, unbounded/reflected malformed input, wildcard domain resolution, and unauthenticated LAN mutations. Tickets #353–#355 capture atomic persistence, request hardening, and the required LAN policy decision; #332/#339 own canonical workspace resolution. Evidence: live HTTP probes and a repeated 100-update concurrency test.
