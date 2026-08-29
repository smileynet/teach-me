---
name: serve-workspace
description: "Run and manage teach-me's serve.py — start ONE server in the background (LAN-ready), poll readiness, hit the /api/map status endpoints, and stop cleanly. Trigger: serve, start the server, run serve.py, background server, serve on LAN, only one server, mark complete, /api/map, status endpoint, curl the server, stop the server, serve:bg, serve:restart."
metadata:
  type: protocol
  invocation: both
  practice: null
---

# Serve Workspace

Run `serve.py` (the FastAPI generation + map server that mounts a workspace at `/` and
project `/assets`) correctly from agent context. The launcher `tools/serve-bg.py` owns the
process logic; this skill is the decision layer + the API contract.

## Which command (decision table)

| Goal | Command | Notes |
|------|---------|-------|
| **Start a server for a task (default)** | `mise run serve:bg -- [--workspace P] [--lan] [--port N]` | Non-blocking; returns when ready, prints URLs, records PID. **Use this in any tool call.** |
| Stop it | `mise run serve:stop` (or `serve:bg -- --stop`) | Kills by PID file, cross-platform. |
| Is it up? | `python tools/serve-bg.py --status` | Reports PID + port state. |
| Restart (replace) | `mise run serve:restart -- [...]` | `--force`: stops the existing one, starts fresh. |
| Interactive human session | `mise run serve` / `serve:lan` | **Blocking** — never in an agent tool call. |
| Live-reload during code edits | `mise run serve:dev` | Blocking; auto-reloads on `tools/` changes. |

## The non-blocking rule (#1 trap)

`serve`, `serve:lan`, and raw `uvicorn.run` **block forever** — calling them in a shell
tool wastes the whole call on a timeout. For any agent-initiated server, use **`serve:bg`**.
It spawns detached (Windows `creationflags`, Unix `setsid`) per the Windows steering — do
NOT hand-roll `Start-Process -RedirectStandard*`/`-NoNewWindow` (those block; see
`project-conventions/references/windows.md`).

## Only ONE server at a time (enforced)

`serve:bg` refuses to start a second server:
- If a background server WE started is already alive (tracked via `.scratch/serve-bg.pid`,
  on **any** port) → refused. Use `--stop`, or `--force` to replace it.
- If the target `--port` is held by a **different** process (a foreground `serve`, a stray
  listener) → refused; it never clobbers something it doesn't own. Stop that process or
  pick another `--port`.

To guarantee a clean single instance: `mise run serve:restart -- [...]` (force-replace) or
`serve:stop` then `serve:bg`.

## LAN exposure

`--lan` binds `0.0.0.0` and prints `http://192.168.x.x:PORT` — reachable from other
devices. First LAN launch on Windows may need a Firewall inbound allow for the port. Always
give the full clickable URL (per AGENTS.md).

## Ports

Default `8787`. Use a distinct `--port` (e.g. `8799`) for throwaway validation so you don't
clobber a running dev server — same reasoning as `check-map-edges.py`'s dedicated `8791`.

## Status API contract (per-user overlay, #258)

Status is NOT in the committed graph — it lives in a gitignored `.user/status-overlay.json`
keyed by ULID node id, joined at runtime.

| Endpoint | Does |
|----------|------|
| `GET /api/map/{domain}` | Topics with overlay-joined status + derived `available_topics` / `next_suggestion`. |
| `GET /api/map/{domain}/{slug}/status` | Single topic status (absent overlay = `not-started`). |
| `POST /api/map/{domain}/{slug}/status` body `{"status":"complete\|in-progress\|not-started"}` | Writes the `.user/` overlay ONLY. Returns `{ok:true,...}`. |

**PowerShell gotcha:** inline `curl -d '{"status":"complete"}'` gets mangled. Use a file:
```
Set-Content .scratch/body.json '{"status":"complete"}' -NoNewline -Encoding ascii
curl.exe -s -X POST http://127.0.0.1:8799/api/map/oidc-rust/oidc-auth-flows/status \
  -H "Content-Type: application/json" --data "@.scratch/body.json"
```
Verify the write landed only in the overlay: `git check-ignore <ws>/.user/status-overlay.json`
returns the path (ignored), and `git status` shows no committed status change.

## Known gap — the "Mark complete" button (#264)

The lesson mark-complete button POSTs to `/api/map/**null**/{slug}/status` (404) because
`data-domain` isn't wired into lesson pages yet (tracked in #264). Until #264 lands,
validate the status endpoints with **curl (explicit domain)**, not the browser button.

## Browser-driven testing

For clicking through pages (mark-complete round-trip, component checks), dispatch the
**browser** specialist (see `browse-and-verify`) against a server you started with
`serve:bg` — don't load Playwright in the default agent.

## Cleanup discipline

Always `serve:stop` when done. The `.user/` overlay is gitignored and disposable (delete =
reset progress). Remove `.scratch/serve-bg.{log,pid}` if they linger.
