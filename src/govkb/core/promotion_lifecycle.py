"""Sidecar lifecycle state for isolated promotion reviews."""

from __future__ import annotations

import json
from pathlib import Path
import re
from typing import Any

from govkb.core.install_state import iso_utc_now


PROMOTION_STATES = {"ready-for-review", "accepted", "rejected", "archived"}


def promotion_project_key(project_id: str) -> str:
    """Return the sidecar storage key for one governed project."""
    normalized = re.sub(r"[^a-zA-Z0-9._-]+", "-", project_id).strip("-._")
    return normalized or "project"


def promotion_metadata_path(codex_home: Path, project_id: str, run_id: str) -> Path:
    """Return the sidecar lifecycle metadata path for one promotion run."""
    return (
        codex_home
        / "memories"
        / "govkb"
        / "promotions"
        / promotion_project_key(project_id)
        / f"{run_id}.json"
    )


def read_promotion_metadata(path: Path) -> dict[str, Any] | None:
    """Read sidecar lifecycle metadata if it exists and is valid."""
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    return data if isinstance(data, dict) else None


def write_promotion_metadata(path: Path, payload: dict[str, Any]) -> None:
    """Write sidecar lifecycle metadata atomically."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(".tmp")
    tmp_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    tmp_path.replace(path)


def initial_promotion_metadata(
    *,
    project_id: str,
    project_root: Path,
    codex_home: Path,
    run_id: str,
    branch: str,
    worktree_root: Path,
    digest_path: Path | None,
    report_path: Path | None,
) -> dict[str, Any]:
    """Build initial lifecycle metadata for one isolated promotion."""
    return {
        "schemaVersion": 1,
        "runId": run_id,
        "projectId": project_id,
        "projectRoot": str(project_root),
        "codexHome": str(codex_home),
        "state": "ready-for-review",
        "branch": branch,
        "worktreeRoot": str(worktree_root),
        "digestPath": str(digest_path) if digest_path else None,
        "reportPath": str(report_path) if report_path else None,
        "createdAt": iso_utc_now(),
        "review": None,
        "archive": None,
    }


def reviewed_promotion_metadata(
    existing: dict[str, Any],
    *,
    state: str,
    reviewer: str | None,
    reason: str,
) -> dict[str, Any]:
    """Return lifecycle metadata updated with an accepted or rejected review."""
    if state not in {"accepted", "rejected"}:
        raise ValueError(f"unsupported review state: {state}")
    updated = dict(existing)
    updated["state"] = state
    updated["review"] = {
        "decision": state,
        "reviewer": reviewer,
        "reason": reason,
        "reviewedAt": iso_utc_now(),
    }
    return updated


def archived_promotion_metadata(existing: dict[str, Any], *, reason: str | None) -> dict[str, Any]:
    """Return lifecycle metadata updated with archive state."""
    updated = dict(existing)
    updated["state"] = "archived"
    updated["archive"] = {
        "reason": reason,
        "archivedAt": iso_utc_now(),
    }
    return updated
