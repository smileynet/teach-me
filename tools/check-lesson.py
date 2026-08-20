#!/usr/bin/env python3
"""check-lesson.py — Mechanical lesson linter.

Enforces structural and convention compliance on lesson HTML files.
Check IDs match the lesson-validation skill (G2, G3, Q1, Q3, Q6, Q9, Q11, CF).

Usage:
    python tools/check-lesson.py --workspace examples/godot-gamedev --lesson lessons/0005-triplanar-mapping.html
    python tools/check-lesson.py --workspace examples/godot-gamedev --all
    python tools/check-lesson.py --workspace examples/godot-gamedev --all --json
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

# --- Result types ---

PASS = "PASS"
FAIL = "FAIL"
WARN = "WARN"
SKIP = "SKIP"


def result(check_id: str, status: str, message: str, line: int | None = None) -> dict:
    r = {"check": check_id, "status": status, "message": message}
    if line is not None:
        r["line"] = line
    return r


# --- Checks ---


def check_g2_template(html: str, lines: list[str]) -> list[dict]:
    """G2: Template compliance — required boilerplate elements."""
    results = []
    required = [
        ("DOCTYPE", "<!DOCTYPE html>"),
        ("style.css", "style.css"),
        ("page-shell.js", "page-shell.js"),
        ("breadcrumb nav", 'class="page-nav"'),
        ("importmap", '"importmap"'),
    ]
    for name, marker in required:
        if marker not in html:
            results.append(result("G2", FAIL, f"Missing: {name}"))
    if not results:
        results.append(result("G2", PASS, "Template compliance"))
    return results


def check_g3_code_files(html: str, workspace: Path, lesson_slug: str) -> list[dict]:
    """G3: Every data-file block has a corresponding file in reference/code/."""
    data_files = re.findall(r'data-file="([^"]+)"', html)
    # Deduplicate and exclude fragments
    unique_files = set()
    for match in re.finditer(r'<pre[^>]*data-file="([^"]+)"[^>]*>', html):
        full_tag = match.group(0)
        if 'data-mode="fragment"' not in full_tag:
            unique_files.add(match.group(1))

    if not unique_files:
        return [result("G3", SKIP, "No extractable data-file blocks")]

    code_dir = workspace / "reference" / "code" / lesson_slug
    missing = []
    for fname in sorted(unique_files):
        if not (code_dir / fname).exists():
            missing.append(fname)

    if missing:
        return [result("G3", FAIL, f"Missing files: {', '.join(missing)} (expected at {code_dir})")]
    return [result("G3", PASS, f"Code files ({len(unique_files)}/{len(unique_files)} present)")]


def check_q1_narrative(html: str, lines: list[str]) -> list[dict]:
    """Q1: No code blocks immediately after headings without prose between."""
    results = []
    # Pattern: </hN> followed by <pre> with only whitespace/comments between
    violations = []
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("<pre"):
            # Look backwards for the nearest non-empty, non-comment line
            for j in range(i - 1, max(i - 5, -1), -1):
                prev = lines[j].strip()
                if not prev or prev.startswith("<!--"):
                    continue
                if re.match(r"</h[23]>", prev) or re.match(r"<h[23][^>]*>.*</h[23]>", prev):
                    violations.append(i + 1)
                break

    if violations:
        for line_num in violations[:3]:  # Report first 3
            results.append(result("Q1", FAIL, f"<pre> follows heading with no prose", line=line_num))
    else:
        results.append(result("Q1", PASS, "Narrative framing OK"))
    return results


def check_q3_diff_blocks(html: str, lines: list[str]) -> list[dict]:
    """Q3: Blocks with colored diff spans should have data-mode='diff'."""
    results = []
    # Find <pre> blocks that contain --error or --success colored spans
    violations = []
    in_pre = False
    pre_start = 0
    pre_has_diff_spans = False
    pre_has_diff_mode = False

    for i, line in enumerate(lines):
        if "<pre" in line:
            in_pre = True
            pre_start = i + 1
            pre_has_diff_spans = False
            pre_has_diff_mode = 'data-mode="diff"' in line
        if in_pre:
            if "var(--error)" in line or "var(--success)" in line:
                pre_has_diff_spans = True
        if "</pre>" in line or "</code></pre>" in line:
            if in_pre and pre_has_diff_spans and not pre_has_diff_mode:
                violations.append(pre_start)
            in_pre = False

    if violations:
        for line_num in violations[:3]:
            results.append(result("Q3", WARN, f"Diff spans without data-mode=\"diff\"", line=line_num))
    else:
        results.append(result("Q3", PASS, "Diff blocks marked correctly"))
    return results


def check_q6_key_concept(html: str) -> list[dict]:
    """Q6: Key concept block present."""
    if "key-concept" in html:
        return [result("Q6", PASS, "Key concept block present")]
    return [result("Q6", FAIL, "Missing .key-concept block")]


def check_q9_svg_accessibility(html: str) -> list[dict]:
    """Q9: SVGs have role='img' and <title> child."""
    svgs = re.findall(r"<svg[^>]*>.*?</svg>", html, re.DOTALL)
    if not svgs:
        return [result("Q9", SKIP, "No SVGs in lesson")]

    violations = []
    for i, svg in enumerate(svgs):
        issues = []
        if 'role="img"' not in svg:
            issues.append("missing role=\"img\"")
        if "<title" not in svg:
            issues.append("missing <title>")
        if issues:
            violations.append(f"SVG {i+1}: {', '.join(issues)}")

    if violations:
        return [result("Q9", FAIL, "; ".join(violations))]
    return [result("Q9", PASS, f"SVG accessibility ({len(svgs)}/{len(svgs)} compliant)")]


def check_q11_nav_chain(workspace: Path, lesson_path: Path, html: str) -> list[dict]:
    """Q11: Previous lesson links forward to this lesson."""
    # Find this lesson's filename
    lesson_filename = lesson_path.name

    # Find all lesson files in the same directory
    lesson_dir = lesson_path.parent
    all_lessons = sorted(lesson_dir.glob("*.html"))
    all_lessons = [f for f in all_lessons if not f.name.endswith("-map.html") and f.name != "index.html"]

    # Find this lesson's position
    try:
        idx = [f.name for f in all_lessons].index(lesson_filename)
    except ValueError:
        return [result("Q11", SKIP, "Lesson not found in directory listing")]

    if idx == 0:
        return [result("Q11", SKIP, "First lesson — no previous to check")]

    # Check if previous lesson links to this one
    prev_lesson = all_lessons[idx - 1]
    prev_html = prev_lesson.read_text(encoding="utf-8")
    if lesson_filename in prev_html:
        return [result("Q11", PASS, f"Previous lesson ({prev_lesson.name}) links forward")]
    return [result("Q11", WARN, f"Previous lesson ({prev_lesson.name}) does not link to {lesson_filename}")]


def check_cf_code_files_section(html: str) -> list[dict]:
    """CF: If data-file blocks exist, lesson should have a Code Files section with download links."""
    # Check if there are extractable data-file blocks (not fragments)
    has_extractable = bool(re.search(r'<pre[^>]*data-file="[^"]*"(?:(?!data-mode="fragment")[^>])*>', html))

    if not has_extractable:
        return [result("CF", SKIP, "No extractable code blocks")]

    if ">Code Files</h2>" not in html and ">Code Files</h3>" not in html:
        return [result("CF", FAIL, "Has data-file blocks but no 'Code Files' section")]

    if "download>" not in html and 'download>' not in html:
        # Check for download attribute on links
        if ' download' not in html:
            return [result("CF", WARN, "Code Files section exists but no download links found")]

    return [result("CF", PASS, "Code Files section with download links")]


# --- Runner ---


def lint_lesson(lesson_path: Path, workspace: Path) -> list[dict]:
    """Run all checks on a single lesson."""
    html = lesson_path.read_text(encoding="utf-8")
    lines = html.split("\n")

    # Derive lesson slug from filename (strip NN- prefix and .html)
    slug = re.sub(r"^\d+-", "", lesson_path.stem)

    all_results = []
    all_results.extend(check_g2_template(html, lines))
    all_results.extend(check_g3_code_files(html, workspace, slug))
    all_results.extend(check_q1_narrative(html, lines))
    all_results.extend(check_q3_diff_blocks(html, lines))
    all_results.extend(check_q6_key_concept(html))
    all_results.extend(check_q9_svg_accessibility(html))
    all_results.extend(check_q11_nav_chain(workspace, lesson_path, html))
    all_results.extend(check_cf_code_files_section(html))

    return all_results


def print_results(lesson_name: str, results: list[dict], use_json: bool = False) -> bool:
    """Print results and return True if all pass (no FAIL)."""
    if use_json:
        print(json.dumps({"lesson": lesson_name, "results": results}, indent=2))
        return all(r["status"] != FAIL for r in results)

    print(f"\n=== check-lesson: {lesson_name} ===")
    counts = {PASS: 0, FAIL: 0, WARN: 0, SKIP: 0}
    for r in results:
        counts[r["status"]] += 1
        line_info = f" (line {r['line']})" if "line" in r else ""
        print(f"  {r['status']:4s} {r['check']:4s} {r['message']}{line_info}")

    print(f"\n  Result: {counts[PASS]} pass, {counts[FAIL]} fail, {counts[WARN]} warn, {counts[SKIP]} skip")
    return counts[FAIL] == 0


# --- CLI ---


def main() -> None:
    args = sys.argv[1:]
    if not args or "-h" in args or "--help" in args:
        print("Usage: python tools/check-lesson.py --workspace PATH [--lesson FILE | --all] [--json]")
        print("\nMechanical lesson linter. Check IDs match lesson-validation skill.")
        sys.exit(0)

    workspace = Path(".")
    lesson_file = None
    check_all = False
    use_json = False

    if "--workspace" in args:
        workspace = Path(args[args.index("--workspace") + 1])
    if "--lesson" in args:
        lesson_file = args[args.index("--lesson") + 1]
    if "--all" in args:
        check_all = True
    if "--json" in args:
        use_json = True

    if not workspace.exists():
        print(f"Error: workspace not found: {workspace}", file=sys.stderr)
        sys.exit(2)

    # Find lessons to check
    lessons_dir = workspace / "lessons"
    if not lessons_dir.exists():
        print(f"Error: no lessons/ directory in {workspace}", file=sys.stderr)
        sys.exit(2)

    if check_all:
        lessons = sorted(lessons_dir.rglob("*.html"))
        lessons = [f for f in lessons if not f.name.endswith("-map.html")
                   and f.name != "index.html"
                   and "quiz" not in str(f)]
    elif lesson_file:
        path = workspace / lesson_file if not Path(lesson_file).is_absolute() else Path(lesson_file)
        if not path.exists():
            # Try relative to lessons/
            path = lessons_dir / lesson_file
        if not path.exists():
            print(f"Error: lesson not found: {lesson_file}", file=sys.stderr)
            sys.exit(2)
        lessons = [path]
    else:
        print("Error: specify --lesson FILE or --all", file=sys.stderr)
        sys.exit(2)

    # Run checks
    all_pass = True
    for lesson_path in lessons:
        results = lint_lesson(lesson_path, workspace)
        passed = print_results(lesson_path.name, results, use_json)
        if not passed:
            all_pass = False

    sys.exit(0 if all_pass else 1)


if __name__ == "__main__":
    main()
