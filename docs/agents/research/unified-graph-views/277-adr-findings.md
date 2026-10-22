# #277 ADR Findings (research + verification, 2026-08-31)

Synthesis of 4 subagents (ADR practice, unified-view prior art, claim verification, ADR/context
review). Full detail in `.scratch/research-277/`. The ADR is 0016.

## Corrections to the proposal

1. **"Grid retired" must be SCOPED (verify-claims #7).** The IndexView card-grid + its local
   DomainCard are retired only from the AGGREGATE landing page. They remain LIVE on per-domain
   `library/*/lessons/index.html` (and `DomainCard.js` still exists on disk). The ADR must say
   "the aggregate landing's card-grid is replaced" — NOT "the grid is retired" globally. (#281
   owns the per-domain decision.)

2. **The real parent is ADR 0014, not 0008/0005 (adr-context).** ADR 0014 (committed content
   graph + minimal overlay) defines the SCHEMA the views render (typed why-annotated edges
   prereq/leads_to/related, ULID node ids, derive-don't-store). ADR 0016 is the PRESENTATION
   layer atop 0014. Also relates to: 0012 (two-tier library the views span), 0015 (HARD
   CONSTRAINT: document-relative `../assets`, never root-relative — the unified page obeys it),
   0008 (a view toggle = Level-5 full Preact component), 0005 (Preact+Signals+dagre stack).

3. **Conflict to flag explicitly (adr-context).** ADR 0014 §B.6 says "no browser store" for
   LEARNER state (progress). The Tree|Map view PREFERENCE in localStorage is UI state — a
   DISTINCT thing. The ADR must draw this line so it doesn't read as violating 0014.

## Verified facts (all TRUE, cited — verify-claims.md)

1. ONE #page-data island {domains,edges,islands,stats,mission} (library/index.html:86; generate_index_page.py:74-88).
2. Shared derivation in domain_graph.build_domain_graph, no dup (domain_graph.py:66; global_map is a stub).
3. Tree DEFAULT, role=tree/treeitem/group + roving tabindex (preferences.js:33; IndentedTreeView.js:181,55,75,64).
4. Map dagre + fit-to-view (IteratedMapView.js:45,53,85-90; dagre loaded library/index.html:80).
5. global-map.html = redirect stub → index.html?view=map (library/global-map.html:5).
6. Toggle persists via mapView additive to DEFAULTS (preferences.js:19,33).
7. THREE node reps on the unified page, no shared DomainCard — TRUE (scope "grid retired" per #1 above).
8. stats count depth-0 only (generate_index_page.py:81; shipped domainCount:5).

## Pattern names + prior art (unified-view-pattern.md)

- Names this instantiates: **Multiple Coordinated Views** (Baldonado et al. — "Rule of
  Parsimony": add a view only when one can't do the job), **Model-View separation**, **Single
  Source of Truth**.
- Prior art (primary-nav choice): Obsidian (tree primary; graph "secondary to the main
  experience", disorienting for nav), MDN/Mintlify (sidebar tree is the spine), VS Code
  (Explorer tree primary, relationship graphs secondary). Tree-primary/graph-secondary is the
  established choice — hierarchy anchors (predictable wayfinding), graph augments (discovery).

## ADR-writing practice (adr-practice.md)

- Backfilled/as-built ADRs are legitimate (MS WAF endorses) but risk "form without substance":
  reconstruct context from EVIDENCE (spike #275, tickets, code), not memory; frame consequences
  as OBSERVED outcomes distinct from decision-time drivers; date honestly + note it's written
  post-implementation; cite the concrete cost that rejected each option.
- MUST capture: Status, Context (forces), Decision (active "We will"), Options + why-rejected,
  Consequences (trade-offs + what we're NOT doing). Append-only — never edit an accepted ADR.

## Format (adr-context #4)

Match ADR 0014: `# 0016 — Title`, inline `**Status:** proposed` + `**Date:**`,
Context → Decision → Alternatives (why rejected) → Consequences (Easier / Harder+risks) →
Implemented by / Follow-ups. Start status = **proposed**; flip to accepted after the
independent-auditor pass reconciles it against shipped code.

## CONTEXT.md (adr-context #2)

NONE of index/landing/forest-map/global-map/map-view are defined (all 20 entries are
teaching-domain terms). Add entries that disambiguate: the same page (`library/index.html`) is
the "aggregate index" / "landing" rendered as Tree; the "global/forest map" is that page's Map
VIEW; "domain map" is a per-domain `{domain}-map.html`. Passes the glossary gate (resolves which
meaning of confusable names).

## Steering verdict (adr-context #3)

Tree|Map toggle is a PERMITTED distinct-view switch (Single-Axis Preferences is scoped to the
reading panel + explicitly exempts "genuinely distinct page types"). Not a discouraged modal
toggle. Record this in Consequences.

## Validation plan
Write 0016 (proposed) → add CONTEXT.md entries → dispatch a fresh subagent auditor to check
every ADR claim against shipped code → flip to accepted only if clean.
