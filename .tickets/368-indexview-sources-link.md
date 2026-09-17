---
id: "368"
title: "Dead Sources link on per-domain index pages"
status: open
blocked_by: []
tags: ["ux", "curriculum", "nav"]
---

# Dead Sources link on per-domain index pages

## Intent

A learner on a per-domain index page should never be offered a link that 404s.

## Context (verified 2026-09-17, UX audit + source check)

`assets/components/IndexView.js:109` renders `<a href="resources.html">Sources</a>`
whenever `mission.why` is set — but no `library/*/lessons/resources.html` exists
anywhere on disk. Observed 404s on `/gltf-format/lessons/index.html` and
`/ink-godot/lessons/index.html` (single-domain IndexView pages whose page-data carries
mission context); any domain with `mission.why` is affected. Confirmed on the assembled
`_site` (GitHub Pages model) 2026-09-17: also renders on the new `world-models` and
`generative-media-pipelines` domain indexes — blast radius is 4 domains and grows with
every mission-bearing scaffold.

Fix options to choose from when picking up: emit the link only when a resources page
actually exists (probe like the quiz HEAD probe, or pass a flag from the generator),
link to the workspace `RESOURCES.md`-derived page if one is generated, or drop the
affordance.

## Acceptance criteria

- [ ] No per-domain index page renders a link that resolves to 404
- [ ] Domains that genuinely have a sources/resources page still link to it
- [ ] `mise run verify` exits 0
