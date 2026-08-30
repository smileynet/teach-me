#!/usr/bin/env python3
"""Check that all expected artifacts exist for a topic in a workspace.

Reports which artifacts are present, missing, or incomplete.

Usage:
    python tools/check-topic-completeness.py --workspace library/oidc-rust --topic oidc-auth-flows
    python tools/check-topic-completeness.py --workspace library/workout-fundamentals --all
"""

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from questions import questions_dir_for


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
    questions_dir = questions_dir_for(workspace)
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


def check_concept_coverage(workspace: Path, topic_slug: str, lesson_path: Path) -> dict:
    """Check concept coverage: do extracted concepts appear in glossary/questions?

    Requires extract_concepts + chunk_text (gated behind --concepts flag to avoid
    forcing networkx+yake dependency on simple runs).

    Returns dict with coverage percentage and gap list.
    """
    from extract_concepts import extract_concepts_from_html, _normalize_term

    # Extract concepts from the lesson
    result = extract_concepts_from_html(lesson_path, top_n=10)
    if not result.concepts:
        return {"coverage": 1.0, "total": 0, "covered": 0, "gaps": []}

    top_concepts = result.concepts[:10]
    concept_terms = {_normalize_term(c.term) for c in top_concepts}

    # Check glossary-data coverage
    lesson_content = lesson_path.read_text(encoding="utf-8")
    glossary_match = re.search(
        r'<script\s+type="application/json"\s+id="glossary-data">\s*(\{.*?\})\s*</script>',
        lesson_content, re.DOTALL,
    )
    glossary_terms = set()
    if glossary_match:
        try:
            glossary = json.loads(glossary_match.group(1))
            glossary_terms = {_normalize_term(k) for k in glossary.keys()}
        except json.JSONDecodeError:
            pass

    # Check term spans in lesson
    term_spans = set()
    for match in re.finditer(r'class="term"[^>]*data-term="([^"]*)"', lesson_content):
        term_spans.add(_normalize_term(match.group(1)))
    # Also check inline <dfn> tags
    for match in re.finditer(r'<dfn[^>]*>(.*?)</dfn>', lesson_content):
        term_spans.add(_normalize_term(match.group(1)))

    # Check SR questions
    question_terms = set()
    questions_dir = questions_dir_for(workspace)
    topic_file = questions_dir / f"{topic_slug}.jsonl"
    if topic_file.exists():
        for line in topic_file.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                q = json.loads(line)
                prompt = q.get("prompt", "").lower()
                for term in concept_terms:
                    if term in prompt:
                        question_terms.add(term)
            except (json.JSONDecodeError, KeyError):
                continue

    # Compute coverage
    all_covered = glossary_terms | term_spans | question_terms
    covered = concept_terms & all_covered
    gaps = concept_terms - all_covered

    coverage = len(covered) / len(concept_terms) if concept_terms else 1.0

    return {
        "coverage": round(coverage, 2),
        "total": len(concept_terms),
        "covered": len(covered),
        "gaps": sorted(gaps),
        "covered_by_glossary": sorted(concept_terms & glossary_terms),
        "covered_by_questions": sorted(concept_terms & question_terms),
    }


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
    """Extract topics the user has marked `complete` in the per-user overlay (#258).

    Status is no longer in the committed MAP.md — it lives in the gitignored overlay
    keyed by ULID node id. We parse each MAP.md for the graph (slug→id, lesson_file),
    then keep only topics whose overlay status is `complete`.
    """
    try:
        from tools.map_parser import load_map
        from tools.lib.overlay import Overlay
    except ModuleNotFoundError:
        from map_parser import load_map  # type: ignore[no-redef]
        from lib.overlay import Overlay  # type: ignore[no-redef]

    status_map = Overlay(workspace).status_map()
    topics = []
    for map_file in workspace.glob("maps/*.MAP.md"):
        dm = load_map(map_file)
        for t in dm.topics:
            if status_map.get(t.id) == "complete":
                topics.append({"slug": t.slug, "lesson_file": t.lesson_file})
    return topics


def main():
    parser = argparse.ArgumentParser(description="Check topic completeness")
    parser.add_argument("--workspace", required=True, help="Workspace root directory")
    parser.add_argument("--topic", help="Single topic slug to check")
    parser.add_argument("--all", action="store_true", help="Check all complete topics in MAP.md")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--concepts", action="store_true", help="Also check concept coverage (requires yake+networkx)")
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

        # Optional concept coverage check
        if args.concepts and result["artifacts"].get("lesson"):
            lesson_path = workspace / result["artifacts"]["lesson"]
            if lesson_path.exists():
                try:
                    coverage = check_concept_coverage(workspace, t["slug"], lesson_path)
                    result["features"]["concept_coverage"] = coverage
                except Exception as e:
                    result["features"]["concept_coverage"] = {"error": str(e)}

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

            cc = r.get("features", {}).get("concept_coverage", {})
            if cc and "error" not in cc:
                if cc.get("gaps"):
                    print(f"    Concepts: {cc['coverage']:.0%} covered ({cc['covered']}/{cc['total']}), gaps: {', '.join(cc['gaps'][:5])}")
                elif cc.get("total", 0) > 0:
                    print(f"    Concepts: {cc['coverage']:.0%} covered ({cc['covered']}/{cc['total']}) ✓")

        print()
        if all_pass:
            print(f"✓ All {len(results)} topics complete")
        else:
            print(f"✗ Issues found")
            sys.exit(1)


if __name__ == "__main__":
    main()
