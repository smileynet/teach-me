#!/usr/bin/env python3
"""Check that all expected artifacts exist for a topic in a workspace.

Reports which artifacts are present, missing, or incomplete.

Usage:
    python tools/check-topic-completeness.py --workspace examples/oidc-rust --topic oidc-auth-flows
    python tools/check-topic-completeness.py --workspace examples/workout-fundamentals --all
"""

import argparse
import json
import re
import sys
from pathlib import Path


def find_lesson(workspace: Path, topic_slug: str, lesson_file: str | None = None) -> Path | None:
    """Find a lesson file matching the topic slug or explicit filename."""
    if lesson_file:
        path = workspace / "lessons" / lesson_file
        if path.exists():
            return path
    for f in sorted(workspace.glob("lessons/*.html")):
        if topic_slug in f.stem and not f.stem.endswith("-map"):
            return f
    return None


def find_reference(workspace: Path, topic_slug: str) -> Path | None:
    """Find a reference file matching the topic slug."""
    for f in sorted(workspace.glob("reference/*.html")):
        if topic_slug in f.stem:
            return f
    return None


def find_quiz(workspace: Path, topic_slug: str) -> Path | None:
    """Find a quiz file matching the topic slug."""
    for f in sorted(workspace.glob("lessons/quiz/*.html")):
        if topic_slug in f.stem:
            return f
    return None


def check_lesson_features(lesson_path: Path) -> dict:
    """Check required features in a lesson file."""
    content = lesson_path.read_text(encoding="utf-8")
    return {
        "has_svg": 'role="img"' in content,
        "has_glossary_data": "glossary-data" in content,
        "has_term_spans": 'class="term"' in content,
        "has_lesson_actions": "lesson-actions.js" in content,
        "has_theme_toggle": "theme-toggle.js" in content,
        "has_exercise": "<details>" in content,
        "uses_css_vars_in_svg": "var(--svg-" in content if 'role="img"' in content else True,
        "no_hardcoded_hex_in_svg": not bool(re.search(
            r'(?:fill|stroke)="#[0-9a-fA-F]{6}"',
            # Only check inside SVG blocks
            "\n".join(re.findall(r'<svg.*?</svg>', content, re.DOTALL))
        )) if 'role="img"' in content else True,
    }


def check_quiz_features(quiz_path: Path) -> dict:
    """Check required features in a quiz file."""
    content = quiz_path.read_text(encoding="utf-8")
    cards = re.findall(r'class="card"', content)
    types = set(re.findall(r'class="card-type">(\w+)', content))
    return {
        "question_count": len(cards),
        "meets_minimum_5": len(cards) >= 5,
        "type_count": len(types),
        "meets_minimum_3_types": len(types) >= 3,
        "types_found": sorted(types),
    }


def check_sr_questions(workspace: Path, topic_slug: str) -> dict:
    """Check SR questions exist for this topic."""
    questions_dir = workspace / "learning-records" / "questions"
    if not questions_dir.exists():
        return {"count": 0, "has_questions": False}

    count = 0

    # Primary: count all valid cards in the topic's own JSONL file
    topic_file = questions_dir / f"{topic_slug}.jsonl"
    if topic_file.exists():
        for line in topic_file.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                json.loads(line)
                count += 1
            except (json.JSONDecodeError, KeyError):
                continue
    else:
        # Fallback: scan all files for lesson_id match (legacy behavior)
        for f in questions_dir.glob("*.jsonl"):
            for line in f.read_text(encoding="utf-8").splitlines():
                if not line.strip():
                    continue
                try:
                    q = json.loads(line)
                    if topic_slug in q.get("lesson_id", ""):
                        count += 1
                except (json.JSONDecodeError, KeyError):
                    continue

    return {"count": count, "has_questions": count > 0}


def check_topic(workspace: Path, topic_slug: str, lesson_file: str | None = None) -> dict:
    """Run all checks for one topic."""
    result = {"topic": topic_slug, "artifacts": {}, "features": {}, "status": "pass"}

    # Artifact existence
    lesson = find_lesson(workspace, topic_slug, lesson_file)
    reference = find_reference(workspace, topic_slug)
    quiz = find_quiz(workspace, topic_slug)

    result["artifacts"] = {
        "lesson": str(lesson.relative_to(workspace)) if lesson else None,
        "reference": str(reference.relative_to(workspace)) if reference else None,
        "quiz": str(quiz.relative_to(workspace)) if quiz else None,
    }

    missing = [k for k, v in result["artifacts"].items() if v is None]
    if missing:
        result["status"] = "fail"
        result["missing"] = missing

    # Feature checks
    if lesson:
        result["features"]["lesson"] = check_lesson_features(lesson)
        failures = [k for k, v in result["features"]["lesson"].items() if not v]
        if failures:
            result["status"] = "fail"
            result["features"]["lesson_failures"] = failures

    if quiz:
        result["features"]["quiz"] = check_quiz_features(quiz)
        if not result["features"]["quiz"]["meets_minimum_5"]:
            result["status"] = "fail"
        if not result["features"]["quiz"]["meets_minimum_3_types"]:
            result["status"] = "fail"

    # SR questions
    sr = check_sr_questions(workspace, topic_slug)
    result["features"]["sr_questions"] = sr
    if not sr["has_questions"]:
        result["status"] = "fail"

    return result


def get_topics_from_map(workspace: Path) -> list[dict]:
    """Extract topic slugs and metadata from MAP.md files in the workspace."""
    topics = []
    for map_file in workspace.glob("maps/*.MAP.md"):
        content = map_file.read_text(encoding="utf-8")
        # Find ### slug lines
        for match in re.finditer(r'^### (\S+)', content, re.MULTILINE):
            slug = match.group(1)
            # Find the status and lesson_file after this heading
            rest = content[match.end():]
            # Stop at next ### or end
            next_heading = re.search(r'^### ', rest, re.MULTILINE)
            section = rest[:next_heading.start()] if next_heading else rest

            status_match = re.search(r'\*\*status:\*\*\s*(\S+)', section)
            lesson_file_match = re.search(r'\*\*lesson_file:\*\*\s*(\S+)', section)

            if status_match and status_match.group(1) == "complete":
                topics.append({
                    "slug": slug,
                    "lesson_file": lesson_file_match.group(1) if lesson_file_match else None,
                })
    return topics


def main():
    parser = argparse.ArgumentParser(description="Check topic completeness")
    parser.add_argument("--workspace", required=True, help="Workspace root directory")
    parser.add_argument("--topic", help="Single topic slug to check")
    parser.add_argument("--all", action="store_true", help="Check all complete topics in MAP.md")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    workspace = Path(args.workspace)
    if not workspace.is_absolute():
        workspace = Path.cwd() / workspace

    if not workspace.exists():
        print(f"Error: workspace not found: {workspace}", file=sys.stderr)
        sys.exit(2)

    if not workspace.is_dir():
        print(f"Error: not a directory: {workspace}", file=sys.stderr)
        sys.exit(2)

    if args.topic:
        topics = [{"slug": args.topic, "lesson_file": None}]
    elif args.all:
        topics = get_topics_from_map(workspace)
        if not topics:
            print("No complete topics found in MAP.md")
            sys.exit(0)
    else:
        print("Provide --topic SLUG or --all")
        sys.exit(1)

    results = []
    for t in topics:
        result = check_topic(workspace, t["slug"], t.get("lesson_file"))
        results.append(result)

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        all_pass = True
        for r in results:
            icon = "✓" if r["status"] == "pass" else "✗"
            print(f"  {icon} {r['topic']}")

            if r.get("missing"):
                print(f"    Missing: {', '.join(r['missing'])}")
                all_pass = False

            if "lesson_failures" in r.get("features", {}):
                print(f"    Lesson issues: {', '.join(r['features']['lesson_failures'])}")
                all_pass = False

            quiz = r.get("features", {}).get("quiz", {})
            if quiz and not quiz.get("meets_minimum_5"):
                print(f"    Quiz: only {quiz['question_count']} questions (need 5+)")
                all_pass = False
            if quiz and not quiz.get("meets_minimum_3_types"):
                print(f"    Quiz: only {quiz['type_count']} types (need 3+)")
                all_pass = False

            sr = r.get("features", {}).get("sr_questions", {})
            if not sr.get("has_questions"):
                print(f"    SR: no questions found")
                all_pass = False

        print()
        if all_pass:
            print(f"✓ All {len(results)} topics complete")
        else:
            print(f"✗ Issues found")
            sys.exit(1)


if __name__ == "__main__":
    main()
