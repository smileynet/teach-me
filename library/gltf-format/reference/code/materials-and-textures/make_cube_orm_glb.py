#!/usr/bin/env python3
"""make_cube_orm_glb.py — generate cube_orm.glb with the Python standard library alone.

Companion generator for lesson 04 (materials-and-textures). Where lesson 02's cube had ONLY a
base-color texture, this cube exercises BOTH color-space families so the color-space rule is
demonstrable on a real file:

  - baseColorTexture           → an sRGB image   (color, must be sRGB-decoded before lighting)
  - metallicRoughnessTexture   → a LINEAR image  (ORM: R=occlusion, G=roughness, B=metalness)
  - occlusionTexture           → the SAME linear ORM image, read from its R channel
  - normalTexture              → a LINEAR image  (tangent-space XYZ, "Non-Color")

Built with `struct`, `json`, and `zlib` only (PNGs via zlib+crc32; no Blender, no Pillow) so it
ships and validates on a fresh clone. The point the lesson teaches: glTF has NO per-slot
color-space FLAG — the family is implied by the SLOT NAME. `check_material_colorspace.py` and the
domain `gltf-format-oracle.py` assert the rule structurally (no image is shared across an sRGB and
a linear slot).

Run: `python make_cube_orm_glb.py [out.glb]`  (default: cube_orm.glb next to this script).
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
    row = bytes(rgb) * width
    raw = b"".join(b"\x00" + row for _ in range(height))
    idat = zlib.compress(raw, 9)
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) + chunk(b"IDAT", idat) + chunk(b"IEND", b"")


def _pad4(b: bytes, fill: bytes = b"\x00") -> bytes:
    return b + fill * ((4 - len(b) % 4) % 4)


def build_cube() -> tuple[dict, bytes]:
    """Return (gltf_json, bin_blob) for a cube with a base-color + ORM + normal textured material."""
    faces = [
        [( 0.5,-0.5,-0.5),( 0.5, 0.5,-0.5),( 0.5, 0.5, 0.5),( 0.5,-0.5, 0.5)],  # +X
        [(-0.5,-0.5, 0.5),(-0.5, 0.5, 0.5),(-0.5, 0.5,-0.5),(-0.5,-0.5,-0.5)],  # -X
        [(-0.5, 0.5,-0.5),(-0.5, 0.5, 0.5),( 0.5, 0.5, 0.5),( 0.5, 0.5,-0.5)],  # +Y
        [(-0.5,-0.5, 0.5),(-0.5,-0.5,-0.5),( 0.5,-0.5,-0.5),( 0.5,-0.5, 0.5)],  # -Y
        [(-0.5,-0.5, 0.5),( 0.5,-0.5, 0.5),( 0.5, 0.5, 0.5),(-0.5, 0.5, 0.5)],  # +Z
        [( 0.5,-0.5,-0.5),(-0.5,-0.5,-0.5),(-0.5, 0.5,-0.5),( 0.5, 0.5,-0.5)],  # -Z
    ]
    positions: list[tuple[float, float, float]] = []
    uvs: list[tuple[float, float]] = []
    indices: list[int] = []
    for quad in faces:
        base = len(positions)
        positions.extend(quad)
        uvs.extend([(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)])
        indices.extend([base, base + 1, base + 2, base, base + 2, base + 3])

    idx_bytes = _pad4(struct.pack(f"<{len(indices)}H", *indices))
    idx_len = len(struct.pack(f"<{len(indices)}H", *indices))
    pos_bytes = struct.pack(f"<{len(positions) * 3}f", *[c for p in positions for c in p])
    uv_bytes = struct.pack(f"<{len(uvs) * 2}f", *[c for uv in uvs for c in uv])

    # Three images. Family is implied by the SLOT that references each — NOT by any flag here.
    base_png = make_png(2, 2, (200, 120, 60))    # sRGB    — base color (a warm albedo)
    orm_png = make_png(2, 2, (255, 200, 0))      # LINEAR  — ORM: R=occ(1.0) G=rough(~0.78) B=metal(0.0)
    normal_png = make_png(2, 2, (128, 128, 255)) # LINEAR  — flat tangent-space normal (0,0,1)

    parts = [idx_bytes, pos_bytes, uv_bytes, _pad4(base_png), _pad4(orm_png), _pad4(normal_png)]
    offsets, cursor = [], 0
    for p in parts:
        offsets.append(cursor)
        cursor += len(p)
    o_idx, o_pos, o_uv, o_base, o_orm, o_norm = offsets
    blob = b"".join(parts)

    pmin = [min(p[i] for p in positions) for i in range(3)]
    pmax = [max(p[i] for p in positions) for i in range(3)]

    gltf = {
        "asset": {"version": "2.0", "generator": "teach-me gltf-format lesson 04 (make_cube_orm_glb.py, stdlib)"},
        "scene": 0,
        "scenes": [{"nodes": [0]}],
        "nodes": [{"mesh": 0, "name": "CubeORM"}],
        "meshes": [{"primitives": [{"attributes": {"POSITION": 1, "TEXCOORD_0": 2},
                                    "indices": 0, "material": 0}]}],
        "materials": [{
            "name": "CubeORM",
            "pbrMetallicRoughness": {
                "baseColorTexture": {"index": 0, "texCoord": 0},          # sRGB
                "metallicRoughnessTexture": {"index": 1, "texCoord": 0},  # linear (ORM)
                "metallicFactor": 1.0,
                "roughnessFactor": 1.0,
            },
            "normalTexture": {"index": 2, "texCoord": 0, "scale": 1.0},   # linear
            "occlusionTexture": {"index": 1, "texCoord": 0, "strength": 1.0},  # same ORM image, R channel
        }],
        "textures": [
            {"source": 0, "sampler": 0},   # base color
            {"source": 1, "sampler": 0},   # ORM
            {"source": 2, "sampler": 0},   # normal
        ],
        "images": [
            {"bufferView": 3, "mimeType": "image/png"},   # base color (sRGB slot)
            {"bufferView": 4, "mimeType": "image/png"},   # ORM (linear slots)
            {"bufferView": 5, "mimeType": "image/png"},   # normal (linear slot)
        ],
        "samplers": [{"magFilter": 9729, "minFilter": 9987}],
        "buffers": [{"byteLength": len(blob)}],
        "bufferViews": [
            {"buffer": 0, "byteOffset": o_idx, "byteLength": idx_len, "target": 34963},
            {"buffer": 0, "byteOffset": o_pos, "byteLength": len(pos_bytes), "target": 34962},
            {"buffer": 0, "byteOffset": o_uv, "byteLength": len(uv_bytes), "target": 34962},
            {"buffer": 0, "byteOffset": o_base, "byteLength": len(base_png)},
            {"buffer": 0, "byteOffset": o_orm, "byteLength": len(orm_png)},
            {"buffer": 0, "byteOffset": o_norm, "byteLength": len(normal_png)},
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
    json_bytes = _pad4(json_bytes, b" ")                 # pad JSON with 0x20
    blob = _pad4(blob)                                   # pad BIN with 0x00
    body = (struct.pack("<II", len(json_bytes), CHUNK_JSON) + json_bytes
            + struct.pack("<II", len(blob), CHUNK_BIN) + blob)
    out.write_bytes(struct.pack("<III", GLB_MAGIC, 2, 12 + len(body)) + body)


def main() -> int:
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).with_name("cube_orm.glb")
    gltf, blob = build_cube()
    write_glb(gltf, blob, out)
    print(f"wrote {out} ({out.stat().st_size} bytes) — baseColor(sRGB) + "
          f"metallicRoughness/occlusion(linear ORM) + normal(linear)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
