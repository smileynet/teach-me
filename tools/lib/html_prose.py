"""html_prose.py — shared lesson-HTML → teaching-prose extraction (#288).

Single source of truth for "strip the chrome, keep the teaching text." Before this,
three copies diverged (hint-coverage-oracle.py, chunk_text.py::chunk_html, and an ad-hoc
regex in check-topic-completeness) — so lesson chrome (the `.lesson-meta` "Win:" statement,
"~N min read", breadcrumb nav) leaked into concept extraction and produced junk "concepts"
like `read win`, `min`. Consolidated here so the chrome definition lives in ONE place.

Two entry points:
  - strip_chrome_blocks(html) -> html : removes chrome CONTAINERS (semantic tags + known
      lesson-chrome classes), returns HTML with the teaching markup intact. Use as a
      front-end before your own heading-split / tag-unwrap (chunk_html does this).
  - html_to_prose(html) -> str : strip_chrome_blocks + unwrap all tags + unescape + collapse
      whitespace, lowercased. A bag-of-words haystack (the hint-coverage oracle uses this).

stdlib only (re + html) — safe for the dependency-free oracle.
"""
from __future__ import annotations

import html as _html
import re

# Chrome containers removed as whole blocks (tag + inner content).
# Semantic chrome tags:
_SEMANTIC_CHROME = ("script", "style", "nav", "header", "footer", "aside")

# Untagged chrome by class — the #288 leak. `.lesson-meta` holds "Lesson N · … · ~N min
# read" + the "Win:" statement; `.page-nav` is the breadcrumb (usually a <nav>, but matched
# by class too for robustness). Matched as a <tag class="…name…">…</tag> block.
_CHROME_CLASSES = ("lesson-meta", "page-nav")


def strip_chrome_blocks(html: str) -> str:
    """Remove chrome container blocks (semantic tags + known chrome classes). Returns HTML."""
    out = html
    for tag in _SEMANTIC_CHROME:
        out = re.sub(rf"<{tag}\b[^>]*>.*?</{tag}>", " ", out, flags=re.DOTALL | re.IGNORECASE)
    # Remove any element whose class attribute contains a chrome class name.
    # Handles <div class="lesson-meta">…</div>, <p class="lesson-meta">…</p>, etc.
    for cls in _CHROME_CLASSES:
        out = re.sub(
            rf'<(\w+)\b[^>]*\bclass="[^"]*\b{re.escape(cls)}\b[^"]*"[^>]*>.*?</\1>',
            " ", out, flags=re.DOTALL | re.IGNORECASE,
        )
    return out


def html_to_prose(html: str) -> str:
    """Chrome-stripped, tag-unwrapped, unescaped, whitespace-collapsed, lowercased prose."""
    text = strip_chrome_blocks(html)
    text = re.sub(r"<[^>]+>", " ", text)      # unwrap remaining tags
    text = _html.unescape(text)
    return re.sub(r"\s+", " ", text).strip().lower()
