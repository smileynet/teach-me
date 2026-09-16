---
id: "354"
title: "Bound and validate local status API mutation requests"
status: open
priority: medium
type: security
blocked_by: ["332", "339"]
tags: ["arch-review", "server", "security"]
validation_criteria:
  - "Malformed or oversized status requests fail predictably without mutating progress"
---

# Bound and validate local status API mutation requests

## Intent

Bound and type-check status mutations at the HTTP trust boundary, and resolve requested domains exactly.

## Context

The server reflects huge invalid JSON bodies in error responses, has no request-size limit, and interpolates domain strings into a glob where wildcard inputs can select the wrong map. The canonical map resolver work in #332 and workspace context in #339 are prerequisites.

## What to build

Define a compact schema and maximum request/error sizes, reject extra or invalid fields, and replace glob-based map lookup with exact canonical resolution.

## Acceptance criteria

- [ ] The mutation schema permits only documented fields and value ranges; unexpected fields are rejected.
- [ ] Oversized request bodies and error responses are bounded and return an appropriate client error without echoing the payload.
- [ ] Domain selection rejects wildcard, ambiguous, and unknown values and cannot mutate another domain's overlay.
- [ ] Invalid requests leave local progress unchanged.
- [ ] Route tests cover malformed JSON, wrong types, extra fields, boundaries, large bodies, and resolver edge cases.
