"""
Static + status server for a teach-me workspace.

Usage:
    cd teach-me && python tools/serve.py [--port 8787] [--workspace PATH] [--lan]

Serves the workspace tree (lessons, quizzes, maps) plus shared /assets, and exposes
read/write status endpoints backed by the per-user overlay:
    GET  /                                   — workspace static files (html=True)
    GET  /assets/... , /{prefix}/assets/...  — shared project assets (any depth, ADR-0015)
    GET  /api/lessons | /api/questions | /api/maps  — workspace inventory
    GET  /api/map/{domain}[/{slug}/status]   — parsed MAP.md + overlay status
    POST /api/map/{domain}/{slug}/status     — persist status to .user/ overlay
    GET  /api/overlay                        — full {node_id → status} map (#279)
"""

from __future__ import annotations

# Windows consoles default to cp1252; force UTF-8 so ✓/→/emoji glyphs don't crash (#265).
import sys as _sys
if hasattr(_sys.stdout, "reconfigure"):
    _sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(_sys.stderr, "reconfigure"):
    _sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import json as json_mod
import sys
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

app = FastAPI(title="teach-me workspace server")

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Add tools/ to import path for map_parser
sys.path.insert(0, str(PROJECT_ROOT / "tools"))
from lib.workspace_context import WorkspaceContext
from lib.overlay import Overlay, OverlayRecoveryError

# ---------------------------------------------------------------------------
# Arg parsing (early — needed before app mounts)
# ---------------------------------------------------------------------------

_KNOWN_FLAGS = {"--port", "--lan", "--workspace"}


def _parse_args() -> tuple[str, int, Path]:
    """Parse CLI args, return (host, port, workspace_path). Warns on unknown flags."""
    host = "127.0.0.1"
    port = 8787
    workspace: Path | None = None
    i = 1
    while i < len(sys.argv):
        arg = sys.argv[i]
        if arg == "--lan":
            host = "0.0.0.0"
        elif arg == "--port" and i + 1 < len(sys.argv):
            port = int(sys.argv[i + 1])
            i += 1
        elif arg == "--workspace" and i + 1 < len(sys.argv):
            workspace = Path(sys.argv[i + 1])
            i += 1
        elif arg.startswith("--"):
            print(f"⚠ Unknown flag: {arg} (known: {', '.join(sorted(_KNOWN_FLAGS))})")
            sys.exit(1)
        i += 1

    # Resolve workspace
    if workspace is not None:
        # Resolve relative to cwd, not project root
        resolved = Path.cwd() / workspace if not workspace.is_absolute() else workspace
        if not resolved.exists():
            # Try relative to project root
            resolved = PROJECT_ROOT / workspace
        if not resolved.exists():
            print(f"✗ Workspace not found: {workspace}")
            sys.exit(1)
        ws = resolved
    elif (PROJECT_ROOT / "workspace" / "lessons").is_dir():
        ws = PROJECT_ROOT / "workspace"
    elif (PROJECT_ROOT / "library").is_dir():
        # Fresh clone (no private workspace): serve the committed public library
        # (ADR-0012, supersedes ADR-0011's empty-workspace default). The library is a
        # multi-domain tree with no top-level lessons/maps — it's mounted at / as a
        # static tree and its domain maps are resolved from the workspace context.
        ws = PROJECT_ROOT / "library"
    else:
        # No workspace and no library — auto-create a default workspace (in-process).
        from init_workspace import init_workspace

        print("First launch - creating default workspace...")
        result = init_workspace(default=True)
        for w in result.get("warnings", []):
            print(f"  note: {w}")
        ws = PROJECT_ROOT / "workspace"
        if not (ws / "lessons").is_dir():
            print(f"! Workspace init did not complete: {result}")
            sys.exit(1)

    return host, port, ws


_HOST, _PORT, WORKSPACE = _parse_args()
try:
    CONTEXT = WorkspaceContext.from_root(WORKSPACE)
except ValueError as error:
    print(f"✗ {error}")
    sys.exit(1)


def _map_for_domain(domain: str):
    """Return the one parsed map whose canonical domain identity matches `domain`.

    Parse failures are isolated to their own file (#373): a malformed MAP.md is
    skipped, and when the requested domain is (by filename attribution) the broken
    one, the caller gets a 422 naming the file — healthy domains keep serving.
    """
    from map_parser import load_map

    matches = []
    broken: list[Path] = []
    for path in CONTEXT.maps:
        try:
            parsed = load_map(path)
        except (ValueError, OSError):
            broken.append(path)
            continue
        if parsed.domain == domain:
            matches.append((path, parsed))
    if len(matches) != 1:
        if not matches:
            ours = [p for p in broken if domain in p.stem or p.parent.parent.name == domain]
            if ours:
                names = ", ".join(str(p) for p in ours)
                raise HTTPException(
                    status_code=422,
                    detail=f"MAP.md for domain '{domain}' failed to parse: {names}",
                )
            detail = "No"
        else:
            detail = "Ambiguous"
        raise HTTPException(status_code=404, detail=f"{detail} MAP.md found for domain '{domain}'")
    return matches[0]


def _overlay():
    """The per-user status overlay for the served content root."""
    return Overlay(CONTEXT.overlay_root)


def _overlay_status_map() -> dict[str, str]:
    try:
        return _overlay().status_map()
    except OverlayRecoveryError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error

@app.get("/api/lessons")
async def list_lessons() -> JSONResponse:
    """Return list of HTML files in lessons/ for dynamic status detection."""
    lessons_dir = CONTEXT.lessons_dir
    if not lessons_dir.exists():
        return JSONResponse([])
    files = sorted(
        f.name for f in lessons_dir.iterdir()
        if f.suffix == ".html" and not f.name.startswith("index") and not f.name.endswith("-map.html")
    )
    return JSONResponse(files)


@app.get("/api/questions")
async def list_questions() -> JSONResponse:
    """Return map of lesson_ids that have questions (for complete state detection)."""
    questions_dir = CONTEXT.questions_dir
    if not questions_dir.exists():
        return JSONResponse({})
    lesson_ids: dict[str, int] = {}
    for f in questions_dir.iterdir():
        if f.suffix != ".jsonl":
            continue
        for line in f.read_text().splitlines():
            if not line.strip():
                continue
            try:
                q = json_mod.loads(line)
                lid = q.get("lesson_id", "")
                if lid:
                    lesson_ids[lid] = lesson_ids.get(lid, 0) + 1
            except (json_mod.JSONDecodeError, KeyError):
                continue
    return JSONResponse(lesson_ids)


@app.get("/api/maps")
async def list_maps() -> JSONResponse:
    """Return list of existing domain map pages (for leads-to linking)."""
    lessons_dir = CONTEXT.lessons_dir
    if not lessons_dir.exists():
        return JSONResponse([])
    maps = sorted(
        f.name for f in lessons_dir.iterdir()
        if f.name.endswith("-map.html")
    )
    return JSONResponse(maps)


@app.get("/api/map/{domain}")
async def get_map(domain: str) -> JSONResponse:
    """Return parsed MAP.md data for a domain, joined with the per-user status overlay."""
    from map_parser import validate, get_available_topics, get_next_suggestion

    _, m = _map_for_domain(domain)
    errors = validate(m)
    status_map = _overlay_status_map()  # {node_id → status}; absent = not-started
    available = get_available_topics(m, status_map)
    suggestion = get_next_suggestion(m, status_map)

    return JSONResponse({
        "domain": m.domain,
        "description": m.description,
        "depth": m.depth,
        "parent": m.parent,
        "leads_to": [{"slug": lt.slug, "why": lt.why} for lt in m.leads_to],
        "topic_count": len(m.topics),
        "topics": [
            {"slug": t.slug, "title": t.title,
             "status": status_map.get(t.id, "not-started"),
             "scope": t.scope, "prereqs": t.prereqs, "lesson_file": t.lesson_file}
            for t in m.topics
        ],
        "validation_errors": errors,
        "available_topics": [t.slug for t in available],
        "next_suggestion": suggestion.slug if suggestion else None,
    })


class StatusUpdateRequest(BaseModel):
    status: str  # not-started | in-progress | complete


def _resolve_topic_id(domain: str, slug: str):
    """Resolve (map_path, node_id) for a domain+slug, or raise 404.

    A topic whose ULID was minted at parse time gets a NEW id on every parse, so an
    overlay write keyed on it would silently never persist — reject loudly with the
    remediation instead (#373).
    """
    path, m = _map_for_domain(domain)
    for t in m.topics:
        if t.slug == slug:
            if t.ephemeral_id:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        f"Topic '{slug}' has no persisted ULID in {path.name} — its id is "
                        f"minted fresh on every parse, so progress writes would never "
                        f"persist. Run: python tools/migrate_map_ids.py --apply {path}"
                    ),
                )
            return path, t.id
    raise HTTPException(status_code=404, detail=f"Topic '{slug}' not found in domain '{domain}'")


@app.get("/api/map/{domain}/{slug}/status")
async def get_topic_status(domain: str, slug: str) -> JSONResponse:
    """Get a topic's current status from the per-user overlay (absent = not-started)."""
    _, node_id = _resolve_topic_id(domain, slug)
    try:
        rec = _overlay().get(node_id)
    except OverlayRecoveryError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
    status = rec["status"] if rec else "not-started"
    return JSONResponse({"domain": domain, "slug": slug, "status": status})


@app.post("/api/map/{domain}/{slug}/status")
async def update_topic_status(domain: str, slug: str, req: StatusUpdateRequest) -> JSONResponse:
    """Persist a topic's status to the per-user overlay ONLY (never the committed MAP.md)."""
    _, node_id = _resolve_topic_id(domain, slug)
    try:
        _overlay().set(node_id, req.status)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except OverlayRecoveryError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error

    return JSONResponse({"ok": True, "domain": domain, "slug": slug, "status": req.status})


@app.get("/api/overlay")
async def get_overlay() -> JSONResponse:
    """Return the whole per-user status overlay as a flat {node_id → status} map (#279).

    The aggregate landing page reads this at load to recompute per-domain progress counts
    from the user's OWN overlay, overriding the baked demo/no-JS floor in #page-data. This
    is a READ of the single-source-of-truth `.user/` file (ADR 0014 §B.6 permits "simple
    status read"), not a new browser store of learner state. Absent overlay → empty map →
    the demo floor stands. Static hosts (GH Pages) have no server, so this 404s there and
    the page keeps the baked demo counts (Option A: static = display-only demo)."""
    return JSONResponse({"overlay": _overlay_status_map()})


# Mount static files: workspace content + project assets
# Serve workspace (lessons, quiz, etc.) and assets from project root
app.mount("/assets", StaticFiles(directory=str(PROJECT_ROOT / "assets")), name="assets")


@app.get("/.user/{path:path}")
async def _block_private_overlay(path: str) -> JSONResponse:
    """The `.user/` overlay (status + SR progress) is PRIVATE — never browsable (#255).

    Registered before the catch-all workspace mount so it wins. Access goes through the
    API (e.g. /api/map, /api/questions), not raw file fetch.
    """
    raise HTTPException(status_code=404, detail="Not found")


# Unifying root (ADR-0015): pages use document-relative `../assets/...` correct for their
# committed location; the SERVER makes those resolve from any depth. When serving a
# multi-domain root (e.g. library/), a page at /{domain}/lessons/X.html requests
# /{domain}/assets/... — normalize any-depth `**/assets/{rest}` to the shared assets tree.
# Registered BEFORE the greedy `/` mount so it wins (mirrors the .user/ guard precedence).
@app.get("/{prefix:path}/assets/{rest:path}")
async def _nested_assets(prefix: str, rest: str):
    """Resolve `.../assets/<rest>` at ANY depth to PROJECT_ROOT/assets/<rest> (ADR-0015).

    `prefix` is intentionally ignored — assets are shared, not per-domain. Path-traversal
    guarded via resolve()+containment.
    """
    from fastapi.responses import FileResponse

    assets_root = (PROJECT_ROOT / "assets").resolve()
    target = (assets_root / rest).resolve()
    if assets_root != target and assets_root not in target.parents:
        raise HTTPException(status_code=404, detail="Not found")
    if not target.is_file():
        raise HTTPException(status_code=404, detail="Not found")
    return FileResponse(str(target))


if CONTEXT.multi_domain:
    # Domain-map / lesson pages emit bare `index.html` back-links (correct when the page
    # sits directly in a workspace's lessons/). Under a multi-domain root they'd resolve to
    # /{domain}/lessons/index.html (nonexistent). Normalize any nested `index.html` request
    # to the served-root index. Only active when serving a multi-domain tree — single-
    # workspace serving keeps its own per-workspace index untouched.
    @app.get("/{prefix:path}/index.html")
    async def _root_index(prefix: str):
        from fastapi.responses import FileResponse

        # #284: prefer the COMMITTED per-domain page when it exists on disk (mirrors the
        # deploy — pages.yml serves it as-is, synthesizing a redirect only when absent). This
        # keeps `mise run serve` consistent with GitHub Pages AND makes per-domain landings
        # locally reachable / QA-able. Path-traversal guarded via resolve()+containment.
        ws_root = WORKSPACE.resolve()
        candidate = (WORKSPACE / prefix / "index.html").resolve()
        within = candidate == ws_root or ws_root in candidate.parents
        if within and candidate.is_file() and candidate != (ws_root / "index.html"):
            return FileResponse(str(candidate))

        # Fallback: bare `index.html` back-links from domain-map / lesson pages that have NO
        # per-domain index resolve to the aggregate root index (the original normalizer intent).
        root_index = WORKSPACE / "index.html"
        if root_index.is_file():
            return FileResponse(str(root_index))
        raise HTTPException(status_code=404, detail="Not found")


app.mount("/", StaticFiles(directory=str(WORKSPACE), html=True), name="workspace")

# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def _get_lan_ip() -> str:
    """Get LAN IP address for network access."""
    import socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def _print_startup_info() -> None:
    """Print available URLs on startup."""
    lan_ip = _get_lan_ip()
    local_url = f"http://127.0.0.1:{_PORT}"
    lan_url = f"http://{lan_ip}:{_PORT}"

    print(f"\n  Workspace: {WORKSPACE}")
    print(f"  Local:     {local_url}")
    if _HOST == "0.0.0.0":
        print(f"  LAN:       {lan_url}")
    print()

    # Broken maps discovered at scan time (#373): name them up front so a per-request
    # 422 isn't the only signal. Their own domain 422s; other domains keep serving.
    from map_parser import load_map

    for path in CONTEXT.maps:
        try:
            load_map(path)
        except (ValueError, OSError) as error:
            print(f"  ⚠ Unparseable MAP.md (its domain will 422 until fixed): {path} — {error}")
    print()

    # Scan for lesson files
    lessons_dir = WORKSPACE / "lessons"
    if lessons_dir.exists():
        lessons = sorted(lessons_dir.rglob("*.html"))
        lessons = [f for f in lessons if not f.name.endswith("-map.html")
                   and f.name != "index.html" and "quiz" not in str(f)]
        if lessons:
            base = lan_url if _HOST == "0.0.0.0" else local_url
            print("  Lessons:")
            for lesson in lessons:
                rel = lesson.relative_to(WORKSPACE)
                print(f"    {base}/{rel.as_posix()}")
            print()


if __name__ == "__main__":
    import uvicorn

    _print_startup_info()
    print(f"  Starting server...\n")
    uvicorn.run(app, host=_HOST, port=_PORT, log_level="warning")
