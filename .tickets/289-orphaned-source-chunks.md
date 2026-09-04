---
id: "289"
title: "Decide: orphaned source-chunks (code-design.json, rust.json) — generate or prune"
status: open
blocked_by: []
priority: low
tags: [content, source-ingest]
---

# Decide: orphaned source-chunks (code-design.json, rust.json) — generate or prune

## Problem

Surfaced by #176's domain review (2026-09-03). Root `source-chunks/` holds 3 files; only
one binds to a lesson-bearing library domain:

| File | Content | Lesson-bearing domain? |
|------|---------|------------------------|
| `toon-shaders.json` | Godot toon/cel shading | ✅ godot-gamedev (0004 toon-banding, 0005 triplanar) |
| `code-design.json` | Ousterhout *A Philosophy of Software Design* — "Nature of Complexity" | ❌ no matching library domain exists |
| `rust.json` | Rust "Ownership Fundamentals" | ⚠️ oidc-rust exists but its lessons are OIDC auth-flows / JWT, NOT ownership — content mismatch |

So `code-design.json` and `rust.json` were validated at the hints level only (#176 Half A);
they have no committed lessons to enrich or coverage-check against. They're either latent
content seeds or dead weight.

Source-chunks are domain-agnostic bare arrays (no stored lesson back-reference); binding is
by filename convention + content match at ingest time (`match_section.py`).

## Decision needed

For each orphan, pick:
1. **Generate** — stand up a new domain and lessons (code-design → a "software-design" domain
   is a natural fit; rust.json → a rust-language domain, distinct from oidc-rust).
2. **Prune** — delete the chunk file if we don't intend to build the domain.

Do NOT leave them ambiguous — that's what this ticket resolves.

## Acceptance criteria

- [ ] Decision recorded for `code-design.json` (generate a software-design domain, or prune)
- [ ] Decision recorded for `rust.json` (generate a rust-language domain, or prune)
- [ ] If generate: follow-up ticket(s) filed via `generate-topic`; if prune: files removed + committed
