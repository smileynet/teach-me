---
name: browse-and-verify
description: "Browse a URL with Playwright to validate links, find page sections, and extract content for quiz sources. Trigger: validate link, check this URL, find the section, browse page, what does this page say about, verify source."
metadata:
  type: protocol
  invocation: both
  practice: null
---

# Browse and Verify

Dispatch to the **browser** specialist agent (`.kiro/agents/browser.json`) for URL validation, section extraction, and heading discovery. The browser agent has the Playwright MCP configured — the default agent does NOT load Playwright (40+ tools would degrade tool selection).

## Setup

The browser agent is at `.kiro/agents/browser.json` with `@playwright/mcp` configured headless. Dispatch to it for any browsing task rather than loading Playwright in the main context.

If the browser agent is unavailable, fall back to the `web_fetch` tool (built-in, no MCP needed).

## When to use

- **Before adding a quiz source link**: navigate to the URL, verify the page loads and the content exists
- **When finding the right section to link**: browse the page and look for heading IDs/anchors
- **When writing explanations**: read the relevant section to ground your explanation in the source
- **When a learner questions a source**: re-read the section to confirm accuracy

## Workflow: Validate and find the right section

1. **Navigate** to the page URL
2. **Check the snapshot** — does the page load? Is the content relevant?
3. **Find headings** — look for section IDs in the accessibility snapshot to construct `#anchor` links
4. **Read the section** — confirm the content actually answers/addresses the quiz question
5. **Write the source entry** with the specific URL#anchor, label, and section description

## Quality rules for quiz source links

1. **Always browse before committing** — dead links and irrelevant pages erode trust
2. **Link to the most specific section** — use `#anchor` IDs from headings
3. **Read the section** to confirm it actually helps answer the question
4. **Write the `section` field** based on what you read, not assumptions
5. **If no good anchor exists**, link to the page and describe which paragraph is relevant
6. **Never link to generic overviews** — the linked page must significantly help answer the specific question
7. **Multiple targeted links > one vague link** — e.g., both the spec section AND the AWS implementation docs

## Fallback: web_fetch

When Playwright MCP is not configured or the page is simple (static HTML, no JS rendering needed):

```
web_fetch url="https://iceberg.apache.org/spec/" search_terms="manifest lists" mode="selective"
```

This returns ~10 lines around matches. Sufficient for validation but won't find heading IDs as reliably.

## Escalation Decision Tree

**Default to `web_fetch` first** — it's faster (no browser startup) and sufficient for most documentation pages:

1. Try `web_fetch` with `search_terms` (selective mode)
2. If content is empty or minimal (JS-rendered page): escalate to Playwright
3. If you need heading IDs / anchor discovery: escalate to Playwright
4. If the page requires interaction (login, cookie consent, expand sections): Playwright required

| Page type | Tool | Why |
|-----------|------|-----|
| Static docs (most sources) | `web_fetch` | Fast, sufficient |
| AWS docs (some JS-rendered) | Playwright | Content loads dynamically |
| Pages needing `#anchor` discovery | Playwright | Accessibility snapshot shows heading refs |
| Any page where fetch returns empty | Playwright | JS rendering needed |

## When NOT to use Playwright

- **Page is static HTML** and you only need to check if it loads → use `web_fetch` in `truncated` mode
- **You need a HEAD request** (just check HTTP status) → `web_fetch` is lighter
- **Content is already in your context** from a prior fetch → don't re-browse
