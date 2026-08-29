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

`assets/page-shell.js` is a planned single entry point that orchestrates all component mounting on
lesson pages — components register with the shell rather than self-mounting. Not yet implemented
(ticket 127). It is not an SPA "app shell" or a framework.
