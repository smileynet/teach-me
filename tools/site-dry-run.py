#!/usr/bin/env python3
"""site-dry-run.py (#280) — assemble _site via the SHARED assembler + assert deploy invariants.

The GitHub Pages deploy only fires on a v* tag, so the _site assembly + the /{repo}/ subpath
were never exercised before release. This runs the SAME `tools/assemble-site.sh` the deploy
uses (no re-implementation → no drift) into a temp dir, then asserts what must hold post-#279
(demo-status.json fixtures ship; .user/ never does) and post-#281 (all per-domain indexes
present; the missing-index redirect fallback reaches its sibling map), plus the
ADR-0015 document-relative asset invariant on the subpath.

Requires bash (git-bash on Windows). Exits 0 = all assertions pass, 1 = a failure.
"""
from __future__ import annotations

# Windows consoles default to cp1252; force UTF-8 so ✓/→ glyphs don't crash (#265).
import sys as _sys
if hasattr(_sys.stdout, "reconfigure"):
    _sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(_sys.stderr, "reconfigure"):
    _sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import re
import shutil
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
ASSEMBLER = PROJECT_ROOT / "tools" / "assemble-site.sh"


def _bash() -> str:
    """Locate a bash (git-bash on Windows)."""
    for cand in ("bash", r"C:\Program Files\Git\bin\bash.exe", r"C:\Program Files\Git\usr\bin\bash.exe"):
        if shutil.which(cand) or Path(cand).exists():
            return cand
    return "bash"


class Checks:
    def __init__(self) -> None:
        self.results: list[tuple[bool, str]] = []

    def check(self, ok: bool, label: str) -> None:
        self.results.append((bool(ok), label))

    def report(self) -> int:
        for ok, label in self.results:
            print(f"  {'✓' if ok else '✗'} {label}")
        failed = [l for ok, l in self.results if not ok]
        if failed:
            print(f"\n✗ {len(failed)} deploy assertion(s) failed", file=sys.stderr)
            return 1
        print(f"\n✓ deploy dry-run passed ({len(self.results)} assertions)")
        return 0


def _grep_root_relative_assets(site: Path) -> list[str]:
    """Find root-relative asset refs (href/src/url = /assets…) — they 404 on the /{repo}/
    subpath (ADR-0015 mandates document-relative ../assets). Returns offending files."""
    pat = re.compile(r'(?:href|src)\s*=\s*"/(?:assets|library)/|url\(\s*/assets/')
    bad = []
    for html in site.rglob("*.html"):
        try:
            if pat.search(html.read_text(encoding="utf-8", errors="replace")):
                bad.append(str(html.relative_to(site)))
        except OSError:
            pass
    return bad


def _missing_index_fallback(scratch: Path) -> tuple[bool, str]:
    """Exercise the assembler's fallback in an isolated one-domain source tree."""
    domains = [d for d in (PROJECT_ROOT / "library").iterdir()
               if d.is_dir() and (d / "lessons").is_dir()
               and (d / "lessons" / f"{d.name}-map.html").is_file()]
    if not domains:
        return False, "missing-index fallback fixture has no domain map source"

    domain = domains[0]
    source = scratch / "fallback-source"
    output = source / "_site"
    shutil.copytree(PROJECT_ROOT / "assets", source / "assets")
    shutil.copytree(domain, source / "library" / domain.name)
    (source / "tools").mkdir()
    shutil.copy2(ASSEMBLER, source / "tools" / ASSEMBLER.name)

    index = source / "library" / domain.name / "lessons" / "index.html"
    index.unlink(missing_ok=True)
    result = subprocess.run(
        [_bash(), f"tools/{ASSEMBLER.name}", "_site"],
        cwd=str(source), capture_output=True, text=True,
    )
    stub = output / "library" / domain.name / "lessons" / "index.html"
    target = stub.parent / f"{domain.name}-map.html"
    expected = f"url={domain.name}-map.html"
    ok = result.returncode == 0 and target.is_file() and stub.is_file()
    if ok:
        ok = expected in stub.read_text(encoding="utf-8", errors="replace")
    return ok, f"missing-index fallback targets existing lessons/{domain.name}-map.html"


def main() -> int:
    if not ASSEMBLER.exists():
        print(f"✗ assembler not found: {ASSEMBLER}", file=sys.stderr)
        return 2

    # Use a repo-relative output dir so git-bash never needs an absolute drive-mount path
    # (driving git-bash with D:\ / /d/ absolute paths from a subprocess is fragile — the
    # drive isn't auto-mounted in a non-interactive invocation). Clean it ourselves.
    site_rel = ".scratch/site-dry-run/_site"
    site = PROJECT_ROOT / ".scratch" / "site-dry-run" / "_site"
    if site.parent.exists():
        shutil.rmtree(site.parent, ignore_errors=True)
    try:
        # 1. Assemble via the SHARED script (the exact deploy logic). Relative output path
        #    keeps bash on repo-relative resolution — no drive mount needed.
        r = subprocess.run([_bash(), "tools/assemble-site.sh", site_rel],
                           cwd=str(PROJECT_ROOT), capture_output=True, text=True)
        if r.returncode != 0:
            print(f"✗ assemble-site.sh failed:\n{r.stdout}\n{r.stderr}", file=sys.stderr)
            return 1

        c = Checks()

        # 2. Structure: root redirect + .nojekyll + shared assets.
        idx = site / "index.html"
        c.check(idx.is_file() and 'url=library/index.html' in idx.read_text(encoding="utf-8"),
                "root index.html redirects to library/index.html")
        c.check((site / ".nojekyll").is_file(), ".nojekyll present (Jekyll bypass)")
        c.check((site / "assets").is_dir(), "shared assets/ at deploy root")
        c.check((site / "library" / "index.html").is_file(), "aggregate library/index.html present")
        c.check((site / "library" / "global-map.html").is_file(), "global-map.html redirect stub present")

        # 3. Per-domain indexes (#281): every domain with lessons/ ships an index; the
        #    missing-index redirect loop writes ZERO stubs for the committed corpus. A "stub" is the
        #    redirect signature (<title>Lessons</title> + meta-refresh to a -map.html).
        domain_dirs = [d for d in (site / "library").iterdir()
                       if d.is_dir() and (d / "lessons").is_dir()]
        indexes = [d / "lessons" / "index.html" for d in domain_dirs]
        c.check(all(i.is_file() for i in indexes),
                f"all {len(domain_dirs)} per-domain lessons/index.html present")
        stubs = [i for i in indexes
                 if "<title>Lessons</title>" in i.read_text(encoding="utf-8", errors="replace")]
        c.check(len(stubs) == 0, "no redirect stubs written (all real per-domain indexes shipped)")

        # 4. Demo fixtures ship / .user never does (post-#279 — INVERSE of the stale ticket AC).
        demo = list((site / "library").glob("*/demo-status.json"))
        c.check(len(demo) == 3, f"demo-status.json fixtures ship ({len(demo)} found, expect 3)")
        c.check(not list(site.rglob(".user")), "no .user/ directory anywhere in _site")

        # 5. Subpath asset invariant (ADR-0015): no root-relative /assets refs (they'd 404
        #    under /{repo}/); assets resolve document-relative.
        leaks = _grep_root_relative_assets(site)
        c.check(not leaks, "no root-relative /assets refs (ADR-0015 subpath-safe)"
                + (f" — leaks: {leaks[:3]}" if leaks else ""))

        # 6. No symlinks in the artifact (GitHub Pages rejects them; cp -rL should deref).
        symlinks = [str(p.relative_to(site)) for p in site.rglob("*") if p.is_symlink()]
        c.check(not symlinks, "no symlinks in the artifact"
                + (f" — found: {symlinks[:3]}" if symlinks else ""))

        # 7. Exercise the dormant fallback in an isolated scratch source tree. This proves
        #    the generated redirect reaches the sibling map file instead of merely matching
        #    a shell-script string.
        c.check(*_missing_index_fallback(site.parent))

        return c.report()
    finally:
        shutil.rmtree(site.parent, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main())
