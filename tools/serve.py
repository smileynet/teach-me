"""
Minimal generation server — spawns subprocess, streams stdout via SSE.

Usage:
    cd teach-me && python tools/serve.py [--port 8787] [--workspace PATH] [--lan]

Endpoints:
    GET  /                          — static files from workspace root
    POST /api/generate              — start generation, returns {id, stream_url}
    GET  /api/generate/{id}/stream  — SSE stream of subprocess output
    POST /api/generate/{id}/cancel  — cancel a running generation
"""

from __future__ import annotations

import asyncio
import json as json_mod
import os
import re
import signal
import subprocess
import sys
import uuid
from pathlib import Path
from typing import AsyncGenerator

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# ---------------------------------------------------------------------------
# ANSI stripping
# ---------------------------------------------------------------------------

ANSI_RE = re.compile(r"\x1b\[\??[0-9;]*[a-zA-Z]")


def strip_ansi(text: str) -> str:
    return ANSI_RE.sub("", text)


# ---------------------------------------------------------------------------
# Phase detection patterns (from spike 058 findings)
# ---------------------------------------------------------------------------

PHASE_PATTERNS: list[tuple[re.Pattern, str]] = [
    (re.compile(r"\(using tool: (\w+)\)"), "tool:{0}"),
    (re.compile(r"^Creating: (.+)$"), "creating:{0}"),
    (re.compile(r"^ - Completed in [\d.]+s$"), "tool_done"),
    (re.compile(r"^> .+"), "responding"),
    (re.compile(r"^ [▸►] Time: (\d+)s$"), "complete"),
    (re.compile(r"^\+\s+\d+:"), "writing"),
]


def detect_phase(line: str) -> str | None:
    """Match a stripped line against known kiro-cli output patterns."""
    for pattern, phase_template in PHASE_PATTERNS:
        m = pattern.search(line)
        if m:
            return phase_template.format(*m.groups()) if m.groups() else phase_template
    return None


# ---------------------------------------------------------------------------
# Process registry
# ---------------------------------------------------------------------------


class GenerationTask:
    __slots__ = ("id", "proc", "lines", "phase", "done", "exit_code")

    def __init__(self, task_id: str, proc: subprocess.Popen):
        self.id = task_id
        self.proc = proc
        self.lines: list[str] = []
        self.phase: str = "started"
        self.done = False
        self.exit_code: int | None = None


TASKS: dict[str, GenerationTask] = {}

# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

app = FastAPI(title="teach-me generation server")

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Add tools/ to import path for map_parser
sys.path.insert(0, str(PROJECT_ROOT / "tools"))

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
        # static tree (see the library-root mount below) and MAPS_DIR is unused.
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

MAPS_DIR = WORKSPACE / "maps"
if not MAPS_DIR.exists():
    # Fallback: look in the example workspace
    MAPS_DIR = PROJECT_ROOT / "library" / "iceberg-workspace" / "maps"


def _overlay():
    """The per-user status overlay for the served workspace (root = maps' parent)."""
    from lib.overlay import Overlay

    return Overlay(MAPS_DIR.parent)

# Mock command for testing (simulates a 3-step generation)
MOCK_CMD = [
    "bash",
    "-c",
    'echo "[PHASE] Researching topic..." && sleep 2 '
    '&& echo "I\'ll share my reasoning process (using tool: thinking): analyzing..." '
    "&& sleep 1 "
    '&& echo " - Completed in 1.2s" '
    "&& sleep 1 "
    '&& echo "I\'ll create the following file: lessons/test.html (using tool: write)" '
    "&& sleep 2 "
    '&& echo "+    1: # Test Lesson" '
    '&& echo "+    2: " '
    '&& echo "+    3: Content here" '
    '&& echo "Creating: lessons/test.html" '
    '&& echo " - Completed in 0.1s" '
    "&& sleep 1 "
    '&& echo "> Done! Lesson written to lessons/test.html" '
    '&& echo " ▸ Time: 8s"',
]

LONG_MOCK_CMD = [
    "bash",
    "-c",
    'for i in $(seq 1 13); do echo "[STEP:$i/13] Working... ($((i * 10))s elapsed)"; sleep 10; done && echo " ▸ Time: 130s"',
]


class GenerateRequest(BaseModel):
    prompt: str = ""
    mock: bool = True  # Use mock command for testing
    long_mock: bool = False  # Use 130s mock for SSE stability testing


# Input validation
SAFE_PROMPT_RE = re.compile(r"^[\w\s&:,.'/()\-–—]+$", re.UNICODE)
MAX_PROMPT_LEN = 500


@app.post("/api/generate", status_code=202)
async def start_generation(req: GenerateRequest) -> JSONResponse:
    task_id = uuid.uuid4().hex[:12]

    if req.long_mock:
        cmd = LONG_MOCK_CMD
    elif req.mock:
        cmd = MOCK_CMD
    else:
        # Validate prompt
        if not req.prompt or len(req.prompt) > MAX_PROMPT_LEN:
            raise HTTPException(status_code=400, detail="Prompt required (max 500 chars)")
        if not SAFE_PROMPT_RE.match(req.prompt):
            raise HTTPException(status_code=400, detail="Prompt contains invalid characters")
        cmd = [
            "kiro-cli",
            "chat",
            "--no-interactive",
            "--trust-tools=read,write,glob,shell,code,grep",
            req.prompt,
        ]

    env = {**os.environ, "NO_COLOR": "1", "PYTHONUNBUFFERED": "1"}

    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        cwd=str(WORKSPACE),
        env=env,
        start_new_session=True,
    )

    task = GenerationTask(task_id, proc)
    TASKS[task_id] = task

    # Start background reader
    asyncio.get_event_loop().run_in_executor(None, _read_output, task)

    return JSONResponse(
        status_code=202,
        content={
            "id": task_id,
            "stream_url": f"/api/generate/{task_id}/stream",
        },
    )


def _read_output(task: GenerationTask) -> None:
    """Read subprocess stdout in a thread, populate task.lines."""
    assert task.proc.stdout is not None
    for raw_line in task.proc.stdout:
        clean = strip_ansi(raw_line.rstrip("\n"))
        if not clean:
            continue
        # Filter kiro-cli noise
        if "Checkpoint operation failed" in clean:
            continue
        phase = detect_phase(clean)
        if phase:
            task.phase = phase
        task.lines.append(clean)
    task.proc.wait()
    task.exit_code = task.proc.returncode
    task.done = True


@app.get("/api/generate/{task_id}/stream")
async def stream_generation(task_id: str) -> StreamingResponse:
    if task_id not in TASKS:
        raise HTTPException(status_code=404, detail="Task not found")

    return StreamingResponse(
        _sse_generator(TASKS[task_id]),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


async def _sse_generator(task: GenerationTask) -> AsyncGenerator[str, None]:
    """Yield SSE events as subprocess produces output."""
    cursor = 0
    heartbeat_interval = 5  # seconds
    elapsed = 0.0
    poll_interval = 0.1

    while not task.done:
        if cursor < len(task.lines):
            # Send all new lines
            while cursor < len(task.lines):
                line = task.lines[cursor]
                phase = detect_phase(line)
                event_type = "phase" if phase else "output"
                data = phase if phase else line
                yield f"event: {event_type}\ndata: {data}\n\n"
                cursor += 1
            elapsed = 0.0
        else:
            await asyncio.sleep(poll_interval)
            elapsed += poll_interval
            if elapsed >= heartbeat_interval:
                yield ": heartbeat\n\n"
                elapsed = 0.0

    # Drain remaining lines
    while cursor < len(task.lines):
        line = task.lines[cursor]
        phase = detect_phase(line)
        event_type = "phase" if phase else "output"
        data = phase if phase else line
        yield f"event: {event_type}\ndata: {data}\n\n"
        cursor += 1

    # Final event
    yield f"event: done\ndata: {{\"exit_code\": {task.exit_code}}}\n\n"


@app.post("/api/generate/{task_id}/cancel")
async def cancel_generation(task_id: str) -> JSONResponse:
    if task_id not in TASKS:
        raise HTTPException(status_code=404, detail="Task not found")

    task = TASKS[task_id]
    if task.done:
        return JSONResponse({"status": "already_done"})

    # Kill entire process group (clean shutdown per spike 058)
    try:
        os.killpg(os.getpgid(task.proc.pid), signal.SIGTERM)
    except (ProcessLookupError, OSError):
        pass

    return JSONResponse({"status": "cancelled"})


@app.get("/api/lessons")
async def list_lessons() -> JSONResponse:
    """Return list of HTML files in lessons/ for dynamic status detection."""
    lessons_dir = WORKSPACE / "lessons"
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
    from questions import questions_dir_for
    questions_dir = questions_dir_for(WORKSPACE)
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
    lessons_dir = WORKSPACE / "lessons"
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
    from map_parser import load_map, validate, get_available_topics, get_next_suggestion

    candidates = list(MAPS_DIR.glob(f"*{domain}*MAP.md")) + list(MAPS_DIR.glob(f"{domain}*"))
    if not candidates:
        raise HTTPException(status_code=404, detail=f"No MAP.md found for domain '{domain}'")

    m = load_map(candidates[0])
    errors = validate(m)
    status_map = _overlay().status_map()  # {node_id → status}; absent = not-started
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
    """Resolve (map_path, node_id) for a domain+slug, or raise 404."""
    from map_parser import load_map

    candidates = list(MAPS_DIR.glob(f"*{domain}*MAP.md")) + list(MAPS_DIR.glob(f"{domain}*"))
    if not candidates:
        raise HTTPException(status_code=404, detail=f"No MAP.md found for domain '{domain}'")
    m = load_map(candidates[0])
    for t in m.topics:
        if t.slug == slug:
            return candidates[0], t.id
    raise HTTPException(status_code=404, detail=f"Topic '{slug}' not found in domain '{domain}'")


@app.get("/api/map/{domain}/{slug}/status")
async def get_topic_status(domain: str, slug: str) -> JSONResponse:
    """Get a topic's current status from the per-user overlay (absent = not-started)."""
    _, node_id = _resolve_topic_id(domain, slug)
    rec = _overlay().get(node_id)
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

    return JSONResponse({"ok": True, "domain": domain, "slug": slug, "status": req.status})


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
_SERVING_MULTI_DOMAIN = not (WORKSPACE / "lessons").is_dir()


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


if _SERVING_MULTI_DOMAIN:
    # Domain-map / lesson pages emit bare `index.html` back-links (correct when the page
    # sits directly in a workspace's lessons/). Under a multi-domain root they'd resolve to
    # /{domain}/lessons/index.html (nonexistent). Normalize any nested `index.html` request
    # to the served-root index. Only active when serving a multi-domain tree — single-
    # workspace serving keeps its own per-workspace index untouched.
    @app.get("/{prefix:path}/index.html")
    async def _root_index(prefix: str):
        from fastapi.responses import FileResponse

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
