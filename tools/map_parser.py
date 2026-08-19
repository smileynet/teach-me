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
class LeadsTo:
    slug: str
    why: str = ""


@dataclass
class DomainMap:
    domain: str
    description: str
    depth: int
    parent: str | None
    leads_to: list[LeadsTo]
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
    current_obj = None

    for line in text.split("\n"):
        # Nested object key (4 spaces or 2 spaces + key: value under a list item)
        if current_obj is not None and line.startswith("    ") and ":" in line:
            k, _, v = line.strip().partition(":")
            current_obj[k.strip()] = _parse_yaml_value(v.strip())
            continue

        # List item that starts an object (- key: value)
        if line.startswith("  - ") and current_key:
            rest = line[4:].strip()
            if ":" in rest and not rest.startswith('"') and not rest.startswith("'"):
                # Object item: - slug: value
                if current_obj is not None:
                    current_list.append(current_obj)
                current_obj = {}
                k, _, v = rest.partition(":")
                current_obj[k.strip()] = _parse_yaml_value(v.strip())
            else:
                # Simple string item
                if current_obj is not None:
                    current_list.append(current_obj)
                    current_obj = None
                if current_list is None:
                    current_list = []
                current_list.append(rest)
            continue

        # Flush pending object/list on new top-level key
        if current_key and (current_list is not None or current_obj is not None):
            if current_obj is not None:
                current_list.append(current_obj)
                current_obj = None
            result[current_key] = current_list
            current_list = None
            current_key = None

        # Key: value
        if ":" in line and not line.startswith(" "):
            key, _, val = line.partition(":")
            key = key.strip()
            val = val.strip()
            if not val:
                # Start of a list
                current_key = key
                current_list = []
            else:
                result[key] = _parse_yaml_value(val)
                current_key = None

    # Flush trailing list/object
    if current_key and (current_list is not None or current_obj is not None):
        if current_obj is not None:
            current_list.append(current_obj)
        result[current_key] = current_list

    return result


def _parse_list_field(val: str) -> list[str]:
    """Parse [item1, item2] or [] from a topic field value."""
    # Strip auto-enrichment comments (e.g., <!-- auto: enrich_prereqs -->)
    val = re.sub(r'<!--.*?-->', '', val).strip()
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

    # Normalize leads_to: can be list of strings or list of dicts
    raw_leads = fm.get("leads_to", [])
    leads_to = []
    for item in raw_leads:
        if isinstance(item, str):
            leads_to.append(LeadsTo(slug=item))
        elif isinstance(item, dict):
            leads_to.append(LeadsTo(slug=item.get("slug", ""), why=item.get("why", "")))

    return DomainMap(
        domain=fm.get("domain", ""),
        description=fm.get("description", ""),
        depth=fm.get("depth", 0),
        parent=fm.get("parent"),
        leads_to=leads_to,
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

import threading
_write_lock = threading.Lock()


def update_status(path: str | Path, topic_slug: str, new_status: str) -> None:
    """Update a topic's status in the MAP.md file without clobbering other content."""
    path = Path(path)

    valid = {"not-started", "in-progress", "complete"}
    if new_status not in valid:
        raise ValueError(f"Invalid status '{new_status}', must be one of {valid}")

    with _write_lock:
        text = path.read_text(encoding="utf-8")

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


# ---------------------------------------------------------------------------
# Sub-map Navigation (Zoom)
# ---------------------------------------------------------------------------

MAX_DEPTH = 3


def find_child_map(maps_dir: str | Path, topic_slug: str) -> Path | None:
    """Find an existing child MAP.md for a topic slug.

    Searches for:
      - {topic_slug}.MAP.md (depth 1 child of a depth-0 root)
      - Any file matching *--{topic_slug}.MAP.md (deeper children)
    """
    maps_dir = Path(maps_dir)
    if not maps_dir.is_dir():
        return None

    # Direct match: topic_slug.MAP.md
    direct = maps_dir / f"{topic_slug}.MAP.md"
    if direct.exists():
        return direct

    # Deeper match: parent--topic_slug.MAP.md
    for f in maps_dir.glob(f"*--{topic_slug}.MAP.md"):
        return f

    return None


def get_parent_map(maps_dir: str | Path, domain_map: DomainMap) -> Path | None:
    """Find the parent MAP.md for a given domain map using its `parent` field.

    Scans maps_dir for a MAP.md whose domain matches the parent field.
    """
    maps_dir = Path(maps_dir)
    if not maps_dir.is_dir() or domain_map.parent is None:
        return None

    for f in maps_dir.glob("*.MAP.md"):
        try:
            parent = load_map(f)
            if parent.domain == domain_map.parent:
                return f
        except (ValueError, FileNotFoundError):
            continue

    return None


def resolve_map_filename(parent_domain: str, topic_slug: str, depth: int) -> str:
    """Compute the filename for a new sub-map at a given depth.

    Naming convention (flat in maps/):
      depth 0: {domain}.MAP.md
      depth 1: {topic_slug}.MAP.md
      depth 2+: {parent_topic}--{topic_slug}.MAP.md

    The parent_domain arg is only used at depth 0 (root map creation).
    For depth 1+, we use the topic slug directly.
    """
    if depth == 0:
        return f"{parent_domain}.MAP.md"
    return f"{topic_slug}.MAP.md"


def get_breadcrumb_chain(maps_dir: str | Path, domain_map: DomainMap) -> list[tuple[str, Path | None]]:
    """Build a breadcrumb chain from root to the current map.

    Returns: list of (title, map_file_path) tuples from root to current.
    The last entry (current) has path=None (it's the active page).
    """
    maps_dir = Path(maps_dir)
    chain: list[tuple[str, Path | None]] = []

    # Walk up from current to root
    current = domain_map
    ancestors: list[tuple[str, Path | None]] = []

    while current.parent is not None:
        parent_path = get_parent_map(maps_dir, current)
        if parent_path is None:
            # Can't resolve further — use domain name as label
            ancestors.append((current.parent.replace("-", " ").title(), None))
            break
        parent_map = load_map(parent_path)
        ancestors.append((parent_map.domain.replace("-", " ").title(), parent_path))
        current = parent_map

    # Reverse to get root-first order, then append current
    ancestors.reverse()
    chain = ancestors
    chain.append((domain_map.domain.replace("-", " ").title(), None))
    return chain


def has_child_maps(maps_dir: str | Path, domain_map: DomainMap) -> dict[str, Path]:
    """For each topic in the map, check if a child sub-map exists.

    Returns: dict mapping topic_slug → child MAP.md path (only for those that have one).
    """
    maps_dir = Path(maps_dir)
    result = {}
    for topic in domain_map.topics:
        child = find_child_map(maps_dir, topic.slug)
        if child is not None:
            result[topic.slug] = child
    return result


def can_zoom_in(domain_map: DomainMap) -> bool:
    """Whether this map's topics can have sub-maps (depth < MAX_DEPTH)."""
    return domain_map.depth < MAX_DEPTH
