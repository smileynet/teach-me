---
id: "271"
title: "Index UX: add 'what's next' / primary-action guidance for first-time users"
status: done
blocked_by: []
priority: low
tags: ["platform"]
---

# Index primary-action guidance

## Why (found in UX audit, 2026-08-29)

The All Lessons index shows 5 domain cards with no orientation — a first-time user gets no
answer to "what do I do here / where do I start" (learning-UX principle #3: always-answered
"what's next", exactly one obvious primary CTA per screen). Cards are the only affordance.

## Chosen design (after research + code review, 2026-08-30)

Findings in `.scratch/research/firsttime-cta.md` + `.scratch/subagent-raw/271-*.md`.

**Key constraint the ticket didn't anticipate:** index counts are baked at generation time
from the gitignored `.user/` overlay (`generate_index_page.py:97-157`). On the shipped
`library/` (GitHub Pages) every domain is `complete:0 / inProgress:0` and stays so — no
client-side overlay read at index load, no regen route on serve.py. So the "continue" cue can
only fire on a LIVE served workspace after progress + regeneration; the public library always
shows the empty-state. The cue must therefore be data-driven off counts already in the island
(degrades gracefully), not a client fetch.

**Design — one line in `IndexView`, inserted between `.index-meta` (IndexView.js:71) and
`.domain-grid` (:73). Exactly ONE cue shows at a time** (research: never first-run + resume at
equal weight; one primary action per screen):

- **Empty state** (no domain has `inProgress`/`complete` > 0): first-time orientation, one
  benefit-led line pointing at the cards as the single obvious action ("New here? Pick a domain
  below to start — each opens a map of topics."). This is what the public library always shows.
- **Returning state** (some domain `inProgress > 0`, else a partially-complete domain): a single
  **resume affordance** promoted above the grid — "Continue where you left off → {title}" linking
  to that domain's `mapHref`. Becomes the dominant CTA; grid demotes to browsing.

**Scope: counts-based, no generator change.** `inProgress` already reaches `IndexView` but is
dead data today. Resume target = first domain with `inProgress > 0`. A "most-recently-touched"
target (via overlay `updated_at`) would need the generator to bake a `lastVisited` href — spun
out as a possible follow-up, NOT in this ticket.

**Also fold in a latent fix (same file):** the inline `DomainCard` ignores `domain.inProgress`
entirely (dead data). Surface it in the card stat line ("N to explore · M in progress"),
matching the sibling `DomainCard.js` used by the global map. Minor, consistent vocabulary.

## Acceptance criteria

- [x] Empty state: one clear first-time orientation line (points at the domain cards as the single action)
- [x] Returning state (progress exists): a single overlay-driven "Continue where you left off → {domain}" affordance linking to its map
- [x] Exactly ONE cue renders at a time (empty XOR resume); no banner stack — one line / one link
- [x] Inline DomainCard surfaces `inProgress` in its stat line (previously dead data)
- [x] `mise run verify` EXIT 0

## Verification (2026-08-30)

- Cue-selection logic fixtures (empty / in-progress / partial-complete / all-complete) + card
  stat text: all assertions PASS.
- Browser (aggregate `library/`, all-zero): PASS — `<p class="index-cue index-cue-start">`
  "New here? Pick a domain below to start — each one opens a map of topics." renders BETWEEN
  `.index-meta` and `.domain-grid`; no resume link; exactly one cue.
- Browser (iceberg served directly, 2/7 complete → partial): PASS — `<p class="index-cue
  index-cue-resume">` "Continue where you left off → Modern Data Analytics Stacks"; no
  orientation line; clicking it navigates to `data-analytics-map.html` (map loads). Exactly one cue.
- `mise run verify` → EXIT 0.

## Notes / scope decisions

- **Counts-based, no generator data change.** `inProgress` already reached IndexView (dead data);
  now consumed. Resume target = first in-progress domain, else first partially-complete.
- **CSS applied surgically to committed index pages, NOT via regeneration.** Regenerating would
  re-bake counts from the local (empty) overlay, clobbering committed demo progress
  (iceberg 2/7, godot 2/8, ink 3/8). Patched only the `.index-cue` CSS block; page-data untouched
  (verified: 0 count changes in the diff).
- On the public `library/` (GitHub Pages) counts are always 0, so it always shows the orientation
  line — correct empty-state behavior. Resume only fires on a live served workspace with progress.
- A "most-recently-touched" resume target (via overlay `updated_at`) would need the generator to
  bake a `lastVisited` href — deliberately out of scope; possible follow-up if valued.
- Observed one pre-existing client console error on a directly-served domain index (unrelated to
  the cue; render + navigation unaffected) — not introduced by this change.

## Validation

- Unit-render `IndexView` with three fixtures: all-zero → orientation line; one in-progress →
  resume link points at that domain; all-complete → no resume (affirmative or no cue). Assert
  exactly one cue.
- Browser: served index with empty overlay → orientation present; regenerate with an in-progress
  overlay → resume link appears at the right domain.
- `mise run verify` EXIT 0.
