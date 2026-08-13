"""Tests for tools/map_parser.py."""

import tempfile
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent))

from map_parser import (
    DomainMap, Topic, load_map, validate,
    get_available_topics, get_next_suggestion, update_status,
)

EXAMPLES_DIR = Path(__file__).parent.parent / "examples"
DATA_ANALYTICS_MAP = EXAMPLES_DIR / "iceberg-workspace" / "maps" / "data-analytics.MAP.md"
GODOT_MAP = EXAMPLES_DIR / "godot-gamedev" / "maps" / "godot-gamedev.MAP.md"


# ---------------------------------------------------------------------------
# Parsing tests
# ---------------------------------------------------------------------------

def test_load_data_analytics():
    m = load_map(DATA_ANALYTICS_MAP)
    assert m.domain == "data-analytics"
    assert m.depth == 0
    assert m.parent is None
    assert any(lt.slug == "streaming-architectures" for lt in m.leads_to)
    assert len(m.leads_to) == 5
    # Check that why is populated (new format)
    sa = next(lt for lt in m.leads_to if lt.slug == "streaming-architectures")
    assert "real-time" in sa.why.lower() or "Real-time" in sa.why
    assert "deliberate pipeline" in m.orientation
    assert len(m.topics) == 7

    # Check a specific topic
    t = m.topic_by_slug("storage-and-table-formats")
    assert t is not None
    assert t.title == "Storage & Open Table Formats"
    assert t.status == "complete"
    assert t.prereqs == ["ingestion"]
    assert t.scope == "deep"


def test_load_godot():
    m = load_map(GODOT_MAP)
    assert m.domain == "godot-gamedev"
    assert len(m.topics) == 8
    assert m.topic_by_slug("nodes-and-scenes").prereqs == []
    assert "gdscript-fundamentals" in m.topic_by_slug("2d-game-mechanics").prereqs


def test_load_missing_file():
    try:
        load_map("/nonexistent/path.md")
        assert False, "Should have raised FileNotFoundError"
    except FileNotFoundError:
        pass


def test_load_no_frontmatter():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write("# No frontmatter\n\nJust content.\n")
        f.flush()
        try:
            load_map(f.name)
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "frontmatter" in str(e).lower()


# ---------------------------------------------------------------------------
# Validation tests
# ---------------------------------------------------------------------------

def test_validate_good_maps():
    for path in (DATA_ANALYTICS_MAP, GODOT_MAP):
        m = load_map(path)
        errors = validate(m)
        assert errors == [], f"{path.name} has errors: {errors}"


def test_validate_too_many_topics():
    m = DomainMap(
        domain="test", description="", depth=0, parent=None,
        leads_to=[], orientation="",
        topics=[Topic(slug=f"t{i}", title=f"T{i}", why="", scope="substantial",
                      prereqs=[], status="not-started") for i in range(10)]
    )
    errors = validate(m)
    assert any("Too many topics" in e for e in errors)


def test_validate_undefined_prereq():
    m = DomainMap(
        domain="test", description="", depth=0, parent=None,
        leads_to=[], orientation="",
        topics=[
            Topic(slug="a", title="A", why="", scope="substantial",
                  prereqs=["nonexistent"], status="not-started"),
        ]
    )
    errors = validate(m)
    assert any("undefined prereq" in e for e in errors)


def test_validate_cycle():
    m = DomainMap(
        domain="test", description="", depth=0, parent=None,
        leads_to=[], orientation="",
        topics=[
            Topic(slug="a", title="A", why="", scope="substantial",
                  prereqs=["b"], status="not-started"),
            Topic(slug="b", title="B", why="", scope="substantial",
                  prereqs=["a"], status="not-started"),
        ]
    )
    errors = validate(m)
    assert any("Cycle" in e for e in errors)


def test_validate_invalid_status():
    m = DomainMap(
        domain="test", description="", depth=0, parent=None,
        leads_to=[], orientation="",
        topics=[
            Topic(slug="a", title="A", why="", scope="substantial",
                  prereqs=[], status="garbage"),
        ]
    )
    errors = validate(m)
    assert any("invalid status" in e for e in errors)


# ---------------------------------------------------------------------------
# Query tests
# ---------------------------------------------------------------------------

def test_get_available_topics():
    m = load_map(DATA_ANALYTICS_MAP)
    available = get_available_topics(m)
    slugs = [t.slug for t in available]
    # ingestion has no prereqs but storage is in-progress (prereq satisfied)
    # so compute-engines and transformation-and-modeling should be available
    assert "compute-engines" in slugs
    assert "transformation-and-modeling" in slugs
    # governance requires orchestration which is not-started
    assert "governance-and-observability" not in slugs


def test_get_available_all_blocked():
    m = DomainMap(
        domain="test", description="", depth=0, parent=None,
        leads_to=[], orientation="",
        topics=[
            Topic(slug="a", title="A", why="", scope="substantial",
                  prereqs=["b"], status="not-started"),
            Topic(slug="b", title="B", why="", scope="substantial",
                  prereqs=["a"], status="not-started"),
        ]
    )
    assert get_available_topics(m) == []


def test_get_next_suggestion():
    m = load_map(DATA_ANALYTICS_MAP)
    suggestion = get_next_suggestion(m)
    assert suggestion is not None
    # With ingestion=complete and storage=in-progress, transformation-and-modeling
    # has the most downstream dependents (3) among available topics
    assert suggestion.slug in ("transformation-and-modeling", "compute-engines", "ingestion")


def test_get_next_suggestion_nothing_available():
    m = DomainMap(
        domain="test", description="", depth=0, parent=None,
        leads_to=[], orientation="",
        topics=[
            Topic(slug="a", title="A", why="", scope="substantial",
                  prereqs=["b"], status="not-started"),
            Topic(slug="b", title="B", why="", scope="substantial",
                  prereqs=["a"], status="not-started"),
        ]
    )
    assert get_next_suggestion(m) is None


# ---------------------------------------------------------------------------
# Mutation tests
# ---------------------------------------------------------------------------

def test_update_status():
    # Copy a MAP.md to temp, update, verify
    src = DATA_ANALYTICS_MAP
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(src.read_text())
        tmp = Path(f.name)

    update_status(tmp, "ingestion", "in-progress")
    m = load_map(tmp)
    assert m.topic_by_slug("ingestion").status == "in-progress"
    # Other topics unchanged
    assert m.topic_by_slug("storage-and-table-formats").status == "complete"
    assert m.topic_by_slug("compute-engines").status == "not-started"

    # Update again
    update_status(tmp, "ingestion", "complete")
    m = load_map(tmp)
    assert m.topic_by_slug("ingestion").status == "complete"

    tmp.unlink()


def test_update_status_invalid():
    src = DATA_ANALYTICS_MAP
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(src.read_text())
        tmp = Path(f.name)

    try:
        update_status(tmp, "ingestion", "garbage")
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "Invalid status" in str(e)

    tmp.unlink()


def test_update_status_missing_slug():
    src = DATA_ANALYTICS_MAP
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(src.read_text())
        tmp = Path(f.name)

    try:
        update_status(tmp, "nonexistent-topic", "complete")
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "not found" in str(e)

    tmp.unlink()


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    tests = [v for k, v in globals().items() if k.startswith("test_")]
    passed = failed = 0
    for test in tests:
        try:
            test()
            passed += 1
            print(f"  ✓ {test.__name__}")
        except Exception as e:
            failed += 1
            print(f"  ✗ {test.__name__}: {e}")
    print(f"\n{passed} passed, {failed} failed")
    raise SystemExit(1 if failed else 0)
