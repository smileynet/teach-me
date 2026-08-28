"""
tools/lib/ink_compile.py — Shared inklecate compile helper.

Single source of truth for invoking inklecate, consumed by:
- validate-ink.py (compile + lint, writes .ink.json next to source, uses -c)
- play-ink.py (compile to temp dir for runtime playthrough)
- check-lesson-code.py (fragment-compile, #228 Part A)

Extracted per ticket #228 finding: compile logic was duplicated across
validate-ink.py and play-ink.py with subtle drift (visit-count flag,
output location). Centralizing prevents a third copy.
"""

import os
import re
import subprocess
from pathlib import Path

# Ink constructs whose output varies per run. bink (blade-ink-rs) seeds its
# RNG from system entropy and exposes NO seeding API on Story, so any story
# using these cannot produce a stable golden transcript. Detected so the
# transcript tooling can skip them rather than emit a flapping fixture.
#   {~ a|b|c}   — shuffle (random alternative)
#   RANDOM(a,b) — random integer
#   SEED_RANDOM — (seeds inklecate's RNG, not bink's — still nondeterministic here)
NONDETERMINISM_PATTERNS = [
    re.compile(r"\{~"),               # shuffle alternative
    re.compile(r"\bRANDOM\s*\("),     # RANDOM(min,max)
    re.compile(r"\bSEED_RANDOM\b"),
]

# inklecate is an external, machine-specific binary (not installed by
# `mise run setup`). Overridable via the INKLECATE env var.
DEFAULT_INKLECATE = os.environ.get("INKLECATE", "inklecate")

# Parse inklecate output lines:
#   "ERROR: 'file.ink' line 7: message"
#   "WARNING: 'file.ink' line 7: message"
#   "ERROR: message"  (no file/line)
ISSUE_PATTERN = re.compile(
    r"^(ERROR|WARNING|AUTHOR):\s*(?:'([^']+)'\s+line\s+(\d+):\s*)?(.+)$",
    re.MULTILINE,
)


def inklecate_available(inklecate_path: str = DEFAULT_INKLECATE) -> bool:
    """
    True if inklecate is resolvable — either an existing file path OR a command
    name found on PATH (e.g. installed via mise `[tools]` github:inkle/ink).
    """
    import shutil
    return Path(inklecate_path).exists() or shutil.which(inklecate_path) is not None


def parse_issues(output: str, fallback_name: str) -> list[dict]:
    """Parse inklecate stdout/stderr into structured issue dicts."""
    issues = []
    for match in ISSUE_PATTERN.finditer(output):
        issues.append({
            "severity": match.group(1),
            "file": match.group(2) or fallback_name,
            "line": int(match.group(3)) if match.group(3) else 0,
            "message": match.group(4).strip(),
        })
    return issues


def compile_file(
    ink_file: Path,
    inklecate_path: str = DEFAULT_INKLECATE,
    output_json: Path | None = None,
    count_visits: bool = True,
) -> tuple[bool, list[dict], Path | None]:
    """
    Compile an .ink file to .ink.json.

    Args:
        ink_file: source .ink path.
        inklecate_path: path to the inklecate binary.
        output_json: where to write the compiled JSON. Defaults to
            ink_file with a .ink.json suffix (validate-ink.py behavior).
            Pass a temp-dir path for throwaway compiles (play-ink.py behavior).
        count_visits: emit `-c` so visit counts are tracked (needed for
            stories that branch on read counts; play-ink omits it).

    Returns:
        (success, issues, json_path). json_path is None on failure.
    """
    if output_json is None:
        output_json = ink_file.with_suffix(".ink.json")

    cmd = [inklecate_path]
    if count_visits:
        cmd.append("-c")
    cmd.extend(["-o", str(output_json), str(ink_file)])

    result = subprocess.run(
        cmd, capture_output=True, text=True, encoding="utf-8", errors="replace"
    )
    combined = (result.stdout or "") + (result.stderr or "")
    issues = parse_issues(combined, ink_file.name)
    success = result.returncode == 0
    return success, issues, (output_json if success else None)


def compile_source(
    source: str,
    inklecate_path: str = DEFAULT_INKLECATE,
    tmp_dir: Path | None = None,
    stem: str = "fragment",
    count_visits: bool = True,
) -> tuple[bool, list[dict], Path | None]:
    """
    Compile ink source given as a string (for fragment-compile, #228 Part A).

    Writes the source to a temp .ink file, compiles it, and returns the
    same tuple as compile_file. Caller owns tmp_dir cleanup; if tmp_dir is
    None the file is written beside the current working dir's temp space.
    """
    import tempfile

    if tmp_dir is None:
        tmp_dir = Path(tempfile.mkdtemp(prefix="ink-src-"))
    ink_file = tmp_dir / f"{stem}.ink"
    ink_file.write_text(source, encoding="utf-8")
    return compile_file(
        ink_file, inklecate_path, output_json=tmp_dir / f"{stem}.ink.json",
        count_visits=count_visits,
    )


def detect_nondeterminism(ink_source_path: Path) -> list[str]:
    """
    Return a list of nondeterministic constructs found in an .ink source.
    Empty list = safe for golden-transcript capture. Non-empty = the story's
    output varies per run (shuffle/RANDOM) and cannot be pinned via bink.
    """
    text = ink_source_path.read_text(encoding="utf-8", errors="replace")
    found = []
    for pat in NONDETERMINISM_PATTERNS:
        if pat.search(text):
            found.append(pat.pattern)
    return found

