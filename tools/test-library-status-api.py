#!/usr/bin/env python3
"""Library-root status API regression: maps resolve by identity and progress stays local."""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import urllib.request
from pathlib import Path

from playwright.sync_api import sync_playwright

PROJECT_ROOT = Path(__file__).resolve().parent.parent
FIXTURE = PROJECT_ROOT / ".scratch" / "library-status-api"
sys.path.insert(0, str(PROJECT_ROOT / "tools"))

from lib.serve_harness import serve_workspace  # noqa: E402
from map_parser import load_map  # noqa: E402


def _request(url: str, body: dict | None = None) -> dict:
    payload = json.dumps(body).encode() if body is not None else None
    request = urllib.request.Request(url, data=payload, headers={"content-type": "application/json"})
    with urllib.request.urlopen(request, timeout=5) as response:
        return json.loads(response.read())


def _fixture() -> tuple[Path, list[str]]:
    if FIXTURE.exists():
        shutil.rmtree(FIXTURE)
    FIXTURE.mkdir(parents=True)
    shutil.copy2(PROJECT_ROOT / "library" / "index.html", FIXTURE / "index.html")

    domains = []
    for source in (PROJECT_ROOT / "library").iterdir():
        maps = source / "maps"
        if not maps.is_dir():
            continue
        shutil.copytree(maps, FIXTURE / source.name / "maps")
        domains.extend(load_map(path).domain for path in maps.glob("*.MAP.md"))
    shutil.copytree(PROJECT_ROOT / "library" / "gltf-format" / "lessons",
                    FIXTURE / "gltf-format" / "lessons")
    subprocess.run([
        sys.executable,
        str(PROJECT_ROOT / "tools" / "generate_map_page.py"),
        str(FIXTURE / "gltf-format" / "maps" / "gltf-format.MAP.md"),
        "--workspace", str(FIXTURE / "gltf-format"),
        "--output", str(FIXTURE / "gltf-format" / "lessons" / "gltf-format-map.html"),
    ], check=True, cwd=PROJECT_ROOT)
    (FIXTURE / "gltf-format" / "index.html").write_text("<!doctype html>", encoding="utf-8")
    return FIXTURE, sorted(domains)


def _library_root_flow(base_url: str, map_domains: list[str]) -> None:
    for domain in map_domains:
        data = _request(f"{base_url}/api/map/{domain}")
        assert data["domain"] == domain and data["topics"], domain
        topic = data["topics"][0]
        if domain != "gltf-format":
            _request(
                f"{base_url}/api/map/{domain}/{topic['slug']}/status",
                {"status": "in-progress"},
            )

    gltf = _request(f"{base_url}/api/map/gltf-format")
    topic = next(topic for topic in gltf["topics"] if topic["lesson_file"])
    slug = topic["slug"]
    lesson = topic["lesson_file"]
    parsed = load_map(FIXTURE / "gltf-format" / "maps" / "gltf-format.MAP.md")
    current = next(item for item in parsed.topics if item.slug == slug)
    dependent = next(item for item in parsed.topics if slug in item.prereqs)

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(f"{base_url}/gltf-format/lessons/{lesson}", wait_until="domcontentloaded")
        page.get_by_role("button", name="Mark complete").click()
        page.locator(".lesson-actions-bar .done").wait_for()
        page.reload(wait_until="domcontentloaded")
        page.locator(".lesson-actions-bar .done").wait_for()

        status = _request(f"{base_url}/api/map/gltf-format/{slug}/status")
        assert status["status"] == "complete", status

        page.goto(f"{base_url}/gltf-format/lessons/gltf-format-map.html", wait_until="domcontentloaded")
        current_card = page.locator(f'.topic-card[data-topic-id="{current.id}"]')
        current_card.locator(".badge.complete").wait_for()
        page.locator(f'.topic-card[data-topic-id="{dependent.id}"] .prereq-item.met').wait_for()
        page.reload(wait_until="domcontentloaded")
        current_card.locator(".badge.complete").wait_for()
        page.locator(f'.topic-card[data-topic-id="{dependent.id}"] .prereq-item.met').wait_for()

        fallback = browser.new_page()
        errors = []
        fallback.on("pageerror", lambda error: errors.append(error))
        fallback.route("**/api/map/gltf-format", lambda route: route.abort())
        fallback.goto(f"{base_url}/gltf-format/lessons/gltf-format-map.html", wait_until="domcontentloaded")
        fallback.locator(f'.topic-card[data-topic-id="{current.id}"] .badge.not-started').wait_for()
        assert not errors, errors
        fallback.close()
        overlay = _request(f"{base_url}/api/overlay")["overlay"]
        assert len(overlay) == len(map_domains), overlay
        assert sorted(overlay.values()) == ["complete"] + ["in-progress"] * (len(map_domains) - 1)

        page.goto(f"{base_url}/index.html", wait_until="domcontentloaded")
        row = page.locator('.ti-row[data-domain="gltf-format"]')
        row.wait_for()
        assert f"{gltf['topic_count'] - 1} to explore" in row.inner_text()
        browser.close()


def _single_domain_flow(fixture: Path) -> None:
    workspace = fixture / "gltf-format"
    with serve_workspace(str(workspace.relative_to(PROJECT_ROOT)).replace("\\", "/")) as base_url:
        data = _request(f"{base_url}/api/map/gltf-format")
        topic = next(topic for topic in data["topics"] if topic["lesson_file"])
        saved = _request(
            f"{base_url}/api/map/gltf-format/{topic['slug']}/status",
            {"status": "in-progress"},
        )
        assert saved["status"] == "in-progress", saved
    assert (workspace / ".user" / "status-overlay.json").is_file()


def main() -> int:
    fixture, map_domains = _fixture()
    try:
        with serve_workspace(str(fixture.relative_to(PROJECT_ROOT)).replace("\\", "/")) as base_url:
            _library_root_flow(base_url, map_domains)
        assert (fixture / ".user" / "status-overlay.json").is_file()
        assert not (fixture / "gltf-format" / ".user").exists()
        _single_domain_flow(fixture)
    finally:
        shutil.rmtree(fixture, ignore_errors=True)
    print(f"library status API: {len(map_domains)} map domains + browser persistence pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
