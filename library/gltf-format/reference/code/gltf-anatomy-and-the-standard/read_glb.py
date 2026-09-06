#!/usr/bin/env python3
"""read_glb.py — parse a .glb or .gltf with the Python standard library alone.

Companion artifact for lesson 01 (gltf-anatomy-and-the-standard). Proves the mental
model the lesson teaches — scenes -> nodes -> meshes -> accessors -> bufferViews ->
buffers — on a real file, using nothing but `struct` and `json` (no pygltflib, no
trimesh). Run it on the triangle fixture:

    python read_glb.py triangle.glb
    python read_glb.py triangle.gltf

It prints the object-graph summary, then ASSERTS the structural contracts the lesson
walks through. "It loaded" is not enough — the asserts are what make it *correct*.

Exit codes: 0 = parsed + all asserts hold, 1 = an assert failed, 2 = not a glTF/GLB.
"""
from __future__ import annotations

import json
import struct
import sys

# --- GLB container constants (Khronos glTF 2.0 spec, section 4.4) ---
GLB_MAGIC = 0x46546C67   # the four bytes 'glTF', read little-endian
CHUNK_JSON = 0x4E4F534A  # 'JSON'
CHUNK_BIN = 0x004E4942   # 'BIN\0'


def load_gltf(path: str) -> tuple[dict, bytes | None]:
    """Return (gltf_json_dict, binary_blob_or_None) for a .glb or .gltf file — stdlib only."""
    with open(path, "rb") as f:
        data = f.read()

    # A .gltf file *is* JSON — no container to unwrap.
    if data[:4] != b"glTF":
        return json.loads(data), None

    # A .glb file is a tiny little-endian binary container:
    #   12-byte header (magic, version, total length) + length-prefixed chunks.
    if len(data) < 12:
        raise ValueError("file too small to be a GLB")
    magic, version, total_len = struct.unpack_from("<III", data, 0)
    if magic != GLB_MAGIC:
        raise ValueError(f"bad GLB magic 0x{magic:08X} (expected 'glTF')")
    if version != 2:
        raise ValueError(f"GLB container version {version} != 2 (this is not glTF 2.0)")
    if total_len != len(data):
        raise ValueError(f"header length {total_len} != actual file size {len(data)}")

    gltf: dict | None = None
    blob: bytes | None = None
    offset = 12
    while offset < total_len:
        chunk_len, chunk_type = struct.unpack_from("<II", data, offset)
        offset += 8
        payload = data[offset:offset + chunk_len]
        offset += chunk_len
        if chunk_type == CHUNK_JSON:
            gltf = json.loads(payload)     # trailing 0x20 space padding is valid JSON whitespace
        elif chunk_type == CHUNK_BIN:
            blob = payload
        # Any other chunk type is a future extension — the spec says: ignore it.

    if gltf is None:
        raise ValueError("GLB has no JSON chunk")
    return gltf, blob


def assert_structure(g: dict) -> list[str]:
    """Assert the structural contracts lesson 01 teaches. Returns a list of failures (empty = pass)."""
    errors: list[str] = []
    accessors = g.get("accessors", [])
    buffer_views = g.get("bufferViews", [])

    # asset.version is the ASSET version ("2.0") — distinct from the GLB *container* version (2).
    if g.get("asset", {}).get("version") != "2.0":
        errors.append(f"asset.version {g.get('asset', {}).get('version')!r} != '2.0'")

    # The scene graph must actually contain something.
    if not g.get("meshes") and not g.get("nodes"):
        errors.append("no nodes and no meshes (empty scene?)")

    # Referential integrity: every accessor points at a real bufferView (unless it's sparse).
    for i, acc in enumerate(accessors):
        bv = acc.get("bufferView")
        if bv is not None and not (0 <= bv < len(buffer_views)):
            errors.append(f"accessor[{i}].bufferView {bv} out of range")

    # Every primitive's indices/POSITION point at a real accessor.
    for mi, mesh in enumerate(g.get("meshes", [])):
        for pi, prim in enumerate(mesh.get("primitives", [])):
            idx = prim.get("indices")
            if idx is not None and not (0 <= idx < len(accessors)):
                errors.append(f"mesh[{mi}].primitive[{pi}].indices {idx} out of range")
            for name, a in prim.get("attributes", {}).items():
                if not (0 <= a < len(accessors)):
                    errors.append(f"mesh[{mi}].primitive[{pi}].{name} {a} out of range")

    return errors


def summarize(g: dict, blob: bytes | None) -> None:
    """Print the object graph the way the lesson diagrams it."""
    c = {k: len(g.get(k, [])) for k in
         ("scenes", "nodes", "meshes", "accessors", "bufferViews", "buffers")}
    print(f"  asset.version: {g.get('asset', {}).get('version')}")
    print(f"  graph: {c['scenes']} scene(s) -> {c['nodes']} node(s) -> {c['meshes']} mesh(es)")
    print(f"  data:  {c['accessors']} accessor(s) -> {c['bufferViews']} bufferView(s) "
          f"-> {c['buffers']} buffer(s)")
    if blob is not None:
        print(f"  BIN chunk: {len(blob)} bytes")
    for i, acc in enumerate(g.get("accessors", [])):
        print(f"    accessor[{i}]: {acc.get('type')} {acc.get('componentType')} "
              f"x{acc.get('count')}  (bufferView {acc.get('bufferView')})")


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: python read_glb.py <file.glb|file.gltf>", file=sys.stderr)
        return 2
    path = sys.argv[1]
    try:
        gltf, blob = load_gltf(path)
    except (ValueError, OSError) as exc:
        print(f"read_glb: {path} is not a parseable glTF/GLB: {exc}", file=sys.stderr)
        return 2

    print(f"Parsed {path}:")
    summarize(gltf, blob)

    errors = assert_structure(gltf)
    if errors:
        print("\nFAIL:")
        for e in errors:
            print(f"  - {e}")
        return 1
    print("\nread_glb: all structural contracts hold.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
