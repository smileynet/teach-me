---
id: "087"
title: "Fix: add Core Concept and Decision Aid sections to oidc-rust reference 0002"
status: open
blocked_by: []
priority: low
---

# Fix: add Core Concept and Decision Aid sections to oidc-rust reference 0002

## Problem

The reference page for Token Anatomy (`examples/oidc-rust/reference/0002-token-anatomy.html`) is missing the required "Core Concept" h2 section (one bold sentence summary) and a "Decision Aid" section (conditional if/then guidance). The scaffold requires both.

## What to build

1. Add an h2 "Core Concept" section at the top with a bold one-sentence mental model
2. Verify a "Decision Aid" section exists (it has "Debugging 401s" which is close — check if it meets the scaffold's conditional format)

## Acceptance criteria

- [ ] Page has `<h2>Core Concept</h2>` with a bold summary sentence
- [ ] Page has a decision aid section with conditional actions
- [ ] `mise run verify` passes
