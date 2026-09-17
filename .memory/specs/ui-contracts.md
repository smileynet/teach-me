# UI & Content Contracts

Interface and implementation contracts for teach-me's page/asset system. These are specs
someone implements against — relocated from `CONTEXT.md` (ticket #254), which is a glossary
for term disambiguation only.

## Mask color (diagram cards)

Occluded label masks on diagram cards use slate gray `#585b70`. It is neutral against all
diagram layer colors (blue, amber, green). Never use amber for masks — it clashes with diagram
elements.

## MAP.md `domain` field

The `domain:` frontmatter field in a `MAP.md` MUST match the MAP.md filename (without the
`.MAP.md` suffix). The index page links to `{domain}-map.html`; a mismatch produces a 404.

## Preferences module

`assets/preferences.js` is the single source of truth for all user reading preferences (theme,
font, spacing, layout). It is signal-based, auto-persists to the `teach-me-prefs-v1` localStorage
key, and auto-applies CSS custom properties plus the `data-theme` attribute. It is not a
server-side settings store or config.

## Page shell

`assets/page-shell.js` is the implemented single entry point that orchestrates component
initialization on lesson pages (#127, shipped). It runs an ordered imperative init on
DOMContentLoaded — preferences → LayoutMode → CodeBlockToolbar → Glossary/inline quizzes →
LessonActions → TypographyPanel. It is not an SPA "app shell" or a framework.

Extension contract: a component exports a mount/init function, gets imported in
page-shell.js, and is called at the right position in `init()` — no HTML file changes.
There is no registry; ordering is explicit in the file.

The server-side twin is `tools/lib/page_template.py` (`_base_page`), the single source of
truth for page HTML shells: it emits the `<script type="module" src="…/page-shell.js">`
tag, the import map, the blocking `typography-prefs.js` (FOUC guard — must stay
synchronous/in-head), breadcrumbs, data islands, and the `lesson-actions-config` block.
Lesson/reference/quiz pages include the shell; map/index/resources pages opt out
(`include_page_shell=False`) and mount their own views.


## Map render test contract (`data-*` attributes, #261)

The map graph carries `data-*` attributes that are the contract `tools/check-map-edges.py`
asserts against — dropping them silently breaks the gate:

- `GraphView` edge `<path>` (in the caller's edge-layer SVG — `edge-layer` for the topic map,
  `im-edges` for the domain forest): `data-source`, `data-target` (node ids in the caller's
  key space — ULID for topics, slug for domains), `data-type` (`prereq`|`leads_to`|`related`
  |`parent`). Solid edges emit `stroke-dasharray="none"` (NOT `"0"`) — the gate keys on `none`.
- `TopicCard` root `.topic-card`: `data-topic-id` (the node ULID).
- `GraphView` canvas (class caller-owned — `dag-canvas` for the topic map, `im-canvas` for the
  domain forest): `data-render-complete="true"` and `data-edge-count` (set after dagre layout —
  the gate `waitForFunction`s on `data-render-complete`, never a sleep).

The gate is identity-first: rendered edges must match `load_map(MAP.md).edges` by
`(source, target, type)` + count (Tier 1), then endpoints must land on the correct
source/target cards (Tier 2). Keep these attributes when editing the map components.
