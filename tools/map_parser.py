"""
MAP.md parser and data model.

Parses MAP.md files (YAML frontmatter + markdown topic blocks) into a queryable
data structure. Used by the teach skill, generation server, and map page generator.

Usage:
    from tools.map_parser import load_map, validate, get_available_topics, get_next_suggestion, update_status
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Topic:
    slug: str
    title: str
    why: str
    scope: str  # lightweight | substantial | deep
    prereqs: list[str]
    status: str  # not-started | in-progress | complete
    lesson_file: str | None = None


@dataclass
class DomainMap:
    domain: str
    description: str
    depth: int
    parent: str | None
    leads_to: list[str]
    orientation: str
    topics: list[Topic]

    def topic_by_slug(self, slug: str) -> Topic | None:
        for t in self.topics:
            if t.slug == slug:
                return t
        return None


# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------

_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
_TOPIC_HEADER_RE = re.compile(r"^### (.+)$", re.MULTILINE)
_FIELD_RE = re.compile(r"^- \*\*(\w+):\*\*\s*(.+)$", re.MULTILINE)


def _parse_yaml_value(val: str) -> str | int | list[str] | None:
    """Minimal YAML value parser for the subset we use."""
    val = val.strip()
    if val == "null" or val == "~":
        return None
    if val.startswith('"') and val.endswith('"'):
        return val[1:-1]
    if val.startswith("'") and val.endswith("'"):
        return val[1:-1]
    try:
        return int(val)
    except ValueError:
        pass
    return val


def _parse_frontmatter(text: str) -> dict:
    """Parse YAML frontmatter into a dict (simple key: value + list support)."""
    result = {}
    current_key = None
    current_list = None

    for line in text.split("\n"):
        # List continuation
        if line.startswith("  - ") and current_key:
            if current_list is None:
                current_list = []
            current_list.append(line[4:].strip())
            continue
        elif current_key and current_list is not None:
            result[current_key] = current_list
            current_list = None
            current_key = None

        # Key: value
        if ":" in line and not line.startswith(" "):
            key, _, val = line.partition(":")
            key = key.strip()
            val = val.strip()
            if not val:
                # Could be start of a list
                current_key = key
                current_list = []
            else:
                result[key] = _parse_yaml_value(val)
                current_key = None

    # Flush trailing list
    if current_key and current_list is not None:
        result[current_key] = current_list

    return result


def _parse_list_field(val: str) -> list[str]:
    """Parse [item1, item2] or [] from a topic field value."""
    val = val.strip()
    if val == "[]":
        return []
    if val.startswith("[") and val.endswith("]"):
        inner = val[1:-1]
        return [item.strip() for item in inner.split(",") if item.strip()]
    return [val]


def load_map(path: str | Path) -> DomainMap:
    """Load and parse a MAP.md file into a DomainMap."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"MAP.md not found: {path}")

    text = path.read_text(encoding="utf-8")

    # Parse frontmatter
    fm_match = _FRONTMATTER_RE.match(text)
    if not fm_match:
        raise ValueError(f"No valid frontmatter in {path}")

    fm = _parse_frontmatter(fm_match.group(1))
    body = text[fm_match.end():]

    # Extract orientation
    orientation = ""
    orient_match = re.search(
        r"## Orientation\s*\n\n(.+?)(?=\n## |\Z)", body, re.DOTALL
    )
    if orient_match:
        orientation = orient_match.group(1).strip()

    # Extract topics
    topics_section = ""
    topics_match = re.search(r"## Topics\s*\n(.*)", body, re.DOTALL)
    if topics_match:
        topics_section = topics_match.group(1)

    topics = []
    # Split by ### headers
    parts = _TOPIC_HEADER_RE.split(topics_section)
    # parts[0] is before first header (empty), then alternating: slug, content
    for i in range(1, len(parts), 2):
        slug = parts[i].strip()
        content = parts[i + 1] if i + 1 < len(parts) else ""

        fields = {}
        for m in _FIELD_RE.finditer(content):
            fields[m.group(1)] = m.group(2).strip()

        topics.append(Topic(
            slug=slug,
            title=fields.get("title", slug),
            why=fields.get("why", ""),
            scope=fields.get("scope", "substantial"),
            prereqs=_parse_list_field(fields.get("prereqs", "[]")),
            status=fields.get("status", "not-started"),
            lesson_file=fields.get("lesson_file"),
        ))

    return DomainMap(
        domain=fm.get("domain", ""),
        description=fm.get("description", ""),
        depth=fm.get("depth", 0),
        parent=fm.get("parent"),
        leads_to=fm.get("leads_to", []),
        orientation=orientation,
        topics=topics,
    )


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def validate(domain_map: DomainMap) -> list[str]:
    """Validate a DomainMap. Returns list of error strings (empty = valid)."""
    errors = []
    slugs = {t.slug for t in domain_map.topics}

    # Check topic count
    if len(domain_map.topics) > 9:
        errors.append(f"Too many topics: {len(domain_map.topics)} (max 9)")

    # Check undefined prereqs
    for t in domain_map.topics:
        for prereq in t.prereqs:
            if prereq not in slugs:
                errors.append(f"Topic '{t.slug}' has undefined prereq '{prereq}'")

    # Check for cycles (Kahn's algorithm)
    in_degree = {t.slug: 0 for t in domain_map.topics}
    adjacency: dict[str, list[str]] = {t.slug: [] for t in domain_map.topics}
    for t in domain_map.topics:
        for prereq in t.prereqs:
            if prereq in adjacency:
                adjacency[prereq].append(t.slug)
                in_degree[t.slug] += 1

    queue = [s for s, d in in_degree.items() if d == 0]
    visited = 0
    while queue:
        node = queue.pop(0)
        visited += 1
        for neighbor in adjacency[node]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    if visited < len(domain_map.topics):
        errors.append("Cycle detected in topic prerequisites")

    # Check valid status values
    valid_statuses = {"not-started", "in-progress", "complete"}
    for t in domain_map.topics:
        if t.status not in valid_statuses:
            errors.append(f"Topic '{t.slug}' has invalid status '{t.status}'")

    return errors


# ---------------------------------------------------------------------------
# Queries
# ---------------------------------------------------------------------------

def get_available_topics(domain_map: DomainMap) -> list[Topic]:
    """Return topics whose prereqs are all complete or in-progress."""
    satisfied = {t.slug for t in domain_map.topics if t.status in ("complete", "in-progress")}
    available = []
    for t in domain_map.topics:
        if t.status != "not-started":
            continue
        if all(p in satisfied for p in t.prereqs):
            available.append(t)
    return available


def get_next_suggestion(domain_map: DomainMap) -> Topic | None:
    """Suggest the best next topic: available + most downstream dependents."""
    available = get_available_topics(domain_map)
    if not available:
        return None

    # Count how many topics depend (directly or transitively) on each
    def count_dependents(slug: str) -> int:
        """BFS count of topics downstream of slug."""
        dependents = set()
        queue = [slug]
        while queue:
            current = queue.pop(0)
            for t in domain_map.topics:
                if current in t.prereqs and t.slug not in dependents:
                    dependents.add(t.slug)
                    queue.append(t.slug)
        return len(dependents)

    return max(available, key=lambda t: count_dependents(t.slug))


# ---------------------------------------------------------------------------
# Mutation
# ---------------------------------------------------------------------------

def update_status(path: str | Path, topic_slug: str, new_status: str) -> None:
    """Update a topic's status in the MAP.md file without clobbering other content."""
    path = Path(path)
    text = path.read_text(encoding="utf-8")

    valid = {"not-started", "in-progress", "complete"}
    if new_status not in valid:
        raise ValueError(f"Invalid status '{new_status}', must be one of {valid}")

    # Find the topic section and replace its status line
    # Pattern: after "### {slug}" find "- **status:** ..."
    pattern = re.compile(
        rf"(### {re.escape(topic_slug)}\b.*?- \*\*status:\*\*\s*)\S+",
        re.DOTALL,
    )
    new_text, count = pattern.subn(rf"\g<1>{new_status}", text, count=1)
    if count == 0:
        raise ValueError(f"Topic '{topic_slug}' not found in {path}")

    path.write_text(new_text, encoding="utf-8")
