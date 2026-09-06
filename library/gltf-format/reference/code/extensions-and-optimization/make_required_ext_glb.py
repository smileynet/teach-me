#!/usr/bin/env python3
"""make_required_ext_glb.py — generate required_ext.glb with the Python standard library alone.

Companion generator for lesson 06 (extensions-and-optimization). This is a DECLARE-ONLY teaching
fixture: a plain triangle that lists `EXT_meshopt_compression` in BOTH `extensionsUsed` and
`extensionsRequired` — the correct placement for a compression extension (its buffer bytes are
unreadable without the decoder, so it MUST be required). We do NOT ship a real meshopt payload —
that needs the encoder toolchain (gltf-transform); the point here is the used/required CONTRACT
and its declaration, which is exactly what the oracle's topic-6 assert reads.

A real meshopt file would also carry an `extensions.EXT_meshopt_compression` block on each
bufferView; a declare-only fixture omits that (the geometry stays uncompressed) — so this file
still parses and renders as an ordinary triangle, while demonstrating the required/used split.

Built with `struct` + `json` only. Run: `python make_required_ext_glb.py [out.glb]`.
"""
from __future__ import annotations

import json
import struct
import sys
from pathlib import Path

GLB_MAGIC = 0x46546C67
CHUNK_JSON = 0x4E4F534A
CHUNK_BIN = 0x004E4942
EXT = "EXT_meshopt_compression"   # a compression ext → correctly listed in Used AND Required


def _pad4(b: bytes, fill: bytes = b"\x00") -> bytes:
    return b + fill * ((4 - len(b) % 4) % 4)


def build_triangle() -> tuple[dict, bytes]:
    indices = [0, 1, 2]
    positions = [(0.0, 0.0, 0.0), (1.0, 0.0, 0.0), (0.0, 1.0, 0.0)]

    idx_raw = struct.pack(f"<{len(indices)}H", *indices)
    idx_bytes = _pad4(idx_raw)
    pos_bytes = struct.pack(f"<{len(positions) * 3}f", *[c for p in positions for c in p])

    parts = [idx_bytes, pos_bytes]
    o_idx, o_pos = 0, len(idx_bytes)
    blob = b"".join(parts)

    pmin = [min(p[i] for p in positions) for i in range(3)]
    pmax = [max(p[i] for p in positions) for i in range(3)]

    gltf = {
        "asset": {"version": "2.0", "generator": "teach-me gltf-format lesson 06 (make_required_ext_glb.py, stdlib)"},
        # The whole point of the fixture: a compression ext declared in BOTH arrays (required ⊆ used).
        "extensionsUsed": [EXT],
        "extensionsRequired": [EXT],
        "scene": 0,
        "scenes": [{"nodes": [0]}],
        "nodes": [{"mesh": 0, "name": "RequiredExtTri"}],
        "meshes": [{"primitives": [{"attributes": {"POSITION": 1}, "indices": 0}]}],
        "buffers": [{"byteLength": len(blob)}],
        "bufferViews": [
            {"buffer": 0, "byteOffset": o_idx, "byteLength": len(idx_raw), "target": 34963},
            {"buffer": 0, "byteOffset": o_pos, "byteLength": len(pos_bytes), "target": 34962},
        ],
        "accessors": [
            {"bufferView": 0, "componentType": 5123, "count": len(indices), "type": "SCALAR",
             "min": [0], "max": [len(positions) - 1]},
            {"bufferView": 1, "componentType": 5126, "count": len(positions), "type": "VEC3",
             "min": pmin, "max": pmax},
        ],
    }
    return gltf, blob


def write_glb(gltf: dict, blob: bytes, out: Path) -> None:
    json_bytes = _pad4(json.dumps(gltf, separators=(",", ":")).encode("utf-8"), b" ")
    blob = _pad4(blob)
    body = (struct.pack("<II", len(json_bytes), CHUNK_JSON) + json_bytes
            + struct.pack("<II", len(blob), CHUNK_BIN) + blob)
    out.write_bytes(struct.pack("<III", GLB_MAGIC, 2, 12 + len(body)) + body)


def main() -> int:
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).with_name("required_ext.glb")
    gltf, blob = build_triangle()
    write_glb(gltf, blob, out)
    print(f"wrote {out} ({out.stat().st_size} bytes) — triangle declaring {EXT} in used + required")
    return 0


if __name__ == "__main__":
    sys.exit(main())
