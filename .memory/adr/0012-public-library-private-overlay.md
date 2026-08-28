# 0012 — Public topic library (committed) with a private per-user overlay

**Status:** accepted
**Date:** 2026-08-28

## Context

The project's content model has been inconsistent, and two "done" decisions now
contradict the direction we want.

- **ADR-adjacent #071 (done)** made `workspace/` the gitignored home for *all*
  user content — lessons, maps, quizzes, reference docs, learning records — and
  kept `examples/` as a handful of committed *demos*. Under this model, every
  lesson a user generates is local-only unless force-added; the repo ships only
  the example fixtures.
- **#245 / ADR 0011 (done)** deepened that model: `serve.py` auto-creates a
  gitignored `workspace/` on first launch and serves from it. A fresh clone
  therefore serves an *empty* workspace — the first-run experience shows no
  content (the concrete frustration that surfaced 2026-08-28: a fresh clone had
  nothing to serve, and the ink-godot lessons were only reachable by pointing
  serve.py at `examples/ink-godot`).
- Two open tickets (**#183** "Shared lesson library with local-only user state",
  **#184** "Optional private lessons") already describe the *opposite* model —
  lessons as committed, contributable content with local-only user state — and
  #183 explicitly says it "inverts the current architecture." They have been
  blocked/unactioned because the inversion was never formally decided.

The product intent (owner, 2026-08-28): **the repo ships a growing, shared
library of public topics that everyone gets on clone; contributing new topics
back is the encouraged default; users may optionally keep private topics that
never get committed.** Private is the opt-in escape hatch, not the norm.

A related cleanup the same day anchored `.gitignore`'s `workspace/` → `/workspace/`
and removed a bare `lessons/` rule that was silently ignoring `examples/*/lessons/`
— an incidental step toward this model (committed example lessons are now
first-class, glob-visible, and need no `git add -f`).

## Decision

Adopt a **two-tier content model**:

1. **Public topic library — committed, the default.** The topic library lives in
   the repo and is versioned. **Today's `examples/` directory is renamed to
   `library/` and promoted to be that library** — the workspaces within it stop
   being "demos" and become the shipped, growing set of public topics
   (godot-gamedev, iceberg, ink-godot, oidc-rust, workout-fundamentals, and future
   additions). Generating a new topic produces committable files under `library/`,
   ready to PR/push. Contribution is the encouraged path.

2. **Private overlay — gitignored, opt-in.** A user may mark a topic (or lesson)
   private. Private content is written to the gitignored `.user/` directory and
   never committed. It still integrates with navigation/maps at render time but is
   invisible to git and to other users. This is #184's mechanism, generalized from
   "private lessons" to "private topics."

3. **User *state* is always local.** Completion, SR review progress, and
   preferences are per-user and gitignored regardless of whether the topic they
   describe is public or private (this is #183's local-state half, unchanged).

This **supersedes**:
- the "all user content lives in gitignored `workspace/`" part of #071, and
- the "auto-create and serve an empty `workspace/` on first launch" behavior from
  #245 / ADR 0011. First launch should serve the committed public library, not an
  empty private workspace. (ADR 0011's *implementation* — pure-Python, in-process
  scaffolding, no bash — remains valid and is reused; only *what gets scaffolded
  and served by default* changes.)

It **is implemented by** the existing tickets, which will be re-scoped to match:
- **#183** — public library is committed under `library/{domain}/`; user state is
  local. Includes the `examples/` → `library/` rename (a git `mv` plus updates to
  serve.py, mise tasks, map_parser paths, README, and AGENTS.md references).
- **#184** — private overlay (`.user/`), now at topic granularity, blocked by #183.
- Likely **blocked_by #198** (cross-workspace index) for the "serve the whole
  library, not one workspace at a time" piece.

### Decided (locked 2026-08-28)

- **Rename** `examples/` → `library/` (not kept as `examples/`, not `topics/`).
  Signals it is the shipped library, not throwaway demos.
- **Private path** is `.user/` (gitignored). Its manifest/discovery mechanism is
  a #184 implementation detail, but the path itself is fixed here.

### Deferred (owned elsewhere)

- serve.py multi-workspace serving — owned by #198.

## Consequences

**Easier:**
- Fresh clone serves real content immediately — the first-run experience shows the
  public library instead of an empty page.
- Contribution has a natural on-ramp: generated topics land committable by default,
  matching the "encourage contributing back" goal.
- The 2026-08-28 `.gitignore` anchoring is retroactively coherent — committed
  example lessons are exactly the public library this ADR blesses.
- #183/#184 stop contradicting #071 — there's now a decided model they implement.

**Harder / risks:**
- **Reverses a `done` decision.** #071 and ADR 0011's serve default must be
  explicitly updated; AGENTS.md's "workspace/ is THE live workspace, gitignored,
  auto-created on first serve" contract (lines 8, 26, 56) is now wrong and must be
  rewritten. Until that doc + serve.py change lands, the repo is mid-migration and
  the two models coexist confusingly.
- **Privacy is now a user responsibility.** With committable-by-default, a user
  could accidentally commit a personal/work-specific topic. The private path must
  be discoverable and the default must fail safe (e.g., clear prompts, and never
  auto-commit — commits stay explicit per git-safety).
- **serve.py serves one workspace at a time (#198).** "Serve the whole library"
  isn't possible until #198; interim behavior (serve a chosen topic, or an index)
  must be specified in #183.
- **Migration for existing users.** Anyone with real content in a local
  `workspace/` needs a documented path (keep it as the private overlay, or promote
  selected topics to the library). #183's last AC already calls for this.

## Follow-ups

- Re-scope #183 and #184 to reference this ADR; set #183 to supersede #071's
  content-location model and to own the `examples/` → `library/` rename.
- The rename touches: `git mv examples library`, serve.py default/paths, mise
  tasks (`serve`, `maps:regenerate`, `index:generate`), `map_parser` path
  assumptions, README example links, and AGENTS.md references throughout.
- Rewrite the AGENTS.md workspace contract (lines 8, 26, 56) once #183 lands.
- Update serve.py first-launch default (currently ADR 0011) to serve the library.
