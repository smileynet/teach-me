"""fetch_url.py — Fetch and extract content from a URL with fallback chain.

Fallback chain (from spike #157):
1. Pattern match: raw text URLs → urllib, PDFs → download
2. Default: trafilatura (best for HTML docs/articles)
3. If <100 words: Playwright (JS-rendered sites)

Usage:
    from tools.fetch_url import fetch_url_content
"""

from __future__ import annotations

import re
import urllib.request
from pathlib import Path

import trafilatura

# Minimum word count to consider extraction successful
SUCCESS_THRESHOLD = 100


def fetch_url_content(url: str) -> tuple[str, str]:
    """Fetch URL and extract text content.

    Returns: (extracted_text, format) where format is "markdown"|"html"|"text"|"pdf"
    """
    # Pattern matching: route by URL structure
    if _is_raw_text_url(url):
        text = _fetch_urllib_raw(url)
        fmt = _detect_text_format(url, text)
        return text, fmt

    if _is_pdf_url(url):
        # Download to temp file, caller handles via chunk_pdf
        path = _download_file(url)
        return str(path), "pdf"

    # Default: trafilatura for HTML pages
    text = _fetch_trafilatura(url)
    if len(text.split()) >= SUCCESS_THRESHOLD:
        return text, _detect_extracted_format(text)

    # Fallback: Playwright for JS-rendered pages
    text = _fetch_playwright(url)
    if len(text.split()) >= SUCCESS_THRESHOLD:
        return text, _detect_extracted_format(text)

    # Last resort: urllib + tag strip (noisy but always works)
    text = _fetch_urllib_html(url)
    return text, _detect_extracted_format(text)


def _is_raw_text_url(url: str) -> bool:
    """Detect URLs that serve plain text (not HTML)."""
    patterns = [
        r"raw\.githubusercontent\.com",
        r"gist\.githubusercontent\.com",
        r"\.(md|txt|rst|org)(\?|$)",
    ]
    return any(re.search(p, url) for p in patterns)


def _is_pdf_url(url: str) -> bool:
    """Detect PDF URLs."""
    return url.lower().endswith(".pdf")


def _detect_text_format(url: str, text: str) -> str:
    """Detect if fetched text is markdown, rst, or plain text."""
    if url.endswith(".md") or re.search(r"^#{1,3}\s", text, re.MULTILINE):
        return "markdown"
    return "text"


def _detect_extracted_format(text: str) -> str:
    """Detect whether extracted content is HTML or plain text.

    Trafilatura and Playwright typically return plain text (no tags).
    Route to the correct chunker based on actual content structure.
    """
    # If content has HTML heading tags, it's still HTML
    if re.search(r"<h[1-6][^>]*>", text):
        return "html"
    # If content has markdown headings, treat as markdown
    if re.search(r"^#{1,3}\s", text, re.MULTILINE):
        return "markdown"
    # Otherwise it's extracted plain text (paragraph-based)
    return "text"


def _fetch_urllib_raw(url: str) -> str:
    """Fetch raw text content via urllib."""
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 teach-me"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        return resp.read().decode("utf-8", errors="replace")


def _fetch_urllib_html(url: str) -> str:
    """Fetch HTML and do basic tag stripping."""
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 teach-me"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        html = resp.read().decode("utf-8", errors="replace")

    # Strip script/style/nav/footer
    text = re.sub(
        r"<(script|style|nav|footer|header|aside)[^>]*>.*?</\1>",
        "", html, flags=re.DOTALL | re.IGNORECASE
    )
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _fetch_trafilatura(url: str) -> str:
    """Fetch and extract using trafilatura."""
    downloaded = trafilatura.fetch_url(url)
    if not downloaded:
        return ""
    text = trafilatura.extract(
        downloaded,
        include_comments=False,
        include_tables=True,
        favor_recall=True,
        output_format="txt",
    )
    return text or ""


def _fetch_playwright(url: str) -> str:
    """Fetch using Playwright headless browser (for JS-rendered pages)."""
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, wait_until="networkidle", timeout=20000)
            content = page.evaluate("""() => {
                const el = document.querySelector('main') ||
                           document.querySelector('article') ||
                           document.querySelector('[role="main"]') ||
                           document.body;
                return el ? el.innerText : '';
            }""")
            browser.close()
            return content or ""
    except Exception:
        return ""


def _download_file(url: str) -> Path:
    """Download a file to a temp location."""
    import tempfile
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 teach-me"})
    suffix = ".pdf" if url.lower().endswith(".pdf") else ""
    tmp = Path(tempfile.mktemp(suffix=suffix))
    with urllib.request.urlopen(req, timeout=30) as resp:
        tmp.write_bytes(resp.read())
    return tmp
