---
id: "277"
title: "ADR: index and global-map are two views of one domain graph"
status: done
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

- [x] ADR written in `.memory/adr/` with Context / Decision / Options(+rejected, cited) / Consequences
- [x] Decision reconciled against the as-built #276 implementation (no plan-vs-reality drift)
- [x] Rejected alternatives (keep-separate, replace-index) recorded with the evidence that rejected them
- [x] Status set to Accepted (or Superseded/Rejected if the spike changed course)
- [x] CONTEXT.md updated if terminology shifted

## Validation

ADR reviewed (ideally by a fresh subagent as independent auditor per project practice) against
the merged code; no claim in the ADR contradicts the shipped #276 behavior.

## Resolution (2026-08-31)

Wrote `.memory/adr/0016-unified-domain-graph-views.md` (as-built record of the #275→#276
decision). Matches ADR 0014's house format; parented on ADR 0014 (the graph schema it presents),
relating to 0012/0015/0008/0005. Decision, three cited alternatives (keep-separate,
graph-as-landing rejected on #271 + prior art, chosen unified model), and observed consequences.

Named the pattern (Multiple Coordinated Views / single source of truth) and drew the line the
review flagged: the `mapView` localStorage preference is UI state, NOT the learner state ADR
0014 §B.6 keeps out of the browser. Recorded the two #276 deviations honestly — three node
representations (not a shared DomainCard; "grid retirement" scoped to the aggregate page, per
#281) and the Tree|Map toggle as a permitted distinct-view switch under Single-Axis steering.

Added 5 CONTEXT.md glossary entries disambiguating aggregate index / Tree+Map views / global-forest
map / domain map (none existed before).

**Independent auditor pass** (fresh subagent, `.scratch/research-277/audit.md`): 18 claims agree,
0 contradict, 3 policy/phrasing flags. Applied the two actionable flags (named `DomainCard.js`
explicitly in the crash rationale; corrected the verification note to cite the audit rather than
overstate "8/8"). Then flipped status proposed → **accepted**. No ADR claim contradicts shipped code.
