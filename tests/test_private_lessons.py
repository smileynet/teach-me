"""Tests for #184 private-lesson support in the domain graph.

Covers: private-map discovery (`.user/maps/`), the Visibility variant (single source of
truth = provenance), merge of a private overlay into its committed domain, and a
wholly-private domain record.
"""

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

from lib.domain_graph import (  # noqa: E402
    Shared,
    Private,
    is_private,
    find_maps,
    find_private_maps,
    build_domain_graph,
)


def _write_map(path: Path, domain: str, topics: list[tuple[str, str]]) -> None:
    """Write a minimal valid MAP.md. topics = [(slug, prereq_slug_or_empty), ...]."""
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "---",
        f"domain: {domain}",
        f"description: Test domain {domain}",
        "depth: 0",
        "---",
        "",
        f"# {domain.replace('-', ' ').title()}",
        "",
        "## Topics",
        "",
    ]
    for slug, prereq in topics:
        lines += [
            f"### {slug}",
            f"- **title:** {slug}",
            "- **why:** because this matters for the domain",
            "- **scope:** substantial",
        ]
        if prereq:
            lines.append(f"- **prereqs:** [{prereq}]")
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


class TestVisibilityModel:
    def test_shared_and_private_are_distinct_variants(self):
        s = Shared(Path("library/x/x.MAP.md"))
        p = Private(Path(".user/maps/x.MAP.md"), promote_target=Path("x.MAP.md"))
        assert not is_private(s)
        assert is_private(p)

    def test_private_carries_promote_target(self):
        p = Private(Path(".user/maps/secret.MAP.md"), promote_target=Path("ws/secret.MAP.md"))
        assert p.promote_target == Path("ws/secret.MAP.md")


class TestDiscovery:
    def test_find_maps_excludes_user_overlay(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write_map(root / "shared" / "shared.MAP.md", "shared", [("a", "")])
            _write_map(root / ".user" / "maps" / "secret.MAP.md", "secret", [("b", "")])
            found = find_maps([root])
            assert any(".user" not in p.parts for p in found)
            assert all(".user" not in p.parts for p in found), "committed scan must skip .user/"

    def test_find_private_maps_finds_only_user_overlay(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write_map(root / "shared" / "shared.MAP.md", "shared", [("a", "")])
            _write_map(root / ".user" / "maps" / "secret.MAP.md", "secret", [("b", "")])
            priv = find_private_maps([root])
            assert len(priv) == 1
            assert priv[0].name == "secret.MAP.md"
            assert ".user" in priv[0].parts


class TestGraphMerge:
    def test_private_only_domain_becomes_private_record(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write_map(root / ".user" / "maps" / "mynotes.MAP.md", "mynotes", [("t1", "")])
            records = build_domain_graph(find_maps([root]), find_private_maps([root]))
            assert len(records) == 1
            rec = records[0]
            assert rec["domain"] == "mynotes"
            assert rec["private"] is True
            assert is_private(rec["source"])
            # A private domain never seeds the committed demo.
            assert rec["demo_status"] == {}

    def test_private_overlay_merges_into_committed_domain(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write_map(root / "godot" / "godot.MAP.md", "godot", [("nodes", ""), ("scenes", "")])
            _write_map(root / ".user" / "maps" / "godot.MAP.md", "godot", [("my-secret-topic", "")])
            records = build_domain_graph(find_maps([root]), find_private_maps([root]))
            # Merged, not a separate record.
            godot = [r for r in records if r["domain"] == "godot"]
            assert len(godot) == 1
            rec = godot[0]
            assert rec["source"].__class__.__name__ == "Shared"  # host stays Shared
            assert rec["total"] == 3, "2 committed + 1 private"
            assert rec.get("has_private") is True
            assert len(rec["private_topic_ids"]) == 1
            # The private topic id is in the union join key but NOT in the demo seed.
            assert len(rec["topic_ids"]) == 3
            for pid in rec["private_topic_ids"]:
                assert pid not in rec["demo_status"]

    def test_no_private_maps_is_unchanged_behavior(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write_map(root / "godot" / "godot.MAP.md", "godot", [("nodes", "")])
            records = build_domain_graph(find_maps([root]))  # no private arg
            assert len(records) == 1
            assert records[0]["private"] is False
            assert "private_topic_ids" not in records[0]


class TestSharedToPrivatePrereqBan:
    """Step E: a committed topic MUST NOT depend on a private one. Because the committed
    forest validation only sees committed maps, a committed prereq that resolves only in a
    `.user/` overlay fails as 'undefined prereq' — structurally enforcing the ban."""

    def test_committed_prereq_on_private_only_slug_is_undefined(self):
        from map_parser import load_map, validate_forest

        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            # Committed 'public' topic prereqs 'private-note' which lives ONLY in .user/.
            _write_map(root / "d" / "maps" / "d.MAP.md", "d", [("public", "private-note")])
            _write_map(root / "d" / ".user" / "maps" / "d.MAP.md", "d", [("private-note", "")])
            # Committed forest = committed maps only (never .user/).
            committed = [load_map(p) for p in (root / "d" / "maps").glob("*.MAP.md")]
            errors = validate_forest(committed)
            assert any("undefined prereq" in e and "private-note" in e for e in errors), errors


class TestIndexGenerationIntegration:
    """Steps C + D end-to-end via generate_index_page: a private overlay surfaces a badge
    and merges counts; NO overlay produces a page with zero private references (no pollution)."""

    def _gen(self, scan_dir: Path, out: Path) -> str:
        import importlib.util

        gp = Path(__file__).resolve().parent.parent / "tools" / "generate_index_page.py"
        spec = importlib.util.spec_from_file_location("generate_index_page", gp)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        paths = mod.find_maps([scan_dir])
        private = mod.find_private_maps([scan_dir])
        records = mod.build_domain_graph(paths, private)
        data = mod.build_page_data(records, out, None)
        return data

    def test_private_overlay_adds_badge_flag_and_merges_count(self):
        with tempfile.TemporaryDirectory() as d:
            scan = Path(d)
            _write_map(scan / "godot" / "maps" / "godot.MAP.md", "godot", [("nodes", ""), ("scenes", "")])
            _write_map(scan / ".user" / "maps" / "godot.MAP.md", "godot", [("my-notes", "")])
            data = self._gen(scan, scan / "index.html")
            godot = next(dd for dd in data["domains"] if dd["slug"] == "godot")
            assert godot["hasPrivate"] is True
            assert godot["total"] == 3, "2 committed + 1 private merged locally"
            assert len(godot["privateTopicIds"]) == 1
            # The private topic must NOT be in the committed demo seed.
            assert godot["privateTopicIds"][0] not in data["demoOverlay"]

    def test_no_overlay_has_no_private_flags(self):
        with tempfile.TemporaryDirectory() as d:
            scan = Path(d)
            _write_map(scan / "godot" / "maps" / "godot.MAP.md", "godot", [("nodes", "")])
            data = self._gen(scan, scan / "index.html")
            godot = next(dd for dd in data["domains"] if dd["slug"] == "godot")
            assert godot["private"] is False
            assert godot["hasPrivate"] is False
            assert godot["privateTopicIds"] == []


class TestPromote:
    """Optional AC: promote a private topic (move .user/ -> committed tree, no auto-commit)."""

    def _promote(self, workspace, domain, dry_run=False):
        import importlib.util

        pp = Path(__file__).resolve().parent.parent / "tools" / "promote-private-topic.py"
        spec = importlib.util.spec_from_file_location("promote_private_topic", pp)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod.promote(workspace, domain, dry_run)

    def test_promote_moves_map_and_lessons(self):
        with tempfile.TemporaryDirectory() as d:
            ws = Path(d)
            _write_map(ws / ".user" / "maps" / "mynotes.MAP.md", "mynotes", [("t1", "")])
            (ws / ".user" / "lessons" / "mynotes").mkdir(parents=True)
            (ws / ".user" / "lessons" / "mynotes" / "01-t1.html").write_text("<html>", encoding="utf-8")
            report = self._promote(ws, "mynotes")
            assert not report["errors"], report
            assert (ws / "maps" / "mynotes.MAP.md").exists()
            assert (ws / "lessons" / "mynotes" / "01-t1.html").exists()
            # Moved OUT of .user/
            assert not (ws / ".user" / "maps" / "mynotes.MAP.md").exists()

    def test_promote_refuses_to_overwrite_committed(self):
        with tempfile.TemporaryDirectory() as d:
            ws = Path(d)
            _write_map(ws / ".user" / "maps" / "dup.MAP.md", "dup", [("t1", "")])
            _write_map(ws / "maps" / "dup.MAP.md", "dup", [("committed", "")])
            report = self._promote(ws, "dup")
            assert report["errors"], "must refuse to overwrite an existing committed map"
            assert (ws / ".user" / "maps" / "dup.MAP.md").exists(), "private map left intact"

    def test_promote_dry_run_moves_nothing(self):
        with tempfile.TemporaryDirectory() as d:
            ws = Path(d)
            _write_map(ws / ".user" / "maps" / "mynotes.MAP.md", "mynotes", [("t1", "")])
            report = self._promote(ws, "mynotes", dry_run=True)
            assert report["moved"] and "[dry-run]" in report["moved"][0]
            assert (ws / ".user" / "maps" / "mynotes.MAP.md").exists()
            assert not (ws / "maps" / "mynotes.MAP.md").exists()

