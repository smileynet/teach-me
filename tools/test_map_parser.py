"""Tests for tools/map_parser.py."""

# Windows consoles default to cp1252; force UTF-8 so ✓/→/emoji glyphs don't crash (#265).
import sys as _sys
if hasattr(_sys.stdout, "reconfigure"):
    _sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(_sys.stderr, "reconfigure"):
    _sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import tempfile
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent))

from map_parser import (
    DomainMap, Topic, Edge, load_map, validate,
    get_available_topics, get_next_suggestion,
)

EXAMPLES_DIR = Path(__file__).parent.parent / "library"
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
                      prereqs=[]) for i in range(10)]
    )
    errors = validate(m)
    assert any("Too many topics" in e for e in errors)


def test_validate_undefined_prereq():
    m = DomainMap(
        domain="test", description="", depth=0, parent=None,
        leads_to=[], orientation="",
        topics=[
            Topic(slug="a", title="A", why="", scope="substantial",
                  prereqs=["nonexistent"]),
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
                  prereqs=["b"]),
            Topic(slug="b", title="B", why="", scope="substantial",
                  prereqs=["a"]),
        ]
    )
    errors = validate(m)
    assert any("Cycle" in e for e in errors)


# ---------------------------------------------------------------------------
# Query tests
# ---------------------------------------------------------------------------

def test_get_available_topics():
    m = load_map(DATA_ANALYTICS_MAP)
    # Status now lives in the overlay: {node_id → status}. Reproduce the historical
    # scenario (ingestion complete, storage in-progress) via an explicit status_map.
    ing = m.topic_by_slug("ingestion").id
    sto = m.topic_by_slug("storage-and-table-formats").id
    status_map = {ing: "complete", sto: "in-progress"}
    available = get_available_topics(m, status_map)
    slugs = [t.slug for t in available]
    # compute-engines and transformation-and-modeling should be available
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
                  prereqs=["b"], id="A" * 26),
            Topic(slug="b", title="B", why="", scope="substantial",
                  prereqs=["a"], id="B" * 26),
        ],
        edges=[
            Edge(source_id="B" * 26, target_id="A" * 26, type="prereq"),  # a needs b
            Edge(source_id="A" * 26, target_id="B" * 26, type="prereq"),  # b needs a
        ],
    )
    assert get_available_topics(m, {}) == []


def test_get_next_suggestion():
    m = load_map(DATA_ANALYTICS_MAP)
    ing = m.topic_by_slug("ingestion").id
    sto = m.topic_by_slug("storage-and-table-formats").id
    suggestion = get_next_suggestion(m, {ing: "complete", sto: "in-progress"})
    assert suggestion is not None
    # transformation-and-modeling has the most downstream dependents among available
    assert suggestion.slug in ("transformation-and-modeling", "compute-engines", "ingestion")


def test_get_next_suggestion_nothing_available():
    m = DomainMap(
        domain="test", description="", depth=0, parent=None,
        leads_to=[], orientation="",
        topics=[
            Topic(slug="a", title="A", why="", scope="substantial",
                  prereqs=["b"], id="A" * 26),
            Topic(slug="b", title="B", why="", scope="substantial",
                  prereqs=["a"], id="B" * 26),
        ],
        edges=[
            Edge(source_id="B" * 26, target_id="A" * 26, type="prereq"),
            Edge(source_id="A" * 26, target_id="B" * 26, type="prereq"),
        ],
    )
    assert get_next_suggestion(m, {}) is None


# ---------------------------------------------------------------------------
# Overlay-derived readiness (fresh overlay = all not-started)
# ---------------------------------------------------------------------------

def test_empty_overlay_only_roots_available():
    """Fresh clone (empty overlay): only topics with no prereqs are available."""
    m = load_map(DATA_ANALYTICS_MAP)
    available = get_available_topics(m, {})
    # Every available topic must have zero prereqs (nothing is complete/in-progress yet).
    for t in available:
        assert t.prereqs == [], f"{t.slug} available with unmet prereqs on empty overlay"
    assert available, "at least one root topic should be available"


# ---------------------------------------------------------------------------
# #257 — ULID ids + typed edges
# ---------------------------------------------------------------------------

import lib.ulid as _ulid


def _write_map(body: str) -> Path:
    with tempfile.NamedTemporaryFile(mode="w", suffix=".MAP.md", delete=False, encoding="utf-8") as f:
        f.write(body)
        return Path(f.name)


_BASE_MAP = """---
domain: t
description: "d"
depth: 0
parent: null
---

# T

## Orientation

Intro.

## Topics

### alpha
- **title:** Alpha
- **why:** w
- **scope:** substantial
- **prereqs:** []

### beta
- **title:** Beta
- **why:** w
- **scope:** substantial
- **prereqs:** [alpha]
"""


def test_id_minted_when_absent():
    p = _write_map(_BASE_MAP)
    m = load_map(p)
    assert all(_ulid.is_valid(t.id) for t in m.topics)
    assert m.topic_by_id(m.topics[0].id) is m.topics[0]
    p.unlink()


def test_prereq_edges_synthesized_from_inline():
    p = _write_map(_BASE_MAP)
    m = load_map(p)
    prereq = [e for e in m.edges if e.type == "prereq"]
    assert len(prereq) == 1
    alpha = m.topic_by_slug("alpha")
    beta = m.topic_by_slug("beta")
    assert prereq[0].source_id == alpha.id and prereq[0].target_id == beta.id
    assert validate(m) == []
    p.unlink()


def test_edges_section_typed_and_related_symmetric():
    body = _BASE_MAP + """
## Edges
- from: alpha
  to: beta
  type: related
  why: "adjacent ideas"
"""
    p = _write_map(body)
    m = load_map(p)
    related = [e for e in m.edges if e.type == "related"]
    # symmetric — author once, both directions derived
    assert len(related) == 2
    pairs = {(e.source_id, e.target_id) for e in related}
    a, b = m.topic_by_slug("alpha").id, m.topic_by_slug("beta").id
    assert (a, b) in pairs and (b, a) in pairs
    assert all(e.why == "adjacent ideas" for e in related)
    # a symmetric related edge must NOT be flagged as a prereq cycle
    assert validate(m) == []
    p.unlink()


def test_prereq_cycle_detected_but_related_cycle_ok():
    # prereq cycle → error
    m = DomainMap(
        domain="t", description="", depth=0, parent=None, leads_to=[], orientation="",
        topics=[
            Topic(slug="a", title="A", why="", scope="substantial", prereqs=[], id="A" * 26),
            Topic(slug="b", title="B", why="", scope="substantial", prereqs=[], id="B" * 26),
        ],
        edges=[
            Edge("A" * 26, "B" * 26, "prereq"),
            Edge("B" * 26, "A" * 26, "prereq"),
        ],
    )
    assert any("Cycle" in e for e in validate(m))
    # same shape but related → no cycle error
    m.edges = [Edge("A" * 26, "B" * 26, "related"), Edge("B" * 26, "A" * 26, "related")]
    assert not any("Cycle" in e for e in validate(m))


def test_validate_flags_bad_id_and_edge_type():
    m = DomainMap(
        domain="t", description="", depth=0, parent=None, leads_to=[], orientation="",
        topics=[Topic(slug="a", title="A", why="", scope="substantial", prereqs=[], id="not-a-ulid")],
        edges=[Edge("A" * 26, "A" * 26, "bogus")],
    )
    errs = validate(m)
    assert any("invalid ULID" in e for e in errs)
    assert any("invalid type" in e for e in errs)


def test_soft_prereqs_become_symmetric_related_edges():
    body = _BASE_MAP.replace(
        "### beta\n- **title:** Beta\n- **why:** w\n- **scope:** substantial\n- **prereqs:** [alpha]",
        "### beta\n- **title:** Beta\n- **why:** w\n- **scope:** substantial\n- **prereqs:** []\n- **soft_prereqs:** [alpha]",
    )
    p = _write_map(body)
    m = load_map(p)
    a, b = m.topic_by_slug("alpha").id, m.topic_by_slug("beta").id
    related = [(e.source_id, e.target_id) for e in m.edges if e.type == "related"]
    assert (a, b) in related and (b, a) in related  # symmetric
    # soft prereq is NOT a prereq edge and is NOT cycle-checked
    assert not any(e.type == "prereq" and e.source_id == a and e.target_id == b for e in m.edges)
    assert validate(m) == []
    p.unlink()


def test_slug_rename_preserves_edges():
    # Fixture with EXPLICIT ids so ids are stable across loads (no ephemeral minting).
    aid, bid = _ulid.new(), _ulid.new()
    body = (
        "---\ndomain: t\ndescription: \"d\"\ndepth: 0\nparent: null\n---\n\n# T\n\n"
        "## Orientation\n\nIntro.\n\n## Topics\n\n"
        f"### alpha\n- **id:** {aid}\n- **title:** Alpha\n- **prereqs:** []\n\n"
        f"### beta\n- **id:** {bid}\n- **title:** Beta\n- **prereqs:** [alpha]\n"
    )
    p = _write_map(body)
    before = sorted((e.source_id, e.target_id, e.type) for e in load_map(p).edges)

    # Rename alpha's slug (header) AND its reference in beta's prereqs. Ids are unchanged.
    renamed = p.read_text(encoding="utf-8").replace("### alpha", "### alpha-renamed").replace("[alpha]", "[alpha-renamed]")
    p.write_text(renamed, encoding="utf-8")
    m2 = load_map(p)
    after = sorted((e.source_id, e.target_id, e.type) for e in m2.edges)

    assert after == before, "id-keyed edges changed after a slug rename"
    assert validate(m2) == [], "rename introduced validation errors"
    # The prereq edge still points from alpha's id to beta's id, regardless of the new slug.
    assert (aid, bid, "prereq") in after
    p.unlink()


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
