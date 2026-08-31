---
id: "282"
title: "Index cue matrix: empty→orientation + all-complete→no-resume via synthetic fixture"
status: open
blocked_by: []
tags: [platform]
---

# Index cue matrix: empty→orientation + all-complete→no-resume via synthetic fixture

## Context (deferred from #274, option A)

The #271 index orientation/resume cue has three states:
- **empty** (no progress) → orientation cue ("New here? Pick a domain…")
- **in-progress / partial** → resume cue ("Continue where you left off → {domain}")
- **all-complete** → no resume cue

`test-navigation.py` (#274) asserts the **resume** state — all 5 real library domains are
in-progress on disk, so that's the only state exercisable from the real library. The **empty**
and **all-complete** states cannot be produced from real domains:
- Empty: every library domain has authored lessons + a committed demo overlay (#278).
- All-complete: no domain has every topic complete.
- (And overlay counts re-bake to 0 on a clean checkout — so "empty" is actually what a clean
  CI sees, but the committed pages bake in-progress counts.)

So #274 covers resume only and deferred the other two states here.

## What to build

A **synthetic fixture** the nav suite can point at to exercise all three cue states, WITHOUT
polluting the real library:
- A throwaway scan dir (e.g. `.scratch/cue-fixture/` or a test-only workspace) with 2-3 tiny
  MAP.md domains + a committed-style `status-overlay.json` per state:
  - one domain with ZERO overlay entries → asserts orientation cue,
  - one domain with a partial overlay → asserts resume cue + destination,
  - one domain with ALL topics complete → asserts no resume cue.
- Generate the aggregate index over the fixture (`generate_index_page.py --scan-dir …`),
  serve it, and assert the cue for each state.
- OR drive the states client-side via `store.js` (`setTopicStatus`) if that's simpler than
  fixtures — decide during implementation.

Add these assertions to `test-navigation.py` (a `--fixture` mode) or a sibling suite.

## Acceptance criteria

- [ ] Empty-state fixture → orientation cue asserted
- [ ] Partial-state fixture → resume cue + click destination asserted
- [ ] All-complete fixture → no resume cue asserted
- [ ] Fixture is throwaway (gitignored scratch or test-only), does NOT touch the real library
- [ ] Runnable via `mise run test:nav` (fixture mode) or a documented sibling task

## References
- Cue logic: `assets/components/UnifiedView.js` `IndexCue` (resume = first domain with in-progress,
  else first partial-complete; else orientation). Markup: `.index-cue-resume a` / `.index-cue-start`.
- `tools/test-navigation.py` — `check_resume_cue()` asserts the resume state today; add a
  `--fixture` mode (or sibling) here. It self-serves `library/`; a fixture mode serves the fixture dir.
- Generate a fixture aggregate: `python tools/generate_index_page.py --scan-dir <fixture> --output <fixture>/index.html`.
- Overlay authoring: `tools/lib/overlay.py` schema (`{schema:1, overlay:{ULID:{status,updated_at}}}`);
  ULID ids come from each fixture MAP.md's `- **id:**` field. See #278's committed overlays for the exact shape.
- Client-drive alternative: `assets/components/store.js` `setTopicStatus(id, status)` (keyed by ULID).
- Context: `.memory/research/unified-graph-views/274-implementation-findings.md` (cue-matrix caveat);
  #271 (the cue feature); #274 resolution (why only resume is covered by the real library).
