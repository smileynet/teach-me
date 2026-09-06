#!/usr/bin/env python3
"""make_cube_glb.py — generate cube_metalrough.glb with the Python standard library alone.

Companion generator for lesson 02 (authoring-and-blender-export). Builds the "clean export"
the lesson teaches — a cube with a **pbrMetallicRoughness** material whose base color comes
from an **embedded PNG texture** — using only `struct`, `json`, and `zlib` (the PNG is generated
with `zlib`+`struct`+`crc32`; no Blender, no Pillow). The point: the exact channel layout a
conformant DCC export produces, made reproducible and inspectable, so the lesson's claims are
backed by a real file the `gltf-format-oracle.py` gate validates.

Run: `python make_cube_glb.py [out.glb]`  (default: cube_metalrough.glb next to this script).

This is NOT the Blender path — that's `export_cube.py` (a bpy script). This stdlib generator
is what lets the artifact ship + validate on a fresh clone with no Blender installed.
"""
from __future__ import annotations

import json
import struct
import sys
import zlib
from pathlib import Path

GLB_MAGIC = 0x46546C67
CHUNK_JSON = 0x4E4F534A
CHUNK_BIN = 0x004E4942


def make_png(width: int, height: int, rgb: tuple[int, int, int]) -> bytes:
    """A minimal solid-color RGB PNG, stdlib only (zlib + struct + crc32). No Pillow."""
    def chunk(tag: bytes, data: bytes) -> bytes:
        return (struct.pack(">I", len(data)) + tag + data
                + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF))

    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)  # 8-bit, color type 2 (RGB)
    # raw scanlines: each row prefixed with filter byte 0, then width*3 RGB bytes
    row = bytes(rgb) * width
    raw = b"".join(b"\x00" + row for _ in range(height))
    idat = zlib.compress(raw, 9)
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) + chunk(b"IDAT", idat) + chunk(b"IEND", b"")


def build_cube() -> tuple[dict, bytes]:
    """Return (gltf_json, bin_blob) for a unit cube with a base-color-textured metal-rough material."""
    # 24 vertices (4 per face) so each face has its own UVs; positions in meters, +Y up.
    # face order: +X -X +Y -Y +Z -Z
    faces = [
        ([( 0.5,-0.5,-0.5),( 0.5, 0.5,-0.5),( 0.5, 0.5, 0.5),( 0.5,-0.5, 0.5)]),  # +X
        ([(-0.5,-0.5, 0.5),(-0.5, 0.5, 0.5),(-0.5, 0.5,-0.5),(-0.5,-0.5,-0.5)]),  # -X
        ([(-0.5, 0.5,-0.5),(-0.5, 0.5, 0.5),( 0.5, 0.5, 0.5),( 0.5, 0.5,-0.5)]),  # +Y
        ([(-0.5,-0.5, 0.5),(-0.5,-0.5,-0.5),( 0.5,-0.5,-0.5),( 0.5,-0.5, 0.5)]),  # -Y
        ([(-0.5,-0.5, 0.5),( 0.5,-0.5, 0.5),( 0.5, 0.5, 0.5),(-0.5, 0.5, 0.5)]),  # +Z
        ([( 0.5,-0.5,-0.5),(-0.5,-0.5,-0.5),(-0.5, 0.5,-0.5),( 0.5, 0.5,-0.5)]),  # -Z
    ]
    positions: list[tuple[float, float, float]] = []
    uvs: list[tuple[float, float]] = []
    indices: list[int] = []
    for quad in faces:
        base = len(positions)
        positions.extend(quad)
        uvs.extend([(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)])
        indices.extend([base, base + 1, base + 2, base, base + 2, base + 3])

    # Pack BIN: indices (u16) [pad to 4] + positions (f32 vec3) + uvs (f32 vec2)
    idx_bytes = struct.pack(f"<{len(indices)}H", *indices)
    idx_pad = (4 - len(idx_bytes) % 4) % 4
    idx_bytes += b"\x00" * idx_pad
    pos_bytes = struct.pack(f"<{len(positions) * 3}f", *[c for p in positions for c in p])
    uv_bytes = struct.pack(f"<{len(uvs) * 2}f", *[c for uv in uvs for c in uv])
    png_bytes = make_png(2, 2, (200, 120, 60))  # a small solid base-color texture
    png_pad = (4 - len(png_bytes) % 4) % 4
    png_bytes_padded = png_bytes + b"\x00" * png_pad

    blob = idx_bytes + pos_bytes + uv_bytes + png_bytes_padded
    o_idx, o_pos, o_uv, o_png = 0, len(idx_bytes), len(idx_bytes) + len(pos_bytes), \
        len(idx_bytes) + len(pos_bytes) + len(uv_bytes)

    pmin = [min(p[i] for p in positions) for i in range(3)]
    pmax = [max(p[i] for p in positions) for i in range(3)]

    gltf = {
        "asset": {"version": "2.0", "generator": "teach-me gltf-format lesson 02 (make_cube_glb.py, stdlib)"},
        "scene": 0,
        "scenes": [{"nodes": [0]}],
        "nodes": [{"mesh": 0, "name": "Cube"}],
        "meshes": [{"primitives": [{"attributes": {"POSITION": 1, "TEXCOORD_0": 2},
                                    "indices": 0, "material": 0}]}],
        "materials": [{
            "name": "CubeMetalRough",
            "pbrMetallicRoughness": {
                "baseColorTexture": {"index": 0},
                "metallicFactor": 0.0,
                "roughnessFactor": 0.8,
            },
        }],
        "textures": [{"source": 0, "sampler": 0}],
        "images": [{"bufferView": 3, "mimeType": "image/png"}],
        "samplers": [{"magFilter": 9729, "minFilter": 9987}],
        "buffers": [{"byteLength": len(blob)}],
        "bufferViews": [
            {"buffer": 0, "byteOffset": o_idx, "byteLength": len(idx_bytes) - idx_pad, "target": 34963},
            {"buffer": 0, "byteOffset": o_pos, "byteLength": len(pos_bytes), "target": 34962},
            {"buffer": 0, "byteOffset": o_uv, "byteLength": len(uv_bytes), "target": 34962},
            {"buffer": 0, "byteOffset": o_png, "byteLength": len(png_bytes)},  # image bytes (no target)
        ],
        "accessors": [
            {"bufferView": 0, "componentType": 5123, "count": len(indices), "type": "SCALAR",
             "min": [0], "max": [len(positions) - 1]},
            {"bufferView": 1, "componentType": 5126, "count": len(positions), "type": "VEC3",
             "min": pmin, "max": pmax},
            {"bufferView": 2, "componentType": 5126, "count": len(uvs), "type": "VEC2"},
        ],
    }
    return gltf, blob


def write_glb(gltf: dict, blob: bytes, out: Path) -> None:
    json_bytes = json.dumps(gltf, separators=(",", ":")).encode("utf-8")
    json_bytes += b" " * ((4 - len(json_bytes) % 4) % 4)          # pad JSON with 0x20
    blob = blob + b"\x00" * ((4 - len(blob) % 4) % 4)             # pad BIN with 0x00
    body = (struct.pack("<II", len(json_bytes), CHUNK_JSON) + json_bytes
            + struct.pack("<II", len(blob), CHUNK_BIN) + blob)
    out.write_bytes(struct.pack("<III", GLB_MAGIC, 2, 12 + len(body)) + body)


def main() -> int:
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).with_name("cube_metalrough.glb")
    gltf, blob = build_cube()
    write_glb(gltf, blob, out)
    print(f"wrote {out} ({out.stat().st_size} bytes) — "
          f"{len(gltf['meshes'][0]['primitives'])} primitive, pbrMetallicRoughness + baseColorTexture")
    return 0


if __name__ == "__main__":
    sys.exit(main())
