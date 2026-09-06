#!/usr/bin/env python3
"""make_tri_morph_glb.py — generate morph_tri.glb with the Python standard library alone.

Companion generator for lesson 05 (animation-skins-and-morphs). Where skinning re-poses a shared
mesh through joint matrices, a MORPH TARGET moves vertices by per-vertex DELTAS: the rendered
position is `base + Σ weights[j]·target[j]`. This is the minimal demonstration — a single triangle
with ONE morph target whose POSITION-delta lifts one vertex, plus a `mesh.weights` array.

Built with `struct` + `json` only (no Blender, no Pillow) so it ships and validates on a fresh
clone. It also lights up the domain oracle's morph branch (`len(mesh.weights) == len(targets)`),
which no other committed fixture exercises.

Run: `python make_tri_morph_glb.py [out.glb]`  (default: morph_tri.glb next to this script).
"""
from __future__ import annotations

import json
import struct
import sys
from pathlib import Path

GLB_MAGIC = 0x46546C67
CHUNK_JSON = 0x4E4F534A
CHUNK_BIN = 0x004E4942


def _pad4(b: bytes, fill: bytes = b"\x00") -> bytes:
    return b + fill * ((4 - len(b) % 4) % 4)


def build_triangle() -> tuple[dict, bytes]:
    """A triangle with one morph target (a POSITION delta lifting vertex 0 by +0.5 in Y)."""
    indices = [0, 1, 2]
    positions = [(0.0, 0.0, 0.0), (1.0, 0.0, 0.0), (0.0, 1.0, 0.0)]
    # Morph target = per-vertex POSITION deltas. Only vertex 0 moves (+0.5 Y); others are zero.
    deltas = [(0.0, 0.5, 0.0), (0.0, 0.0, 0.0), (0.0, 0.0, 0.0)]

    idx_raw = struct.pack(f"<{len(indices)}H", *indices)
    idx_bytes = _pad4(idx_raw)
    pos_bytes = struct.pack(f"<{len(positions) * 3}f", *[c for p in positions for c in p])
    delta_bytes = struct.pack(f"<{len(deltas) * 3}f", *[c for d in deltas for c in d])

    parts = [idx_bytes, pos_bytes, delta_bytes]
    offsets, cursor = [], 0
    for p in parts:
        offsets.append(cursor)
        cursor += len(p)
    o_idx, o_pos, o_delta = offsets
    blob = b"".join(parts)

    pmin = [min(p[i] for p in positions) for i in range(3)]
    pmax = [max(p[i] for p in positions) for i in range(3)]
    dmin = [min(d[i] for d in deltas) for i in range(3)]
    dmax = [max(d[i] for d in deltas) for i in range(3)]

    gltf = {
        "asset": {"version": "2.0", "generator": "teach-me gltf-format lesson 05 (make_tri_morph_glb.py, stdlib)"},
        "scene": 0,
        "scenes": [{"nodes": [0]}],
        "nodes": [{"mesh": 0, "name": "MorphTri"}],
        "meshes": [{
            "primitives": [{
                "attributes": {"POSITION": 1},
                "indices": 0,
                "targets": [{"POSITION": 2}],   # one morph target: a POSITION-delta accessor
            }],
            "weights": [0.0],                   # base weight for the single target (animate via a "weights" channel)
        }],
        "buffers": [{"byteLength": len(blob)}],
        "bufferViews": [
            {"buffer": 0, "byteOffset": o_idx, "byteLength": len(idx_raw), "target": 34963},
            {"buffer": 0, "byteOffset": o_pos, "byteLength": len(pos_bytes), "target": 34962},
            {"buffer": 0, "byteOffset": o_delta, "byteLength": len(delta_bytes), "target": 34962},
        ],
        "accessors": [
            {"bufferView": 0, "componentType": 5123, "count": len(indices), "type": "SCALAR",
             "min": [0], "max": [len(positions) - 1]},
            {"bufferView": 1, "componentType": 5126, "count": len(positions), "type": "VEC3",
             "min": pmin, "max": pmax},
            # the POSITION-delta accessor — same count/type as base POSITION; min/max cover DELTAS
            {"bufferView": 2, "componentType": 5126, "count": len(deltas), "type": "VEC3",
             "min": dmin, "max": dmax},
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
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).with_name("morph_tri.glb")
    gltf, blob = build_triangle()
    write_glb(gltf, blob, out)
    print(f"wrote {out} ({out.stat().st_size} bytes) — triangle + 1 morph target (POSITION delta) + weights[0.0]")
    return 0


if __name__ == "__main__":
    sys.exit(main())
