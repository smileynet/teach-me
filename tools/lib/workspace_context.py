"""One explicit content and local-state root for generators and the server."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class WorkspaceContext:
    """Paths that must stay together for one served or generated workspace."""

    root: Path
    maps: tuple[Path, ...]
    lessons_dir: Path
    questions_dir: Path
    overlay_root: Path
    multi_domain: bool

    @classmethod
    def from_root(cls, root: Path) -> "WorkspaceContext":
        """Validate and describe one single-domain or library-root workspace."""
        root = root.resolve()
        single_maps = tuple(sorted((root / "maps").glob("*.MAP.md")))
        multi_maps = tuple(sorted(root.glob("*/maps/*.MAP.md")))
        if single_maps:
            maps, multi_domain = single_maps, False
        elif multi_maps:
            maps, multi_domain = multi_maps, True
        else:
            raise ValueError(f"Workspace has no MAP.md files: {root}")

        user_records = root / ".user" / "learning-records"
        committed_records = root / "learning-records"
        records_root = user_records if user_records.exists() else committed_records
        if not records_root.exists():
            records_root = user_records
        return cls(
            root=root,
            maps=maps,
            lessons_dir=root / "lessons",
            questions_dir=records_root / "questions",
            overlay_root=root,
            multi_domain=multi_domain,
        )

    @classmethod
    def for_map(cls, map_path: Path) -> "WorkspaceContext":
        """Describe a map's owning workspace, including ad-hoc fixture maps."""
        map_path = map_path.resolve()
        if map_path.parent.name == "maps":
            return cls.from_root(map_path.parent.parent)
        root = map_path.parent
        user_records = root / ".user" / "learning-records"
        committed_records = root / "learning-records"
        records_root = user_records if user_records.exists() else committed_records
        if not records_root.exists():
            records_root = user_records
        return cls(root, (map_path,), root / "lessons", records_root / "questions", root, False)
