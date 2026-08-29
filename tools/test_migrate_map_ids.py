"""Tests for tools/migrate_map_ids.py insert_ids (#257 Subtask B)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from migrate_map_ids import insert_ids
from lib import ulid

_LF = (
    "---\ndomain: t\ndepth: 0\n---\n\n# T\n\n## Topics\n\n"
    "### alpha\n- **title:** Alpha\n- **prereqs:** []\n- **status:** complete\n\n"
    "### beta\n- **title:** Beta\n- **prereqs:** [alpha]\n- **status:** not-started\n"
)
_CRLF = _LF.replace("\n", "\r\n")


def _id_values(text: str) -> list[str]:
    import re
    return re.findall(r"- \*\*id:\*\*[ \t]*(\S+)", text)


def test_inserts_one_id_per_topic():
    out, ins, skip, manual = insert_ids(_LF)
    assert ins == 2 and skip == 0 and manual == []
    ids = _id_values(out)
    assert len(ids) == 2 and all(ulid.is_valid(i) for i in ids)


def test_id_is_first_field_after_header():
    out, _, _, _ = insert_ids(_LF)
    # The line immediately after each '### slug' is the id line.
    lines = out.split("\n")
    for i, ln in enumerate(lines):
        if ln.startswith("### "):
            assert lines[i + 1].startswith("- **id:** "), lines[i + 1]


def test_idempotent_second_pass_is_noop():
    once, _, _, _ = insert_ids(_LF)
    twice, ins, skip, manual = insert_ids(once)
    assert twice == once  # byte-identical
    assert ins == 0 and skip == 2 and manual == []


def test_preserves_lf():
    out, _, _, _ = insert_ids(_LF)
    assert "\r\n" not in out  # pure-LF input stays LF


def test_preserves_crlf():
    out, ins, _, _ = insert_ids(_CRLF)
    assert ins == 2
    # every line (incl. inserted id lines) is CRLF-terminated; no bare LF introduced
    assert "\r\n" in out
    assert out.replace("\r\n", "") .count("\n") == 0  # no lone \n remains


def test_skips_valid_existing_id_flags_invalid():
    good = ulid.new()
    with_valid = _LF.replace(
        "### alpha\n- **title:** Alpha",
        f"### alpha\n- **id:** {good}\n- **title:** Alpha",
    )
    out, ins, skip, manual = insert_ids(with_valid)
    assert ins == 1  # only beta gets one
    assert manual == []
    assert good in _id_values(out)  # existing valid id preserved

    with_invalid = _LF.replace(
        "### alpha\n- **title:** Alpha",
        "### alpha\n- **id:** NOT-A-ULID\n- **title:** Alpha",
    )
    out2, ins2, skip2, manual2 = insert_ids(with_invalid)
    assert "alpha" in manual2  # flagged, not duplicated
    assert out2.count("- **id:**") == 2  # alpha's invalid one left, beta's added — no dup on alpha


if __name__ == "__main__":
    for name, fn in sorted((k, v) for k, v in globals().items() if k.startswith("test_")):
        fn()
        print(f"  ok {name}")
    print("all passed")
