---
id: "278"
title: "Commit a library demo status-overlay so regen is idempotent (unblocks #276)"
status: done
blocked_by: []
tags: ["platform"]
---

# Commit a library demo status-overlay so regen is idempotent (unblocks #276)

## Why (found in #275 spike review, 2026-08-30)

The committed library index pages ship real demo progress counts (verified: ink 3 complete /
5 in-progress `library/ink-godot/lessons/index.html:58`, iceberg 2 `:55`, godot 2 `:58`), but
those counts are baked at generation time from a **gitignored** `.user/status-overlay.json`
(`.gitignore:20` — `.user/` at any depth). There is NO committed overlay, and `pages.yml:143`
deletes `_site/library/.user`. So `overlay.status_map_for_map()` returns `{}` on any fresh
checkout/CI → **regenerating any index re-bakes all counts to 0**, clobbering the demo progress.

#271 dodged this by hand-patching CSS and never regenerating. #276 (unify index + global-map)
MUST regenerate — it merges the two generators — so this footgun must be removed FIRST. This
is the durable fix #276's "preserve demo counts" AC needs; a passive "don't regenerate" rule is
the weakest possible satisfaction.

## What to build

- **Un-gitignore the library overlay only.** Add a negation to `.gitignore` so
  `library/**/.user/status-overlay.json` IS committed while the live `workspace/.user/` and any
  real user's `.user/` stay ignored. (e.g. `!library/**/.user/` + `!library/**/.user/status-overlay.json`,
  keeping the broad `.user/` ignore for everything else.)
- **Author a demo overlay per library domain** that reproduces the currently-committed counts:
  `library/{domain}/.user/status-overlay.json` mapping the demo topics' ULID node ids →
  `{status, updated_at}`. Node ids are recoverable from each domain's MAP.md. Counts to match:
  ink-godot 3 complete + 5 in-progress, iceberg-workspace (data-analytics) 2 complete,
  godot-gamedev 2 complete (confirm exact ids/counts against the committed page-data).
- **Stop deleting the library overlay at deploy.** `pages.yml:143` currently
  `rm -rf _site/library/.user` — scope the private-overlay strip so it removes a REAL user's
  `.user/` but KEEPS the committed library demo overlay (or move the demo overlay somewhere the
  strip doesn't cover, matching whatever #276's generator reads).
- **Verify idempotent regen:** running `index:generate` / `map:global` on a clean checkout now
  re-bakes the SAME committed counts (not zeros).

## Acceptance criteria

- [x] `.gitignore` commits `library/**/.user/status-overlay.json`; live `workspace/.user/` + real user overlays still ignored
- [x] Demo overlay committed per library domain, reproducing the current committed counts (ink 3/5, iceberg 2, godot 2)
- [x] Regenerating a library index on a clean checkout yields the SAME counts (not 0) — idempotent
- [x] `pages.yml` no longer deletes the committed library demo overlay (private-user strip still works)
- [x] `mise run verify` EXIT 0

## Validation

On a clean checkout: `index:generate --scan-dir library/ink-godot` → page-data still shows
`complete:3, inProgress:5` (not zeros). Deploy assembly keeps the demo overlay but excludes a
real `.user/`. Blocks #276.

## Resolution (2026-08-31, commit 455236d)

**Approach A** (un-ignore + un-strip) — chosen over Approach B (a committed-fixture fallback in
`Overlay` mirroring `questions.py:_store_root_for`). A is the smaller, more localized change and
matches the ticket spec; B widens the "locked" `Overlay` interface for marginal benefit. B is
recorded as the considered alternative for #277's ADR.

- **.gitignore:** replaced bare `.user/` with `**/.user/*` (ignore CONTENTS, so git still
  descends and the negation can take effect) + `!library/**/.user/` + `!library/**/.user/status-overlay.json`.
  Empirically verified with `git check-ignore`: the demo overlay is committable while
  `workspace/.user/`, private lessons (`.user/lessons/`, #184), and SR data
  (`.user/learning-records/`) — including under `library/**/.user/` — all stay ignored. The
  negation is scoped to the exact filename, so a future naive edit can't accidentally re-include
  private content.
- **Overlays:** authored per domain with the current persisted ULID node ids recovered from each
  MAP.md — ink-godot (complete 01/02/03, in-progress 04–08), godot-gamedev (nodes-and-scenes,
  gdscript-fundamentals), iceberg-workspace/data-analytics (ingestion, storage-and-table-formats).
- **pages.yml:** scoped the deploy strip to `_site/.user` only (was `_site/library/.user _site/.user`).
  `cp -rL library/. _site/library/` (earlier in the job) lands the committed overlay; nothing removes it.
- **Idempotency proven:** regenerating each domain index + the aggregate re-bakes ink 3/5, godot 2,
  data-analytics 2 (oidc/workout 0) — not zeros. Did NOT commit the regenerated pages (they carry an
  unrelated `mapHref` drift, out of #278 scope — #276 will regenerate them).
- **Known non-blocker:** the runtime write-API (`POST /api/map/.../status` → `Overlay.set`) could
  mutate the committed overlay in place only if someone runs `serve --workspace library/{domain}`
  AND POSTs a status — not a normal fresh-clone flow. Treat the committed overlay as read-only fixture.
- `mise run verify` EXIT 0. Unblocks #276.
