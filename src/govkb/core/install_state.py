"""Local install-state helpers."""

from __future__ import annotations

import datetime as dt
import json
import os
from pathlib import Path
from typing import Any


def default_codex_home() -> Path:
    """Resolve the local Codex home."""
    configured = os.environ.get("CODEX_HOME")
    if configured:
        return Path(configured).expanduser().resolve()
    return (Path.home() / ".codex").resolve()


def install_state_path(codex_home: Path, project_id: str, assistant: str = "codex") -> Path:
    """Return the local install-state path for one project/assistant pair."""
    safe_project_id = project_id.replace("/", "-")
    return codex_home / "memories" / "govkb" / "install-state" / f"{safe_project_id}--{assistant}.json"


def backups_root(codex_home: Path, project_id: str, assistant: str, run_id: str) -> Path:
    """Return the backup root for one materialization run."""
    safe_project_id = project_id.replace("/", "-")
    return codex_home / "memories" / "govkb" / "backups" / safe_project_id / assistant / run_id


def iso_utc_now() -> str:
    """Return the current UTC timestamp in ISO Z form."""
    return dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z")


def load_install_state(path: Path) -> dict[str, Any] | None:
    """Load an install-state file if it exists and is valid."""
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None


def write_install_state(path: Path, payload: dict[str, Any]) -> None:
    """Write install state atomically."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(".tmp")
    tmp_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    tmp_path.replace(path)
