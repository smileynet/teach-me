"""Minimal ULID — 48-bit ms timestamp + 80-bit randomness, Crockford base32.

Lexicographically sortable by creation time (the timestamp is front-loaded), so
`sorted(ids)` yields creation order with no separate timestamp column. 26 chars,
URL-safe, no hyphens. Spec: https://github.com/ulid/spec

Vendored (zero runtime deps) per ADR-0014 / #257: IDs are minted rarely (authoring +
one-shot migration) and stored as the 26-char string in git; the runtime path only
parses/validates. Escape hatch preserved — the string is a spec-compliant ULID, so a
later move to `python-ulid` or stdlib `uuid7` (py3.14+) needs no reformatting.

Case policy: mint canonical UPPERCASE; `is_valid`/`parse` fold lowercase (ULID is
case-insensitive) so a hand-lowercased id still resolves, while stored ids stay
uppercase for stable diffs.
"""
from __future__ import annotations

import os
import time

_ALPHABET = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"  # Crockford base32 (no I, L, O, U)
_DECODE = {c: i for i, c in enumerate(_ALPHABET)}
_LEN = 26


def new(ms: int | None = None) -> str:
    """Mint a new 26-char ULID string (canonical uppercase)."""
    ms = int(time.time() * 1000) if ms is None else ms
    n = (ms << 80) | int.from_bytes(os.urandom(10), "big")  # 128 bits
    out = bytearray(_LEN)
    for i in range(_LEN - 1, -1, -1):
        out[i] = ord(_ALPHABET[n & 0x1F])
        n >>= 5
    return out.decode("ascii")


def is_valid(s: object) -> bool:
    """True if s is a well-formed ULID string (case-insensitive)."""
    if not isinstance(s, str) or len(s) != _LEN:
        return False
    su = s.upper()
    # First char <= '7': the 130-bit base32 space must not overflow 128 bits.
    return su[0] <= "7" and all(c in _DECODE for c in su)


def parse(s: str) -> int:
    """Return the 128-bit integer value, raising ValueError on a malformed ULID."""
    if not is_valid(s):
        raise ValueError(f"invalid ULID: {s!r}")
    n = 0
    for c in s.upper():
        n = (n << 5) | _DECODE[c]
    return n


def timestamp_ms(s: str) -> int:
    """Extract the embedded creation time (ms since epoch)."""
    return parse(s) >> 80


if __name__ == "__main__":
    # Self-test: mint, validate, round-trip, sortability, rejection.
    a = new()
    assert is_valid(a) and len(a) == 26, a
    assert a == a.upper(), "canonical form is uppercase"
    assert parse(a) == parse(a.lower()), "case-insensitive parse"
    # Monotonic across increasing timestamps → lexicographic sort = time order.
    older = new(ms=1_000)
    newer = new(ms=2_000)
    assert older < newer, (older, newer)
    assert timestamp_ms(older) == 1_000 and timestamp_ms(newer) == 2_000
    # Rejections.
    for bad in ["", "x", "I" * 26, "8" + "0" * 25, 123, None, a[:-1]]:
        assert not is_valid(bad), bad
    print("tools/lib/ulid.py self-test OK:", a)
