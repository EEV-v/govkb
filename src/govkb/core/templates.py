"""Template copy helpers."""

from __future__ import annotations

from pathlib import Path


def _copy_tree(source, destination: Path, replacements: dict[str, str]) -> None:
    destination.mkdir(parents=True, exist_ok=True)
    for child in source.iterdir():
        target = destination / child.name
        if child.is_dir():
            _copy_tree(child, target, replacements)
            continue
        text = child.read_text(encoding="utf-8")
        for token, value in replacements.items():
            text = text.replace(token, value)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")


def copy_project_template(project_root: Path, replacements: dict[str, str]) -> None:
    """Copy the packaged project template into a project root."""
    source_root = Path(__file__).resolve().parent.parent / "templates" / "project" / ".governed"
    _copy_tree(source_root, project_root / ".governed", replacements)
