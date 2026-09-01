# 0017 — Do NOT unify the domain and topic derivations into a shared `derive_graph`

**Status:** accepted
**Date:** 2026-08-31

> A rejected-alternative record. During an architecture-deepening session we considered
> extracting a shared `derive_graph(nodes, edges, status_map)` from the two places that turn
> a committed graph + per-user status into rendered data. We deliberately did NOT — this ADR
> exists so a future session doesn't re-propose it. The line counts below were verified
> against the source (`domain_graph.py:83-99`, `generate_map_page.py:120-136`) and by two
> independent dispatched code-reviews.

## Context

teach-me renders a 4-level hierarchy: **aggregate index → domain map → topic → lesson**. Two
modules derive rendered data from the committed graph ⋈ per-user status:

- `tools/lib/domain_graph.py` `build_domain_graph` — **domains** as nodes. Joins a status
  map, computes per-domain completion **counts** (`total`/`complete`/`in_progress`), and
  projects `topic_ids` + a `demo_status` seed. Status is sourced from the committed demo
  fixture (`demo_status_map_for_map`, ADR-0016/#279).
- `tools/generate_map_page.py` `parse_map_md` — **topics** as nodes. Joins a status map
  (one line: `status_map.get(t.id, "not-started")`), then a SEPARATE, topic-only
  `compute_effective_status` promotes status from disk evidence (lesson/quiz/reference
  files). Status is sourced from the live `.user/` overlay.

They looked like the same "derive" and the deepening review's outcome #3 was "one derivation,
not per-level." So we scoped a pure `derive_graph(nodes, edges, status_map) → {nodes+status,
edges, stats}` (join + completion only; sourcing and disk-promotion stay per-caller).

## Decision

**Keep the two derivations separate. Do NOT extract a shared `derive_graph`.** The only
genuinely shared logic — completion counting — already lives in exactly ONE place (#276
localized it to `build_domain_graph`), and the topic path has no completion logic to share.

## Rationale (why extraction fails its own test)

1. **It's a pass-through, by measurement.** The domain join+completion is 3 comprehension
   lines; the topic "join" is 1 line and computes NO completion/stats. A `derive_graph`
   would be ~10 lines (core ~5), the domain caller would net ~0 lines shed, and the topic
   caller would net **negative** (a call + unpack to shed one `.get`). Ousterhout's deep-module
   test (small interface / much hidden behavior; zero pass-through methods) fails outright.
2. **No shared *knowledge*, only shared *shape*.** The functional-core research is explicit:
   a shared pure function must carry a rule that must change in all callers together. Here the
   domain level **aggregates** (fold over `topic_ids` → counts) and the topic level
   **annotates** (per-topic status, no counts). Different operations that merely rhyme —
   the "coincidentally identical / wrong abstraction" trap (Metz, Jovanović).
3. **Sourcing is deliberately different (ADR-0016/#279).** Domain = committed demo fixture;
   topic = live overlay + disk-evidence promotion. A shared derivation would pressure these
   back together or need a flag — re-opening a decision #279 settled on purpose.
4. **Node shapes diverge sharply.** Domain superset records carry `topic_ids`/`demo_status`;
   topic nodes are 8-field dicts (`slug`/`why`/`scope`/`prereqs`/…). A shared node contract
   would be a lowest-common-denominator both callers shape around — added coupling for no
   locality gain.

## Alternatives considered

- **(a) `derive_graph` = join + completion (the scoped proposal).** Rejected: pass-through
  (above). The 3 shared lines already live in one place; nothing to consolidate.
- **(b) `derive_graph` = join + completion + full ADR-0014 derived-quantity suite**
  (readiness / topological order / next-suggestion / backlinks). Rejected earlier in the
  session as **speculative generality**: those quantities have ONE consumer (the topic map);
  a domain forest never sequences, so the domain caller would carry (and be tested against)
  machinery it never renders.
- **(c) Keep both derivations (chosen).** The counts stay localized in `build_domain_graph`
  (#276); topic status + disk promotion stay in the map generator. Duplication is not the
  problem here — there is none to remove.

## Consequences

**Easier:**
- No lowest-common-denominator node contract; each level's record stays shaped for its view.
- The #279 status-sourcing split stays intact and un-blurred.
- No thin pass-through module to name, test, and maintain.

**Harder / accepted:**
- The two derivations remain textually similar at a glance; a future reader may re-notice the
  resemblance. This ADR is the answer: the resemblance is shape, not knowledge.
- IF a THIRD derivation appears that genuinely shares completion+sourcing (rule of three),
  revisit — but only when the shared logic is knowledge-bearing, not shape-bearing.

## Relationship to the client-side deepening

This ADR concerns the **server/Python derivation** seam only. The **client/JS renderer** seam
(the two dagre renderers `MapView` + `IteratedMapView`) is a SEPARATE, stronger candidate —
its shared core is a real 5-stage layout algorithm, not 3 comprehension lines — and is being
validated by a spike (unify into one `GraphView` with injected node rendering). The two seams
were deliberately judged independently; killing this one does not bear on that one.

## Related ADRs
- **ADR 0016** (#276) — localized the domain completion derivation to `build_domain_graph`;
  that localization is precisely why there is nothing left to share here.
- **ADR 0014** — derive-don't-store; the derived quantities alternative (b) would have hoisted
  belong to the topic level per its single-consumer reality.
