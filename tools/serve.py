"""
Minimal generation server — spawns subprocess, streams stdout via SSE.

Usage:
    cd teach-me && python tools/serve.py [--port 8787]

Endpoints:
    GET  /                          — static files from project root
    POST /api/generate              — start generation, returns {id, stream_url}
    GET  /api/generate/{id}/stream  — SSE stream of subprocess output
    POST /api/generate/{id}/cancel  — cancel a running generation
"""

from __future__ import annotations

import asyncio
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


@app.post("/api/generate", status_code=202)
async def start_generation(req: GenerateRequest) -> JSONResponse:
    task_id = uuid.uuid4().hex[:12]

    if req.long_mock:
        cmd = LONG_MOCK_CMD
    elif req.mock:
        cmd = MOCK_CMD
    else:
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
        cwd=str(PROJECT_ROOT),
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
    lessons_dir = PROJECT_ROOT / "lessons"
    if not lessons_dir.exists():
        return JSONResponse([])
    files = sorted(
        f.name for f in lessons_dir.iterdir()
        if f.suffix == ".html" and not f.name.startswith("index") and not f.name.endswith("-map.html")
    )
    return JSONResponse(files)


# Mount static files LAST (catch-all)
app.mount("/", StaticFiles(directory=str(PROJECT_ROOT), html=True), name="static")

# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn

    port = int(sys.argv[sys.argv.index("--port") + 1]) if "--port" in sys.argv else 8787
    print(f"Serving teach-me at http://localhost:{port}")
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
