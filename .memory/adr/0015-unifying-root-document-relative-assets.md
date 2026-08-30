# ADR 0015: Unifying Site Root — Document-Relative Assets, Not Root-Relative

## Status

Accepted (2026-08-30)

## Context

Pages reference shared assets with **document-relative** paths (`../assets/style.css`,
`../../assets/…` for deeper pages) computed at generate time as `prefix = "../" * depth`
(`tools/lib/page_template.py`). The correct `../` count depends on how deep the page sits
under whatever is mounted at `/`.

This has been a recurring wound — patched six times in six places:

- **#163** — mount `/assets` at project root so `../assets` resolves (workaround for the
  missing invariant).
- **#229** — 218 false link-check failures because `library/*/assets` symlinks are Windows
  text stubs, not directories; added `verify-links._resolve_via_assets_mount` to *simulate*
  the mount.
- **#230** — quiz depth-2 assumptions broke at depth-3; made generation depth-aware.
- **#242** — `check-lesson` had to reuse the mount-resolution logic for images.
- **#261** — the map-edge gate FALSELY passed because `../assets` 404'd (dagre never loaded).
- **#198** — the `examples/`→`library/` rename put pages at `{domain}/lessons/…` (variable
  depth); index/global-map link-targets 404, and served-from-library-root, the pages'
  `../assets` resolves to `/{domain}/assets/…` → 404, so maps never render.

The root cause is **not** relative paths — it is the **absence of a unifying root with a
consistent page depth**. The library rename introduced *variable* depth
(`{domain}/lessons/…` vs `lessons/…` vs `{domain}/lessons/quiz/…`).

The tempting fix was to go **root-relative** (`/assets/…`, `/index.html`) — depth-independent,
one canonical reference. Research (2026-08-30, `.scratch/research/root-relative-migration.md`,
`base-tag-vs-alternatives.md`) showed this is a trap for THIS project:

- teach-me deploys to a GitHub **project page** (`{user}.github.io/teach-me/`, #112). Root-
  relative `/assets` resolves to `{user}.github.io/assets` (repo segment skipped) → 404.
- The only fix that keeps root-relative is `<base href="/{repo}/">`, which **silently breaks
  every in-page `#fragment` anchor, SVG `url(#id)` reference, form action, and JS-built URL**
  — and lesson pages are anchor- and SVG-heavy. That trades the depth-bug class for a worse,
  quieter anchor/SVG-bug class, plus a mandatory build-time injection step.

## Decision

**Keep document-relative asset/nav paths. Provide a UNIFYING ROOT at serve/assembly time
instead of encoding it into the pages. Do NOT migrate to root-relative + `<base>`.**

Concretely, the unifying root is provided by two mechanisms, per serve context — the pages
are byte-identical in both:

1. **Dynamic serving (`serve.py`)** — when serving a multi-domain root (e.g. `library/`),
   serve.py NORMALIZES any-depth requests to the shared root: a route maps
   `**/assets/{rest}` → `PROJECT_ROOT/assets/{rest}`, and `**/index.html` (+ domain-map
   back-links) → the served-root index, registered BEFORE the greedy `/` mount (mirrors the
   existing `/.user/` guard precedence). Document-relative `../assets` then resolves from any
   depth. (#198)

2. **Static deploy (`_site/` for GitHub Pages, #112)** — the assembly step lays out the
   tree so each page's document-relative `../assets` resolves within `_site/` (shared assets
   at the depth the pages expect). No `<base>`, no per-page prefix injection.

The invariant this ADR establishes: **a page's asset/nav paths are document-relative and
correct for its committed location; the serving context (dev server route-normalize, or
static assembly layout) is responsible for making that location's relative paths resolve —
NOT the page.**

## Alternatives Considered

| Alternative | Why rejected |
|-------------|-------------|
| Root-relative (`/assets`) + `<base href="/{repo}/">` | `<base>` silently breaks in-page `#fragment` anchors, SVG `url(#id)`, JS/form URLs — anchor/SVG-heavy lessons. Needs build-time base injection. Worse, quieter bug class. |
| Root-relative + base-path generator config (Vite/Jekyll `base`) | Only rewrites tool-controlled asset/script tags; MISSES plain `<a href>` nav links. Couples to a generator we don't use. |
| Regenerate all 75 pages to `depth+1` for library | Just moves the breakage: fixes library-root, breaks single-workspace + standalone `--workspace library/{domain}` serving (they need depth-1). Depth is build-time; correct value is serve-time. |
| Deploy as a user/org page at `/` (no subpath) | Would make root-relative free, but requires a dedicated `{user}.github.io` repo or a custom domain — a hosting change out of scope. Revisit if the deploy target changes. |

## Consequences

- **Easier:** the depth-bug class disappears without touching page content. New page types /
  nesting depths need no per-page path math — the server/assembly root absorbs it. Multi-
  domain serving from `library/` works. No anchor/SVG/fragment breakage. Works from a simple
  HTTP server (ADR 0003's "no build step" holds).
- **Retired workarounds:** the `library/*/assets` git symlink stubs (Windows text stubs) are
  deleted; `verify-links._resolve_via_assets_mount` becomes the honest mount-resolver, not a
  simulation of a broken invariant.
- **New obligation on the static deploy (#112):** the `_site/` assembly MUST reproduce the
  depth relationship (shared assets reachable via the pages' `../assets`). The current Pages
  workflow is stale (assembles nonexistent `examples/*/`, ships only `docs/index.html`) and
  must be fixed to assemble `library/` at consistent depth — tracked separately.
- **Constraint recorded:** do NOT introduce root-relative (`/…`) asset or nav paths in
  generated pages; a future contributor "simplifying" to `/assets` would reintroduce the
  project-page 404 + force `<base>`. If the deploy target ever becomes a root/user page or
  custom domain, this ADR should be revisited (root-relative becomes viable then).
- **Supersedes** the ad-hoc depth handling rationale in #163/#229/#230/#242/#261 by naming
  the invariant; complements ADR 0003 (shared asset contract) and ADR 0012 (library default).
