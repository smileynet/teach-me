---
id: "079"
title: "Feature: replace example workspaces — remove web-security, add OIDC-in-Rust"
status: done
priority: high
blocked_by: []
type: feature
---

# Feature: replace example workspaces

## What to do

### Remove
- `examples/web-security/` — delete entirely

### Replace roguelike-rust → OIDC in Rust
- Delete `examples/roguelike-rust/`
- Create `examples/oidc-rust/`
- Write MISSION.md: "How to implement OIDC in a Rust client/server app"
- Generate MAP.md with 5-7 topics (auth flows, token handling, middleware, testing, etc.)
- Generate 2 topic lessons + quizzes

### Expected result
```
examples/oidc-rust/
  MISSION.md
  RESOURCES.md
  maps/oidc-rust.MAP.md
  lessons/0001-*.html
  lessons/0002-*.html
  lessons/quiz/0001-*-quiz.html
  lessons/quiz/0002-*-quiz.html
  learning-records/questions/*.jsonl
```

## Validation

- `mise run verify` passes
- Playwright: navigate to OIDC example, verify lessons load and quiz works

## Resolution (2026-08-12)

TBD
