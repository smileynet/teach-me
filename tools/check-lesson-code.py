#!/usr/bin/env python3
"""check-lesson-code.py — compile the pasteable code blocks in lesson HTML (#231, #228 Part A).

Every `<pre data-file="X"><code>...</code></pre>` block in a lesson is a file the reader can
download and paste. This gate proves those files actually compile — catching the bug class #228
flagged: a fragment that names an undefined divert / has a syntax error looks fine in the browser
but breaks the moment the learner uses it.

How it works:
  1. Extract every `data-file` block from each lesson HTML (skip `data-mode="fragment"` — those are
     illustrations, not downloadable files).
  2. Group blocks by their `data-file` target and assemble them in document order (matches the file
     the learner downloads; catches cross-block references a per-block compile would miss).
  3. Reconstruct `data-mode="diff"` blocks to their post-diff (final) state before assembling.
  4. Validate each assembled file with the REAL toolchain, dispatched by extension:
       .ink                -> inklecate            (skip-guarded: inklecate_available)
       .py                 -> python -m py_compile  (always available)
       .gd / .gdshader     -> reported as SKIP here (needs Godot + a project context;
                              covered by the opt-in Godot gate, not core verify)

Language skip-guards keep core `verify` fast and dependency-light: a missing optional toolchain
is a SKIP (exit 0 contribution), never a failure.

Exit codes: 0 = all validated blocks pass (or skipped), 1 = a block failed to compile, 2 = setup error.

Usage:
    python tools/check-lesson-code.py [--lessons-glob GLOB] [--only EXT[,EXT...]]
"""

import html
import re
import subprocess
import sys
import tempfile
from pathlib import Path

# Windows cp1252 stdout would choke on the ✓/✗/… this prints (AGENTS.md).
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib.ink_compile import compile_source, inklecate_available, DEFAULT_INKLECATE

DEFAULT_LESSONS_GLOB = "examples/**/lessons/**/*.html"

# Match a whole <pre ...data-file="X"...> ... <code>BODY</code> ... </pre> block.
# DOTALL so BODY spans newlines; non-greedy so adjacent blocks don't merge.
BLOCK_RE = re.compile(
    r'<pre\b([^>]*\bdata-file="([^"]+)"[^>]*)>.*?<code>(.*?)</code>\s*</pre>',
    re.DOTALL,
)
DATA_MODE_RE = re.compile(r'data-mode="([^"]+)"')
# Diff markup: spans wrap added/removed lines and MAY straddle newlines, so we
# unwrap the span tags first (keeping inner text), THEN classify each physical line.
SPAN_OPEN_RE = re.compile(r'<span[^>]*>')
SPAN_CLOSE_RE = re.compile(r'</span>')


def reconstruct_diff(body: str) -> str:
    """Post-diff (final) state of a data-mode="diff" block.

    Order matters (per #231 review): unwrap spans BEFORE classifying lines (spans straddle
    newlines, so a leading '<' would misclassify), then html.unescape ONCE at the end
    (real code '<' is encoded as &lt;; span markup is unambiguous — strip markup first).
    """
    no_spans = SPAN_CLOSE_RE.sub("", SPAN_OPEN_RE.sub("", body))
    out = []
    for line in no_spans.split("\n"):
        if line.startswith(("---", "+++", "@@", "\\ ")):
            continue  # diff headers / "\ No newline at end of file"
        if line.startswith("-"):
            continue  # removed line — drop
        if line.startswith("+"):
            out.append(line[1:])  # added — strip the '+' marker
        elif line.startswith(" "):
            out.append(line[1:])  # context — strip the single-space gutter
        else:
            out.append(line)  # blank line or unmarked
    return html.unescape("\n".join(out))


def plain_body(body: str) -> str:
    """Post-state of a non-diff block: strip any markup spans, unescape once."""
    return html.unescape(SPAN_CLOSE_RE.sub("", SPAN_OPEN_RE.sub("", body)))


def extract_blocks(html_text: str) -> list[dict]:
    """Return non-fragment data-file blocks: {file, mode, source} in document order."""
    blocks = []
    for m in BLOCK_RE.finditer(html_text):
        pre_attrs, data_file, body = m.group(1), m.group(2), m.group(3)
        mode_m = DATA_MODE_RE.search(pre_attrs)
        mode = mode_m.group(1) if mode_m else "complete"
        if mode == "fragment":
            continue  # illustration, not a downloadable file
        source = reconstruct_diff(body) if mode == "diff" else plain_body(body)
        blocks.append({"file": data_file, "mode": mode, "source": source})
    return blocks


def assemble_by_file(blocks: list[dict]) -> dict[str, str]:
    """Group blocks by data-file, concatenate in document order (the downloaded file)."""
    files: dict[str, list[str]] = {}
    for b in blocks:
        files.setdefault(b["file"], []).append(b["source"].rstrip("\n"))
    return {name: "\n".join(parts) + "\n" for name, parts in files.items()}


def validate_ink(name: str, source: str) -> tuple[str, str]:
    if not inklecate_available(DEFAULT_INKLECATE):
        return ("SKIP", "inklecate not found")
    with tempfile.TemporaryDirectory(prefix="lesson-ink-") as tmp:
        ok, issues, _ = compile_source(source, DEFAULT_INKLECATE, tmp_dir=Path(tmp), stem=Path(name).stem)
    if ok:
        return ("PASS", "compiles")
    detail = "; ".join(f"L{i['line']}: {i['message']}" for i in issues) or "compile failed"
    return ("FAIL", detail[:300])


def validate_py(name: str, source: str) -> tuple[str, str]:
    with tempfile.TemporaryDirectory(prefix="lesson-py-") as tmp:
        f = Path(tmp) / Path(name).name
        f.write_text(source, encoding="utf-8")
        r = subprocess.run([sys.executable, "-m", "py_compile", str(f)],
                           capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode == 0:
        return ("PASS", "compiles")
    return ("FAIL", (r.stderr or r.stdout).strip()[:300])


# .gd/.gdshader need a Godot project context + headless import; covered by the
# opt-in Godot gate, not core verify (keeps verify Godot-free). Reported as SKIP.
def validate_godot(name: str, source: str) -> tuple[str, str]:
    return ("SKIP", "Godot compile-check is opt-in (not in core verify)")


VALIDATORS = {
    ".ink": validate_ink,
    ".py": validate_py,
    ".gd": validate_godot,
    ".gdshader": validate_godot,
}


def main() -> int:
    lessons_glob = DEFAULT_LESSONS_GLOB
    only_exts: set[str] | None = None
    args = sys.argv[1:]
    i = 0
    while i < len(args):
        if args[i] == "--lessons-glob" and i + 1 < len(args):
            lessons_glob = args[i + 1]; i += 2
        elif args[i] == "--only" and i + 1 < len(args):
            only_exts = {e if e.startswith(".") else "." + e for e in args[i + 1].split(",")}; i += 2
        else:
            print(f"Unknown arg: {args[i]}", file=sys.stderr); return 2

    root = Path(".")
    lesson_files = sorted(root.glob(lessons_glob))
    if not lesson_files:
        print(f"No lesson HTML matched {lessons_glob}")
        return 0

    fail = 0
    checked = skipped = 0
    print(f"Checking data-file code blocks in {len(lesson_files)} lesson(s)\n")
    for lesson in lesson_files:
        blocks = extract_blocks(lesson.read_text(encoding="utf-8", errors="replace"))
        if not blocks:
            continue
        assembled = assemble_by_file(blocks)
        for name, source in assembled.items():
            ext = Path(name).suffix
            if only_exts and ext not in only_exts:
                continue
            validator = VALIDATORS.get(ext)
            if validator is None:
                continue  # unknown extension — not our concern
            status, detail = validator(name, source)
            marker = {"PASS": "  [ok]", "FAIL": "  [XX]", "SKIP": "  [--]"}[status]
            rel = lesson.relative_to(root).as_posix()
            print(f"{marker} {rel} :: {name} ({detail})")
            if status == "FAIL":
                fail += 1
            elif status == "SKIP":
                skipped += 1
            else:
                checked += 1

    print(f"\nResults: {checked} compiled, {skipped} skipped, {fail} failed")
    if fail:
        print("FAILED (a downloadable code block does not compile)")
        return 1
    print("PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
