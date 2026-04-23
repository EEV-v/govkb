"""Project scaffold command."""

from __future__ import annotations

import sys
from pathlib import Path

from govkb.core.ids import normalize_identifier
from govkb.core.templates import copy_project_template


def run_init(args) -> int:
    """Scaffold a valid `.governed` package into the target project root."""
    project_root = Path(args.dest).resolve()
    project_name = args.project_name or project_root.name
    project_id = args.project_id or normalize_identifier(project_name)
    governed_root = project_root / ".governed"

    if governed_root.exists():
        print(f"error: {governed_root} already exists", file=sys.stderr)
        return 1

    replacements = {
        "__PROJECT_ID__": project_id,
        "__PROJECT_NAME__": project_name,
    }
    copy_project_template(project_root, replacements)

    print(f"Scaffolded {governed_root}")
    print(f"Project id: {project_id}")
    print("Next step: govkb validate")
    return 0
