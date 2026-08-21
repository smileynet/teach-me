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
    elif (PROJECT_ROOT / "workspace").exists():
        ws = PROJECT_ROOT / "workspace"
    else:
        # Auto-create default workspace on first launch
        import subprocess as _sp

        print("First launch — creating default workspace...")
        _sp.run(
            ["bash", str(PROJECT_ROOT / "tools" / "init-workspace.sh"), "--default"],
            check=True,
        )
        ws = PROJECT_ROOT / "workspace"

    return host, port, ws


_HOST, _PORT, WORKSPACE = _parse_args()

MAPS_DIR = WORKSPACE / "maps"
if not MAPS_DIR.exists():
    # Fallback: look in the example workspace
    MAPS_DIR = PROJECT_ROOT / "examples" / "iceberg-workspace" / "maps"

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
    questions_dir = WORKSPACE / "learning-records" / "questions"
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
    """Return parsed MAP.md data for a domain."""
    from map_parser import load_map, validate, get_available_topics, get_next_suggestion

    candidates = list(MAPS_DIR.glob(f"*{domain}*MAP.md")) + list(MAPS_DIR.glob(f"{domain}*"))
    if not candidates:
        raise HTTPException(status_code=404, detail=f"No MAP.md found for domain '{domain}'")

    m = load_map(candidates[0])
    errors = validate(m)
    available = get_available_topics(m)
    suggestion = get_next_suggestion(m)

    return JSONResponse({
        "domain": m.domain,
        "description": m.description,
        "depth": m.depth,
        "parent": m.parent,
        "leads_to": [{"slug": lt.slug, "why": lt.why} for lt in m.leads_to],
        "topic_count": len(m.topics),
        "topics": [
            {"slug": t.slug, "title": t.title, "status": t.status,
             "scope": t.scope, "prereqs": t.prereqs, "lesson_file": t.lesson_file}
            for t in m.topics
        ],
        "validation_errors": errors,
        "available_topics": [t.slug for t in available],
        "next_suggestion": suggestion.slug if suggestion else None,
    })


class StatusUpdateRequest(BaseModel):
    status: str  # not-started | in-progress | complete


@app.get("/api/map/{domain}/{slug}/status")
async def get_topic_status(domain: str, slug: str) -> JSONResponse:
    """Get a topic's current status from its MAP.md file."""
    from map_parser import load_map

    candidates = list(MAPS_DIR.glob(f"*{domain}*MAP.md")) + list(MAPS_DIR.glob(f"{domain}*"))
    if not candidates:
        raise HTTPException(status_code=404, detail=f"No MAP.md found for domain '{domain}'")

    m = load_map(candidates[0])
    for t in m.topics:
        if t.slug == slug:
            return JSONResponse({"domain": domain, "slug": slug, "status": t.status})

    raise HTTPException(status_code=404, detail=f"Topic '{slug}' not found in domain '{domain}'")


@app.post("/api/map/{domain}/{slug}/status")
async def update_topic_status(domain: str, slug: str, req: StatusUpdateRequest) -> JSONResponse:
    """Update a topic's status in its MAP.md file."""
    from map_parser import update_status

    candidates = list(MAPS_DIR.glob(f"*{domain}*MAP.md")) + list(MAPS_DIR.glob(f"{domain}*"))
    if not candidates:
        raise HTTPException(status_code=404, detail=f"No MAP.md found for domain '{domain}'")

    try:
        update_status(candidates[0], slug, req.status)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return JSONResponse({"ok": True, "domain": domain, "slug": slug, "status": req.status})


# Mount static files: workspace content + project assets
# Serve workspace (lessons, quiz, etc.) and assets from project root
app.mount("/assets", StaticFiles(directory=str(PROJECT_ROOT / "assets")), name="assets")
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
