"""Project path helpers."""

from __future__ import annotations

from pathlib import Path

GOVERNED_DIRNAME = ".governed"


def governed_root(project_root: Path) -> Path:
    """Return the governed root for a project root."""
    return project_root / GOVERNED_DIRNAME


def resolve_project_root(start: Path) -> Path:
    """Resolve the owning project root from a path within or next to `.governed`."""
    candidate = start.resolve()
    if candidate.name == GOVERNED_DIRNAME:
        return candidate.parent
    if governed_root(candidate).is_dir():
        return candidate
    for parent in candidate.parents:
        if governed_root(parent).is_dir():
            return parent
    return candidate
