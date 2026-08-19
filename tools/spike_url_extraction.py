#!/usr/bin/env python3
"""Spike: compare URL content extraction methods.

Tests urllib (tag stripping), trafilatura, and Playwright against real URLs.
Measures word count, noise, code preservation, and speed.

Usage:
    python tools/spike_url_extraction.py
"""

from __future__ import annotations

import re
import sys
import time
import urllib.request
from dataclasses import dataclass
from pathlib import Path

import trafilatura


# =============================================================================
# Test URLs
# =============================================================================

TEST_URLS = [
    {
        "name": "Static docs (Redis persistence)",
        "url": "https://redis.io/docs/latest/operate/oss_and_stack/management/persistence/",
        "type": "static_docs",
        "expect_code": True,
    },
    {
        "name": "Technical article (GitHub blog)",
        "url": "https://github.blog/engineering/architecture-optimization/scaling-git-at-github/",
        "type": "article",
        "expect_code": True,
    },
    {
        "name": "Raw markdown (GitHub)",
        "url": "https://raw.githubusercontent.com/networkx/networkx/main/README.rst",
        "type": "raw_text",
        "expect_code": False,
    },
    {
        "name": "MDN reference (static HTML)",
        "url": "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Promise",
        "type": "static_docs",
        "expect_code": True,
    },
]


# =============================================================================
# Extraction methods
# =============================================================================

@dataclass
class ExtractionResult:
    method: str
    url_name: str
    word_count: int
    has_code_blocks: bool
    noise_indicators: int  # count of nav/footer-like fragments
    elapsed_ms: int
    first_100_words: str
    success: bool
    error: str = ""


def _count_noise(text: str) -> int:
    """Count indicators of navigation/boilerplate that leaked through."""
    noise_patterns = [
        r"skip to content",
        r"sign (in|up)",
        r"cookie",
        r"privacy policy",
        r"terms of (use|service)",
        r"©\s*\d{4}",
        r"all rights reserved",
        r"subscribe",
        r"newsletter",
        r"follow us",
    ]
    count = 0
    text_lower = text.lower()
    for p in noise_patterns:
        count += len(re.findall(p, text_lower))
    return count


def _has_code(text: str) -> bool:
    """Detect if code blocks survived extraction."""
    indicators = [
        r"```",           # fenced code blocks
        r"    \w+",       # indented code (4 spaces)
        r"def \w+\(",     # Python function
        r"function \w+",  # JS function
        r"\w+\.\w+\(",   # method calls
        r"import \w+",    # import statements
        r"const \w+",     # JS const
    ]
    for p in indicators:
        if re.search(p, text):
            return True
    return False


def extract_urllib(url: str) -> tuple[str, float]:
    """Extract using urllib + basic tag stripping."""
    start = time.time()
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 teach-me-spike"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        html = resp.read().decode("utf-8", errors="replace")

    # Strip script/style tags entirely
    text = re.sub(r"<(script|style|nav|footer|header)[^>]*>.*?</\1>", "", html, flags=re.DOTALL | re.IGNORECASE)
    # Strip remaining tags
    text = re.sub(r"<[^>]+>", " ", text)
    # Collapse whitespace
    text = re.sub(r"\s+", " ", text).strip()
    elapsed = (time.time() - start) * 1000
    return text, elapsed


def extract_trafilatura(url: str) -> tuple[str, float]:
    """Extract using trafilatura."""
    start = time.time()
    downloaded = trafilatura.fetch_url(url)
    if not downloaded:
        return "", (time.time() - start) * 1000

    text = trafilatura.extract(
        downloaded,
        include_comments=False,
        include_tables=True,
        favor_recall=True,
        output_format="txt",
    )
    elapsed = (time.time() - start) * 1000
    return text or "", elapsed


def extract_playwright(url: str) -> tuple[str, float]:
    """Extract using Playwright headless browser."""
    start = time.time()
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, wait_until="networkidle", timeout=15000)
            # Get text content from main/article, fall back to body
            content = page.evaluate("""() => {
                const el = document.querySelector('main') ||
                           document.querySelector('article') ||
                           document.querySelector('[role="main"]') ||
                           document.body;
                return el ? el.innerText : '';
            }""")
            browser.close()
    except Exception as e:
        return f"ERROR: {e}", (time.time() - start) * 1000

    elapsed = (time.time() - start) * 1000
    return content or "", elapsed


# =============================================================================
# Runner
# =============================================================================

METHODS = {
    "urllib": extract_urllib,
    "trafilatura": extract_trafilatura,
    "playwright": extract_playwright,
}


def run_comparison() -> list[ExtractionResult]:
    results = []

    for test in TEST_URLS:
        print(f"\n{'─'*60}")
        print(f"Testing: {test['name']}")
        print(f"URL: {test['url']}")
        print(f"{'─'*60}")

        for method_name, method_fn in METHODS.items():
            try:
                text, elapsed = method_fn(test["url"])
                words = text.split()
                word_count = len(words)
                first_100 = " ".join(words[:100])
                noise = _count_noise(text)
                has_code = _has_code(text)
                success = word_count >= 50  # minimum viable extraction

                result = ExtractionResult(
                    method=method_name,
                    url_name=test["name"],
                    word_count=word_count,
                    has_code_blocks=has_code,
                    noise_indicators=noise,
                    elapsed_ms=int(elapsed),
                    first_100_words=first_100[:200],
                    success=success,
                )
            except Exception as e:
                result = ExtractionResult(
                    method=method_name,
                    url_name=test["name"],
                    word_count=0,
                    has_code_blocks=False,
                    noise_indicators=0,
                    elapsed_ms=0,
                    first_100_words="",
                    success=False,
                    error=str(e)[:100],
                )

            results.append(result)
            status = "✓" if result.success else "✗"
            code = "code✓" if result.has_code_blocks else "no-code"
            print(f"  {status} {method_name:12} │ {result.word_count:>5} words │ {result.elapsed_ms:>4}ms │ noise:{result.noise_indicators} │ {code}")
            if result.error:
                print(f"    ERROR: {result.error}")

    return results


def print_summary(results: list[ExtractionResult]):
    print(f"\n{'═'*60}")
    print("SUMMARY: Decision Matrix")
    print(f"{'═'*60}\n")

    # Group by URL
    urls = {}
    for r in results:
        urls.setdefault(r.url_name, []).append(r)

    print(f"{'Source':<35} {'Best Method':<14} {'Reason'}")
    print(f"{'─'*35} {'─'*14} {'─'*40}")

    for url_name, url_results in urls.items():
        # Score each method: word_count (high=good) - noise*50 (high=bad), penalize failures
        scored = []
        for r in url_results:
            if not r.success:
                score = -1000
            else:
                score = r.word_count - (r.noise_indicators * 100)
                # Bonus for code preservation on code-expected pages
                if r.has_code_blocks:
                    score += 200
                # Penalty for being slow (diminishing — speed matters less than quality)
                if r.elapsed_ms > 3000:
                    score -= 100
            scored.append((r, score))

        best = max(scored, key=lambda x: x[1])
        runner_up = sorted(scored, key=lambda x: x[1], reverse=True)[1] if len(scored) > 1 else None

        reason_parts = []
        if best[0].word_count > 0:
            reason_parts.append(f"{best[0].word_count}w")
        if best[0].has_code_blocks:
            reason_parts.append("code✓")
        if best[0].noise_indicators == 0:
            reason_parts.append("clean")
        reason_parts.append(f"{best[0].elapsed_ms}ms")
        reason = ", ".join(reason_parts)

        print(f"{url_name:<35} {best[0].method:<14} {reason}")

    # Overall recommendation
    print(f"\n{'═'*60}")
    print("RECOMMENDED FALLBACK CHAIN:")
    print(f"{'═'*60}")
    print("""
  1. Check Content-Type / URL pattern:
     - .pdf → download, route to chunk_pdf
     - raw.githubusercontent.com → urllib (plain text)
     - Known JS-heavy sites → Playwright directly

  2. Default chain (try in order, stop on success):
     a. trafilatura (best F1 for article extraction)
     b. If word_count < 100: Playwright (page needs JS rendering)
     c. urllib as last resort (always succeeds, may be noisy)

  3. Success threshold: extracted text ≥ 200 words
     (below that, escalate to next method)
""")

    # Dependency recommendation
    traf_results = [r for r in results if r.method == "trafilatura"]
    traf_successes = sum(1 for r in traf_results if r.success)
    print(f"Trafilatura success rate: {traf_successes}/{len(traf_results)}")
    if traf_successes >= len(traf_results) * 0.6:
        print("→ RECOMMENDATION: Add trafilatura as dependency (good hit rate, lightweight)")
    else:
        print("→ RECOMMENDATION: Skip trafilatura (insufficient advantage over urllib)")


def main():
    print("═" * 60)
    print("SPIKE: URL Content Extraction Comparison")
    print("═" * 60)

    results = run_comparison()
    print_summary(results)


if __name__ == "__main__":
    main()
