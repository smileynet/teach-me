# Unified Graph Views — Research

Research feeding the index+global-map unification chain (#275 spike done → #276 impl →
#277 ADR; prereq #278). Promoted from `.scratch/` at #275 close (2026-08-31) because the
open #276/#277 tickets build on it. Spike prototypes + consolidated findings live in
`.scratch/spike-275/FINDINGS.md` (gitignored throwaway) — this dir holds the durable research.

## Decision (see #275 / #276)
Unified page, two views over one domain-graph island, **Tree | Map** toggle:
- Primary = indented tree (replaces flat list; ARIA tree; accessible; compact).
- Secondary = iterated dagre node-link map (fit-to-view, edge-type encoding + legend,
  hover-neighbor-highlight, islands sidebar).

## Files
| File | Feeds | Key takeaway |
|------|-------|--------------|
| viz-types.md | #276 | Sectioned grid / tidy-tree > dagre for a small nav forest; treemap/force/radial rejected |
| prior-art.md | #276/#277 | Auto-layout graphs praised-but-useless for nav (Obsidian/Khan); stable authored trees win |
| a11y-desktop.md | #276 | Indented tree = ARIA tree (accessible artifact, no fallback); desktop = columns not wide-scroll |
| view-toggle.md | #276 | Default list/tree; segmented control; persist localStorage, restore pre-paint |
| shared-data-views.md | #276 | One SSOT + derived projections (depth-0 filter = useMemo, not stored state) |
| graph-interactions.md | #276 | Ranked small-graph interactions: hover-neighbor-highlight + fit-to-view top; skip zoom/pan/drag |
| edge-node-encoding.md | #276 | SOLID=parent, DASHED=leads_to; arrowheads=direction; legend + color-not-alone |
| svg-panzoom-layout.md | #276 | Fit-to-view via CSS transform (cards stay HTML); per-component packing for dead space |
| vertical-graph-layout.md | #275 | TB (root-on-top) over LR for depth hierarchy (corrected the LR mis-call) |
| disconnected-nodes.md | #276 | Islands = ONE home (sidebar OR canvas tray, never both); don't inline-scatter |
