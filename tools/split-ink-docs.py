"""
split-ink-docs.py — Split ink documentation into per-section files for portable search.

Follows the godot-knowledge pattern:
  .references/ink/Documentation/ → .memory/ink-reference/

Each section gets:
  - YAML frontmatter (type, part, section, tags)
  - Intent preamble (search hint for semantic retrieval)
  - Tab-indented code converted to fenced ```ink blocks
  - "produces:" output converted to fenced ```text blocks

Usage:
    python tools/split-ink-docs.py [--source DIR] [--output DIR]

Defaults:
    --source .references/ink/Documentation/
    --output .memory/ink-reference/

Stdlib only. No pip dependencies. Idempotent.
"""

import argparse
import re
import shutil
from pathlib import Path

# Intent preambles — map section slugs to search hints.
# These bridge author language ("Part 2 Section 1") to developer queries ("how do I bring branches back together").
INTENT_PREAMBLES = {
    "1-01-content": "Developers search for this when: writing basic ink text, comments, tags, marking up lines, hashtags, TODO markers",
    "1-02-choices": "Developers search for this when: adding player choices, suppressing choice text, square brackets in choices, mixing choice and output text, multiple options",
    "1-03-knots": "Developers search for this when: structuring ink stories, creating named sections, dividing content into pieces, === syntax",
    "1-04-diverts": "Developers search for this when: connecting knots, jumping between sections, -> arrow syntax, invisible flow, glue",
    "1-05-branching-the-flow": "Developers search for this when: branching story paths, joining branches back together, creating loops, story flow control",
    "1-06-includes-and-stitches": "Developers search for this when: sub-sections within knots, = stitch syntax, organizing large stories, splitting into files, INCLUDE",
    "1-07-varying-choices": "Developers search for this when: once-only choices, sticky choices +, fallback choices, conditional choices, choices that disappear",
    "1-08-variable-text": "Developers search for this when: sequences, cycles, shuffles, alternatives, text that changes each visit, conditional text, {|}",
    "1-09-game-queries-and-functions": "Developers search for this when: CHOICE_COUNT, TURNS, TURNS_SINCE, SEED_RANDOM, querying game state from ink",
    "2-01-gathers": "Developers search for this when: bringing branches together, - gather syntax, weave philosophy, avoiding spaghetti diverts",
    "2-02-nested-flow": "Developers search for this when: nested choices, sub-options, nested gathers, deep branching, ** *** nested levels",
    "2-03-tracking-a-weave": "Developers search for this when: labelling gathers, labelling options, scope rules, addressing weave points, loops in weave",
    "3-01-global-variables": "Developers search for this when: VAR keyword, defining variables, printing variables, storing diverts, externally visible state",
    "3-02-logic": "Developers search for this when: ink math, arithmetic, RANDOM, INT, FLOOR, FLOAT, string queries, numerical types",
    "3-03-conditional-blocks": "Developers search for this when: if/else in ink, switch blocks, conditional content, context-relevant text, multiline blocks",
    "3-04-temporary-variables": "Developers search for this when: temp keyword, scratch calculations, knot parameters, passing arguments, recursive knots",
    "3-05-functions": "Developers search for this when: defining functions, return values, calling inline, pass by reference, reusable logic",
    "3-06-constants": "Developers search for this when: CONST keyword, global constants, named values that don't change",
    "3-07-game-side-logic": "Developers search for this when: EXTERNAL functions, calling game code from ink, binding functions, game-side integration",
    "4-01-tunnels": "Developers search for this when: ->-> tunnel return, sub-stories, reusable passages, call stack, tunnel syntax",
    "4-02-threads": "Developers search for this when: <- thread syntax, joining sections, side content, parallel threads, when threads end, -> DONE",
    "5-01-basic-lists": "Developers search for this when: LIST keyword, defining lists, state machines in ink, enums, named states",
    "5-02-reusing-lists": "Developers search for this when: list states, reusing list values, shared names, LIST as variable",
    "5-03-list-values": "Developers search for this when: LIST_VALUE, list to number, number to list, custom numerical values",
    "5-04-multivalued-lists": "Developers search for this when: boolean sets, multiple list values, adding removing entries, containment, LIST_ALL",
    "5-05-advanced-list-operations": "Developers search for this when: comparing lists, inverting lists, intersecting lists, list math, set operations",
    "5-06-multi-list-lists": "Developers search for this when: tracking objects with lists, multiple state machines, cross-list queries",
    "5-07-long-example-crime-scene": "Developers search for this when: full ink example, crime scene investigation, complex list usage, complete working story",
    "5-08-summary": "Developers search for this when: list patterns overview, flags, state machines, properties, list best practices",
    "6-01-international-characters": "Developers search for this when: unicode identifiers, non-latin characters, international ink support",
}


def slugify(text: str) -> str:
    """Convert heading text to a filename-safe slug."""
    text = text.lower()
    # Remove numbering like "1) " or "7) "
    text = re.sub(r"^\d+\)\s*", "", text)
    # Remove "Advanced: " prefix
    text = re.sub(r"^advanced:\s*", "", text)
    # Replace non-alphanum with hyphens
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = text.strip("-")
    return text


def detect_part_number(line: str, current_part: int) -> int:
    """Extract part number from a Part heading line."""
    m = re.match(r"^#\s+Part\s+(\w+)", line, re.IGNORECASE)
    if m:
        word = m.group(1).lower()
        word_map = {"one": 1, "two": 2, "2": 2, "three": 3, "3": 3,
                    "four": 4, "4": 4, "five": 5, "5": 5, "six": 6, "6": 6}
        return word_map.get(word, current_part)
    return current_part


def convert_tab_indented_code(lines: list[str]) -> list[str]:
    """Convert tab-indented code blocks to fenced blocks.

    Detects contiguous runs of tab-indented lines and wraps them in fences.
    Uses ```ink for ink code and ```text for output (after "produces:" lines).
    """
    result = []
    i = 0
    in_output_context = False

    while i < len(lines):
        line = lines[i]

        # Detect "produces:" or "produces output:" context markers
        stripped = line.strip().lower()
        if stripped.startswith("produces") or stripped.startswith("this produces"):
            in_output_context = True
            result.append(line)
            i += 1
            continue

        # Check if this line starts a tab-indented block
        if line.startswith("\t"):
            # Collect the entire indented block
            block_lines = []
            while i < len(lines):
                if lines[i].startswith("\t"):
                    block_lines.append(lines[i][1:])  # Remove leading tab
                    i += 1
                elif lines[i].strip() == "":
                    # Blank line — look ahead to see if block continues
                    j = i + 1
                    while j < len(lines) and lines[j].strip() == "":
                        j += 1
                    if j < len(lines) and lines[j].startswith("\t"):
                        # Block continues after blank line(s)
                        block_lines.append("")
                        i += 1
                    else:
                        # Block ends here
                        break
                else:
                    break

            # Determine fence language
            lang = "text" if in_output_context else "ink"
            result.append(f"```{lang}")
            result.extend(block_lines)
            result.append("```")
            in_output_context = False
            continue

        # Reset output context on non-empty, non-indented lines (unless it's blank)
        if line.strip():
            in_output_context = False

        result.append(line)
        i += 1

    return result


def extract_tags(content: str, section_title: str) -> list[str]:
    """Extract relevant tags from section content and title."""
    tags = []

    # Tags from title keywords
    title_lower = section_title.lower()
    tag_keywords = {
        "choice": "choices", "knot": "knots", "divert": "diverts",
        "stitch": "stitches", "gather": "gathers", "weave": "weave",
        "variable": "variables", "function": "functions", "tunnel": "tunnels",
        "thread": "threads", "list": "lists", "conditional": "conditionals",
        "include": "includes", "loop": "loops", "branch": "branching",
        "constant": "constants", "nested": "nesting", "parameter": "parameters",
    }
    for keyword, tag in tag_keywords.items():
        if keyword in title_lower:
            tags.append(tag)

    # Tags from content patterns
    if "EXTERNAL" in content:
        tags.append("external-functions")
    if "LIST " in content or "LIST_" in content:
        tags.append("lists")
    if "->->" in content:
        tags.append("tunnels")
    if "<-" in content and "thread" in content.lower():
        tags.append("threads")
    if "TURNS_SINCE" in content or "CHOICE_COUNT" in content:
        tags.append("game-queries")

    return sorted(set(tags)) if tags else ["ink-language"]


def split_writing_with_ink(source_path: Path) -> list[dict]:
    """Split WritingWithInk.md into sections at ## boundaries."""
    text = source_path.read_text(encoding="utf-8")
    lines = text.split("\n")

    sections = []
    current_part = 0
    current_section_num = 0
    current_title = ""
    current_lines = []
    section_part = 0  # Part number captured when section starts
    in_toc = False

    for i, line in enumerate(lines):
        # Skip the HTML table of contents
        if "<details>" in line:
            in_toc = True
            continue
        if "</details>" in line:
            in_toc = False
            continue
        if in_toc:
            continue

        # Detect Part headings (H1 level: "# Part One: ...")
        if line.startswith("# ") and not line.startswith("## ") and "Part" in line:
            current_part = detect_part_number(line, current_part)
            # Part headings don't create their own section — content goes to next ##
            continue

        # Skip the title line
        if line == "# Writing with ink":
            continue

        # Detect section boundaries (## level)
        if line.startswith("## "):
            # Save previous section if it has content
            if current_title and current_lines:
                sections.append({
                    "part": section_part if section_part > 0 else 1,
                    "section_num": current_section_num,
                    "title": current_title,
                    "lines": current_lines,
                })

            # Parse new section — capture current_part NOW
            section_part = current_part
            current_title = line[3:].strip()
            current_section_num += 1
            # Use explicit numbering if present
            m = re.match(r"(\d+)\)", current_title)
            if m:
                current_section_num = int(m.group(1))
            current_lines = []
            continue

        current_lines.append(line)

    # Don't forget the last section
    if current_title and current_lines:
        sections.append({
            "part": section_part if section_part > 0 else 1,
            "section_num": current_section_num,
            "title": current_title,
            "lines": current_lines,
        })

    return sections


def build_section_file(section: dict) -> str:
    """Build a complete markdown file for one section."""
    part = section["part"]
    num = section["section_num"]
    title = section["title"]
    lines = section["lines"]

    # Clean title for display (remove "N) " prefix)
    display_title = re.sub(r"^\d+\)\s*", "", title)

    # Build slug
    slug = f"{part}-{num:02d}-{slugify(title)}"

    # Extract tags from content
    content_text = "\n".join(lines)
    tags = extract_tags(content_text, title)

    # Convert tab-indented code to fenced blocks
    converted_lines = convert_tab_indented_code(lines)

    # Get intent preamble
    preamble = INTENT_PREAMBLES.get(slug, "")

    # Build frontmatter
    tags_str = ", ".join(f'"{t}"' for t in tags)
    frontmatter = f"""---
type: ink-reference
source: WritingWithInk.md
part: {part}
section: "{display_title}"
tags: [{tags_str}]
---"""

    # Build content
    parts = [frontmatter, ""]

    if preamble:
        parts.append(f"<!-- search: {preamble} -->")
        parts.append("")

    parts.append(f"# {display_title}")
    parts.append(f"*Part {part} of Writing with ink*")
    parts.append("")
    parts.extend(converted_lines)

    return "\n".join(parts)


def process_small_doc(source_path: Path, doc_type: str) -> str:
    """Process a smaller doc — add frontmatter, leave content mostly intact."""
    text = source_path.read_text(encoding="utf-8")
    lines = text.split("\n")

    # Extract title from first H1
    title = source_path.stem
    for line in lines:
        if line.startswith("# "):
            title = line[2:].strip()
            break

    slug = slugify(title)
    tags_map = {
        "RunningYourInk": ["runtime", "api", "csharp", "integration", "external-functions"],
        "ink_JSON_runtime_format": ["json", "runtime", "format", "serialization"],
        "ArchitectureAndDevOverview": ["architecture", "compiler", "internals"],
    }
    tags = tags_map.get(source_path.stem, ["ink-language"])
    tags_str = ", ".join(f'"{t}"' for t in tags)

    intent_map = {
        "RunningYourInk": "Developers search for this when: runtime API, loading ink stories, saving state, variable observers, external functions, error handling, tags, C# integration, BindExternalFunction",
        "ink_JSON_runtime_format": "Developers search for this when: ink JSON format, compiled ink structure, runtime data format, story.json internals",
        "ArchitectureAndDevOverview": "Developers search for this when: ink compiler architecture, how ink works internally, compilation pipeline, development overview",
    }
    preamble = intent_map.get(source_path.stem, "")

    frontmatter = f"""---
type: ink-reference
source: "{source_path.name}"
section: "{title}"
tags: [{tags_str}]
---"""

    parts = [frontmatter, ""]
    if preamble:
        parts.append(f"<!-- search: {preamble} -->")
        parts.append("")
    parts.extend(lines)

    return "\n".join(parts)


def main():
    parser = argparse.ArgumentParser(description="Split ink docs into per-section reference files")
    parser.add_argument("--source", default=".references/ink/Documentation/",
                        help="Source documentation directory")
    parser.add_argument("--output", default=".memory/ink-reference/",
                        help="Output directory for split files")
    args = parser.parse_args()

    source_dir = Path(args.source)
    output_dir = Path(args.output)

    if not source_dir.exists():
        print(f"ERROR: Source directory not found: {source_dir}")
        return 1

    # Clean output directory for idempotent runs
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True)

    # Process WritingWithInk.md
    writing_path = source_dir / "WritingWithInk.md"
    if not writing_path.exists():
        print(f"ERROR: {writing_path} not found")
        return 1

    print(f"Splitting {writing_path.name}...")
    sections = split_writing_with_ink(writing_path)
    print(f"  Found {len(sections)} sections")

    for section in sections:
        slug = f"{section['part']}-{section['section_num']:02d}-{slugify(section['title'])}"
        filename = f"{slug}.md"
        content = build_section_file(section)
        (output_dir / filename).write_text(content, encoding="utf-8")

    # Process smaller docs
    small_docs = ["RunningYourInk.md", "ink_JSON_runtime_format.md", "ArchitectureAndDevOverview.md"]
    for doc_name in small_docs:
        doc_path = source_dir / doc_name
        if doc_path.exists():
            print(f"Processing {doc_name}...")
            content = process_small_doc(doc_path, "reference")
            out_name = slugify(doc_path.stem) + ".md"
            (output_dir / out_name).write_text(content, encoding="utf-8")
        else:
            print(f"  SKIP: {doc_name} not found")

    # Summary
    output_files = list(output_dir.glob("*.md"))
    print(f"\nDone: {len(output_files)} files written to {output_dir}/")
    for f in sorted(output_files):
        size = f.stat().st_size
        print(f"  {f.name} ({size:,} bytes)")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
