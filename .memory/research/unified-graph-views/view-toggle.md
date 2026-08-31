# Research: LIST ↔ GRAPH/MAP View Toggle over the Same Dataset

## Summary

Default first-time users to the **list/card view**, not the graph — a list is System-1 legible with near-zero orientation cost, whereas a node-graph landing forces effortful System-2 processing and risks "hairball" overload before the user knows what they're looking at. Persist the user's chosen view in `localStorage` and restore it on load, but always **validate the saved value against a hardcoded fallback** (a renamed/removed view must not break the page) and apply it before paint to avoid a flash. Architecturally, keep **one source of truth for the data** and swap only the renderer (list vs. graph consume the same model), so the two views never diverge.

## Details

### Which view to default to (first-time users)
- **Default to the simpler, lower-load view (list/cards).** Dashboards are read by "an active brain trying to make new connections quickly." Good design leverages Kahneman's **System 1** (automatic, <250 ms pre-attentive pattern recognition); poor design forces **System 2** (deliberate analysis). A list of labelled rows is System-1 friendly for "what am I looking at?"; a raw network graph demands System-2 decoding first. [browserlondon]
- **Working memory holds only ~4–7 chunks.** A graph landing that dumps all nodes/edges at once exceeds this and produces measurable cognitive tax (pupil dilation, slower time-to-insight, lower tool adoption — cited 40–60% first-year adoption when tools feel effortful). [browserlondon]
- **Graphs overwhelm when shown "everything everywhere all at once."** The three canonical failure modes on a cold graph are **hairballs** (too many connections), **snowstorms** (too few/disconnected), and **starbursts** (one over-connected node dominates). Users "are usually interested in the most important entities... not in seeing everything." So a graph is a poor first impression; earn it after the user opts in. [cambridge-intelligence]
- **Match default to audience.** UX guidance: default to the view the *majority* first-time user needs; offer the toggle for the minority. If two distinct user groups exist (analysts want the graph, casual users want the list), a visible view switcher lets each self-select rather than baking in one group's preference. [ux.stackexchange 85181]

### Avoiding cognitive overload when the graph *is* shown
- **Progressive disclosure / detail-on-demand** — reveal graph complexity through zoom, filtering, and clustering rather than rendering the full network immediately. [cambridge-intelligence]
- **Onboarding & tooltips** for unfamiliar graph interactions; follow established gestures (pinch-zoom, drag-pan) so the graph doesn't need a manual. [cambridge-intelligence]
- **Node grouping / combos, smart label truncation, size+color hierarchy** to keep the graph readable once entered. [cambridge-intelligence]

### Persisting the choice (localStorage)
- **Pattern:** on toggle, `localStorage.setItem('viewMode', view)`; on load, read it, verify the target renderer/DOM node exists, else fall back to a hardcoded default (`list`). "Never trust saved values — always verify the element exists... keep a hardcoded fallback too." [hashnode]
- **Apply before paint to avoid FOUC.** Run the restore at script-load time (a synchronous head script), not inside `DOMContentLoaded`, or the default view flashes before switching. (Mirrors this repo's own `typography-prefs.js` FOUC rule.) [hashnode; AGENTS.md]
- **Storage choice:** `localStorage` persists across sessions and browser restarts — right for a durable "preferred view." Caveat: it is **not available during SSR**; for server-rendered defaults use a cookie so the first server render matches. For a static/client-only page, `localStorage` is sufficient. [SO 78623374]
- **Content-switcher, not a toggle-switch, for the control.** Grid/list (and by extension list/graph) is a *binary view switch* → use a **segmented control / content switcher**, not an on/off toggle switch (toggles are for state/settings, not for choosing between two renderings of the same data). [ux.stackexchange 148693]

### Single source of data, multiple renderers
- **One authoritative owner of the data; views observe it.** Single Source of Truth: "each piece of data has exactly one authoritative owner. Other components observe that owner rather than holding their own copy." Both the list and the graph render from the *same* model, so switching views never shows stale or divergent data. [codepath SSOT]
- **Same dataset, different lenses is a recognized pattern.** Toggling between e.g. "Impact Analysis" (graph) and "Alerts List" views over the *same network* "helps users understand the same data in different ways" — the value is complementary perspectives on one dataset, not two datasets. [cambridge-intelligence]
- **Choose the format by the question:** graphs for relationships, lists/tables for scanning/lookup, maps for location. A single view can offer multiple lenses when each adds insight. [cambridge-intelligence]

### Practical recommendation for a list↔map/graph dashboard
1. Land first-time users on the **list/card view** (fast orientation, low load).
2. Offer a **segmented control** (List | Graph) — visible, labelled with icons + text.
3. On switch, persist `viewMode` to `localStorage`; on load, restore it with a validated hardcoded `list` fallback, applied pre-paint.
4. Render both views from **one shared data model** (SSOT) so they can't diverge.
5. In the graph view, use **progressive disclosure** (start filtered/clustered, expand on demand) to prevent hairball overload.

## Sources

- [The Cognitive Cost of Dashboard Design (System 1 vs 2, working-memory limits, time-to-aha)](https://browserlondon.medium.com/the-cognitive-cost-of-dashboard-design-data-visualisation-is-a-neuroscience-problem-a71f95cdc9b4) — Browser London, Nov 2025. [L5:reported]
- [Graph visualization UX: Designing intuitive data experiences (hairballs/snowstorms/starbursts, progressive disclosure, same-data multiple views)](https://www.cambridge-intelligence.com/blog/designing-intuitive-data-experiences-with-graph-visualizations/) — Cambridge Intelligence, Jun 2025. [L4:established]
- [Making Your SPA Remember State with localStorage — 3 Patterns and Their Pitfalls (view persistence, validate-with-fallback, FOUC)](https://ai-agent-eng.hashnode.dev/making-your-spa-remember-state-with-localstorage-3-patterns-and-their-pitfalls.md) — Hashnode. [L6:reported]
- [Single Source of Truth (SSOT) — Architecture of Android Apps wiki](https://github.com/codepath/android_guides/wiki/Architecture-of-Android-Apps) — CodePath. [L4:established]
- [Segmented control vs toggle switch (content switcher for binary views like grid/list)](https://ux.stackexchange.com/questions/148693/segmented-control-vs-toggle-switch) — UX StackExchange (cites Carbon Design System guidance). [L5:reported]
- [Navigating and Examining Chart Data (toggle/dropdown/View menu; default per majority audience)](https://ux.stackexchange.com/questions/85181/navigating-and-examining-chart-data) — UX StackExchange. [L6:reported]
- [Using NextJS cookies to remember user preferences (localStorage not available during SSR; cookie for first server render)](https://stackoverflow.com/questions/78623374/using-nextjs-cookies-in-order-to-remember-user-preferences) — Stack Overflow. [L6:reported]
- [Switch Between Grid & List Views in Angular (state + CSS/component-tree coordination for a reusable view toggle)](https://briantree.se/how-to-build-a-flexible-reusable-view-mode-toggle-component-in-angular/) — Briantree. [L6:reported]
