---
id: "277"
title: "ADR: index and global-map are two views of one domain graph"
status: open
blocked_by: ["276"]
tags: ["platform"]
---

# ADR: index and global-map are two views of one domain graph

## Why (ordering note)

The DECISION — "index and global-map are two views over one domain-graph island, not two
pages" — is a hard-to-reverse architectural choice (merges two generators + two components,
retires a URL, changes the landing model). Per project conventions it warrants an ADR. This
ticket is LAST in the chain deliberately: the ADR is written/reviewed AFTER the spike (#275)
surfaces the real options and the implementation (#276) proves the approach, so the ADR records
a DECISION BACKED BY EVIDENCE, not a speculative plan. (If the spike says "keep separate", this
ticket still writes the ADR — documenting the rejected unification and why.)

## What to build

- Write `.memory/adr/NNNN-unified-domain-graph-views.md` capturing:
  - **Context:** the duplication (two generators re-deriving one domain list, two `.domain-card`
    defs), the #271 low-load-landing constraint, the "two views of one dataset" reframe.
  - **Decision:** one data island + list/map views (or the spike's alternative if it diverged).
  - **Options considered + rejected:** (a) keep two separate pages + cross-link only;
    (b) replace index WITH the global map as landing (rejected on #271 cognitive-load grounds);
    (c) the chosen unified two-view model. Cite the #275 spike evidence for each.
  - **Consequences:** generator unification, shared component, `global-map.html` URL fate,
    deploy simplification (one landing), single-axis-preferences steering interaction (view
    toggle as a permitted distinct-view switch), scale behavior.
- Review the ADR against the AS-BUILT #276 result — reconcile any drift between plan and
  implementation before marking accepted.
- Update `.memory/CONTEXT.md` if the unification introduces/retires any ambiguous term
  (e.g. "index" vs "landing" vs "forest map").

## Acceptance criteria

- [ ] ADR written in `.memory/adr/` with Context / Decision / Options(+rejected, cited) / Consequences
- [ ] Decision reconciled against the as-built #276 implementation (no plan-vs-reality drift)
- [ ] Rejected alternatives (keep-separate, replace-index) recorded with the evidence that rejected them
- [ ] Status set to Accepted (or Superseded/Rejected if the spike changed course)
- [ ] CONTEXT.md updated if terminology shifted

## Validation

ADR reviewed (ideally by a fresh subagent as independent auditor per project practice) against
the merged code; no claim in the ADR contradicts the shipped #276 behavior.
