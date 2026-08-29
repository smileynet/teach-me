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

try:
    from tools.lib import ulid
except ModuleNotFoundError:  # when tools/ is on sys.path directly
    from lib import ulid  # type: ignore[no-redef]


@dataclass
class Topic:
    slug: str
    title: str
    why: str
    scope: str  # lightweight | substantial | deep
    prereqs: list[str]  # authored prerequisite slugs (round-trip surface; edges derive from these)
    status: str  # not-started | in-progress | complete
    lesson_file: str | None = None
    id: str = ""  # immutable ULID; minted on parse if absent, persisted by migration (#257)
    aliases: list[str] = field(default_factory=list)  # former slugs, for rename resolution


@dataclass
class LeadsTo:
    slug: str
    why: str = ""


# Closed edge-type vocabulary (ADR-0014). prereq: informational (cycle-checked);
# leads_to: navigational; related: symmetric adjacency (reverse derived).
EDGE_TYPES = ("prereq", "leads_to", "related")


@dataclass
class Edge:
    source_id: str  # ULID of source topic
    target_id: str  # ULID of target topic
    type: str  # one of EDGE_TYPES
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
    title: str = ""  # the '# Heading' of the MAP.md; falls back to domain if absent
    edges: list[Edge] = field(default_factory=list)  # derived, ID-keyed (source of truth for graph)

    def topic_by_slug(self, slug: str) -> Topic | None:
        for t in self.topics:
            if t.slug == slug:
                return t
        return None

    def topic_by_id(self, tid: str) -> Topic | None:
        for t in self.topics:
            if t.id == tid:
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


def _parse_edge_blocks(section: str) -> list[dict]:
    """Parse a `## Edges` section: a block-style list of {from, to, type, why} objects.

    Each edge is a stanza beginning with `- from: <slug>` followed by indented
    `to:`/`type:`/`why:` lines. Values may be quoted. Lines outside a stanza are ignored.
    """
    edges: list[dict] = []
    current: dict | None = None
    for line in section.split("\n"):
        stripped = line.strip()
        if not stripped:
            continue
        # New stanza: "- key: value"
        if stripped.startswith("- "):
            if current:
                edges.append(current)
            current = {}
            stripped = stripped[2:].strip()
        if current is None:
            continue
        if ":" in stripped:
            k, _, v = stripped.partition(":")
            current[k.strip()] = v.strip().strip('"').strip("'")
    if current:
        edges.append(current)
    return edges


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

    # Extract the '# Heading' title (first-level heading in the body; "" if absent)
    title_match = re.search(r"^# (.+)$", body, re.MULTILINE)
    title = title_match.group(1).strip() if title_match else ""

    # Extract orientation
    orientation = ""
    orient_match = re.search(
        r"## Orientation\s*\n\n(.+?)(?=\n## |\Z)", body, re.DOTALL
    )
    if orient_match:
        orientation = orient_match.group(1).strip()

    # Extract topics (bounded — stop at the next '## ' heading, e.g. '## Edges')
    topics_section = ""
    topics_match = re.search(r"## Topics\s*\n(.*?)(?=\n## |\Z)", body, re.DOTALL)
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

        tid = fields.get("id", "")
        if not ulid.is_valid(tid):
            tid = ulid.new()  # ephemeral mint so the graph still loads; migration persists it

        topics.append(Topic(
            slug=slug,
            title=fields.get("title", slug),
            why=fields.get("why", ""),
            scope=fields.get("scope", "substantial"),
            prereqs=_parse_list_field(fields.get("prereqs", "[]")),
            status=fields.get("status", "not-started"),
            lesson_file=fields.get("lesson_file"),
            id=tid,
            aliases=_parse_list_field(fields.get("aliases", "[]")),
        ))

    # slug/alias -> id index (edges are authored by slug, resolved to ids here)
    slug_to_id: dict[str, str] = {}
    for t in topics:
        slug_to_id[t.slug] = t.id
        for a in t.aliases:
            slug_to_id.setdefault(a, t.id)

    # Synthesize edges. Prereq edges come from each topic's authored `prereqs`; typed
    # edges (prereq/leads_to/related) may also be authored in a `## Edges` section.
    edges: list[Edge] = []
    seen: set[tuple[str, str, str]] = set()

    def _add_edge(src_id: str, tgt_id: str, etype: str, why: str = "") -> None:
        key = (src_id, tgt_id, etype)
        if src_id and tgt_id and key not in seen:
            seen.add(key)
            edges.append(Edge(source_id=src_id, target_id=tgt_id, type=etype, why=why))

    for t in topics:
        for pslug in t.prereqs:
            src = slug_to_id.get(pslug)  # None if dangling — validate() reports by slug
            if src:
                _add_edge(src, t.id, "prereq")

    # Optional `## Edges` section: block-style list of {from, to, type, why} authored by slug.
    edges_match = re.search(r"## Edges\s*\n(.*?)(?=\n## |\Z)", body, re.DOTALL)
    if edges_match:
        for raw in _parse_edge_blocks(edges_match.group(1)):
            src = slug_to_id.get(raw.get("from", ""))
            tgt = slug_to_id.get(raw.get("to", ""))
            etype = raw.get("type", "")
            why = raw.get("why", "")
            _add_edge(src or raw.get("from", ""), tgt or raw.get("to", ""), etype, why)
            # `related` is symmetric — derive the reverse (author once).
            if etype == "related":
                _add_edge(tgt or raw.get("to", ""), src or raw.get("from", ""), etype, why)

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
        title=title,
        edges=edges,
    )


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def validate(domain_map: DomainMap) -> list[str]:
    """Validate a DomainMap. Returns list of error strings (empty = valid)."""
    errors = []
    slugs = {t.slug for t in domain_map.topics}
    ids = {t.id for t in domain_map.topics}

    # Check topic count
    if len(domain_map.topics) > 9:
        errors.append(f"Too many topics: {len(domain_map.topics)} (max 9)")

    # Node id integrity: valid ULID + unique
    seen_ids: set[str] = set()
    for t in domain_map.topics:
        if not ulid.is_valid(t.id):
            errors.append(f"Topic '{t.slug}' has invalid ULID id '{t.id}'")
        elif t.id in seen_ids:
            errors.append(f"Duplicate topic id '{t.id}' (slug '{t.slug}')")
        seen_ids.add(t.id)

    # Undefined prereqs — reported by the human-facing slug
    for t in domain_map.topics:
        for prereq in t.prereqs:
            if prereq not in slugs:
                errors.append(f"Topic '{t.slug}' has undefined prereq '{prereq}'")

    # Edge integrity: valid type + both endpoints resolve to a known topic id
    for e in domain_map.edges:
        if e.type not in EDGE_TYPES:
            errors.append(f"Edge {e.source_id}->{e.target_id} has invalid type '{e.type}'")
        if e.source_id not in ids:
            errors.append(f"Edge source '{e.source_id}' ({e.type}) resolves to no topic")
        if e.target_id not in ids:
            errors.append(f"Edge target '{e.target_id}' ({e.type}) resolves to no topic")

    # Cycle check — Kahn over PREREQ edges only (leads_to/related may legitimately cycle)
    prereq_edges = [e for e in domain_map.edges if e.type == "prereq"]
    in_degree = {t.id: 0 for t in domain_map.topics}
    adjacency: dict[str, list[str]] = {t.id: [] for t in domain_map.topics}
    for e in prereq_edges:
        if e.source_id in adjacency and e.target_id in in_degree:
            adjacency[e.source_id].append(e.target_id)
            in_degree[e.target_id] += 1

    queue = [tid for tid, d in in_degree.items() if d == 0]
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

def _prereq_sources(domain_map: DomainMap) -> dict[str, list[str]]:
    """target_id -> [source_id, ...] over prereq edges only."""
    m: dict[str, list[str]] = {t.id: [] for t in domain_map.topics}
    for e in domain_map.edges:
        if e.type == "prereq" and e.target_id in m:
            m[e.target_id].append(e.source_id)
    return m


def get_available_topics(domain_map: DomainMap) -> list[Topic]:
    """Return topics whose prereqs are all complete or in-progress."""
    satisfied = {t.id for t in domain_map.topics if t.status in ("complete", "in-progress")}
    prereq_sources = _prereq_sources(domain_map)
    available = []
    for t in domain_map.topics:
        if t.status != "not-started":
            continue
        if all(src in satisfied for src in prereq_sources.get(t.id, [])):
            available.append(t)
    return available


def get_next_suggestion(domain_map: DomainMap) -> Topic | None:
    """Suggest the best next topic: available + most downstream dependents."""
    available = get_available_topics(domain_map)
    if not available:
        return None

    # target_id -> [source_id] lets us walk downstream via reverse lookup.
    prereq_sources = _prereq_sources(domain_map)

    # Count how many topics depend (directly or transitively) on each
    def count_dependents(tid: str) -> int:
        """BFS count of topics downstream of tid (following prereq edges forward)."""
        dependents: set[str] = set()
        queue = [tid]
        while queue:
            current = queue.pop(0)
            for other_id, srcs in prereq_sources.items():
                if current in srcs and other_id not in dependents:
                    dependents.add(other_id)
                    queue.append(other_id)
        return len(dependents)

    return max(available, key=lambda t: count_dependents(t.id))


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
