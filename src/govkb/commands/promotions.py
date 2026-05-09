"""Promotion review commands."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
from typing import Any

from govkb.core.contracts import load_project_bundle
from govkb.core.ids import normalize_identifier
from govkb.core.install_state import default_codex_home
from govkb.core.promotion_lifecycle import archived_promotion_metadata
from govkb.core.promotion_lifecycle import initial_promotion_metadata
from govkb.core.promotion_lifecycle import promotion_metadata_path
from govkb.core.promotion_lifecycle import promotion_project_key
from govkb.core.promotion_lifecycle import read_promotion_metadata
from govkb.core.promotion_lifecycle import reviewed_promotion_metadata
from govkb.core.promotion_lifecycle import write_promotion_metadata


def _worktree_project_key(project_id: str) -> str:
    return promotion_project_key(project_id)


def _project_id(project_root: Path) -> str:
    bundle, _ = load_project_bundle(project_root)
    return bundle.project_id or normalize_identifier(project_root.name)


def _promotions_root(project_root: Path, codex_home: Path) -> Path:
    return codex_home / "memories" / "govkb" / "worktrees" / _worktree_project_key(_project_id(project_root))


def _git_output(cwd: Path, args: list[str]) -> str | None:
    proc = subprocess.run(
        ["git", *args],
        cwd=cwd,
        text=True,
        capture_output=True,
        check=False,
    )
    if proc.returncode != 0:
        return None
    return proc.stdout.strip()


def _git_status(worktree_root: Path) -> list[str]:
    output = _git_output(worktree_root, ["status", "--short", "--", ".governed"])
    if output is None:
        return ["git status unavailable"]
    return [line for line in output.splitlines() if line.strip()]


def _promotion_summary(worktree_root: Path, *, project_id: str, project_root: Path, codex_home: Path) -> dict[str, Any]:
    digest_path = worktree_root / ".governed" / "reports" / "promotions" / "latest-promotion-digest.md"
    report_paths = sorted((worktree_root / ".governed" / "reports" / "promotions").glob("*-promote-report.md"))
    status = _git_status(worktree_root)
    branch = _git_output(worktree_root, ["branch", "--show-current"])
    head = _git_output(worktree_root, ["rev-parse", "--short", "HEAD"])
    metadata_path = promotion_metadata_path(codex_home, project_id, worktree_root.name)
    metadata = read_promotion_metadata(metadata_path)
    default_state = "ready-for-review" if status else "clean"
    return {
        "runId": worktree_root.name,
        "branch": branch,
        "head": head,
        "worktreeRoot": str(worktree_root),
        "digestPath": str(digest_path) if digest_path.is_file() else None,
        "reportPaths": [str(path) for path in report_paths],
        "status": status,
        "state": metadata.get("state", default_state) if metadata else default_state,
        "metadataPath": str(metadata_path),
        "review": metadata.get("review") if metadata else None,
        "archive": metadata.get("archive") if metadata else None,
    }


def build_promotions_payload(project_root: Path, codex_home: Path | None = None) -> dict[str, Any]:
    """Build the machine-readable isolated promotion list payload."""
    resolved_project_root = Path(project_root).resolve()
    resolved_codex_home = (codex_home or default_codex_home()).resolve()
    project_id = _project_id(resolved_project_root)
    root = _promotions_root(resolved_project_root, resolved_codex_home)
    promotions = [
        _promotion_summary(
            path,
            project_id=project_id,
            project_root=resolved_project_root,
            codex_home=resolved_codex_home,
        )
        for path in sorted(root.iterdir(), reverse=True)
        if path.is_dir()
    ] if root.is_dir() else []
    return {
        "schemaVersion": 1,
        "projectRoot": str(resolved_project_root),
        "codexHome": str(resolved_codex_home),
        "projectId": project_id,
        "promotionsRoot": str(root),
        "promotions": promotions,
    }


def _resolve_promotion(payload: dict[str, Any], target: str) -> dict[str, Any] | None:
    target_path = Path(target).expanduser()
    if target_path.exists():
        resolved = str(target_path.resolve())
        for promotion in payload["promotions"]:
            if promotion["worktreeRoot"] == resolved:
                return promotion
        return _promotion_summary(
            target_path.resolve(),
            project_id=str(payload["projectId"]),
            project_root=Path(str(payload["projectRoot"])),
            codex_home=Path(str(payload["codexHome"])),
        )

    for promotion in payload["promotions"]:
        if target in {
            promotion.get("runId"),
            promotion.get("branch"),
            promotion.get("worktreeRoot"),
        }:
            return promotion
    for promotion in payload["promotions"]:
        branch = promotion.get("branch")
        if isinstance(branch, str) and branch.endswith(f"/{target}"):
            return promotion
    return None


def build_promotion_detail_payload(project_root: Path, target: str, codex_home: Path | None = None) -> dict[str, Any]:
    """Build a machine-readable payload for one isolated promotion."""
    payload = build_promotions_payload(project_root, codex_home)
    promotion = _resolve_promotion(payload, target)
    if promotion is None:
        return {
            "schemaVersion": 1,
            "projectRoot": payload["projectRoot"],
            "codexHome": payload["codexHome"],
            "projectId": payload["projectId"],
            "promotion": None,
            "error": f"promotion not found: {target}",
        }

    digest_text = None
    digest_path = promotion.get("digestPath")
    if isinstance(digest_path, str) and digest_path:
        path = Path(digest_path)
        if path.is_file():
            digest_text = path.read_text(encoding="utf-8")
    return {
        "schemaVersion": 1,
        "projectRoot": payload["projectRoot"],
        "codexHome": payload["codexHome"],
        "projectId": payload["projectId"],
        "promotion": promotion,
        "digestText": digest_text,
        "error": None,
    }


def run_promotions(args) -> int:
    """Run promotion review subcommands."""
    action = getattr(args, "promotion_action", "")
    if action == "list":
        return _run_list(args)
    if action == "show":
        return _run_show(args)
    if action == "mark-reviewed":
        return _run_mark_reviewed(args)
    if action == "archive":
        return _run_archive(args)
    print(f"error: unsupported promotions action: {action}", file=sys.stderr)
    return 1


def _run_list(args) -> int:
    payload = build_promotions_payload(Path(args.project_root), getattr(args, "codex_home", None))
    if getattr(args, "json", False):
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 0

    promotions = payload["promotions"]
    if not promotions:
        print(f"No isolated promotions found under {payload['promotionsRoot']}")
        return 0
    for promotion in promotions:
        changed = len(promotion["status"])
        print(
            f"{promotion['runId']} state={promotion['state']} changed={changed} "
            f"branch={promotion.get('branch') or '<unknown>'} worktree={promotion['worktreeRoot']}"
        )
    return 0


def _run_show(args) -> int:
    payload = build_promotion_detail_payload(Path(args.project_root), args.promotion, getattr(args, "codex_home", None))
    if getattr(args, "json", False):
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 1 if payload["promotion"] is None else 0

    promotion = payload["promotion"]
    if promotion is None:
        print(f"error: {payload['error']}", file=sys.stderr)
        return 1

    print(f"Run: {promotion['runId']}")
    print(f"State: {promotion['state']}")
    print(f"Branch: {promotion.get('branch') or '<unknown>'}")
    print(f"Worktree: {promotion['worktreeRoot']}")
    if promotion.get("metadataPath"):
        print(f"Lifecycle metadata: {promotion['metadataPath']}")
    review = promotion.get("review")
    if isinstance(review, dict):
        print(f"Review: {review.get('decision', '<unknown>')}")
        if review.get("reviewer"):
            print(f"Reviewer: {review['reviewer']}")
        if review.get("reason"):
            print(f"Review reason: {review['reason']}")
    archive = promotion.get("archive")
    if isinstance(archive, dict):
        print(f"Archived at: {archive.get('archivedAt', '<unknown>')}")
        if archive.get("reason"):
            print(f"Archive reason: {archive['reason']}")
    if promotion.get("digestPath"):
        print(f"Digest: {promotion['digestPath']}")
    if promotion["status"]:
        print("Git status:")
        for line in promotion["status"]:
            print(f"  {line}")
    else:
        print("Git status: clean")
    digest_text = payload.get("digestText")
    if isinstance(digest_text, str) and digest_text.strip():
        print("")
        print(digest_text.rstrip())
    return 0


def _metadata_from_promotion(payload: dict[str, Any], promotion: dict[str, Any]) -> dict[str, Any]:
    report_paths = promotion.get("reportPaths") if isinstance(promotion.get("reportPaths"), list) else []
    report_path = Path(str(report_paths[0])) if report_paths else None
    digest_value = promotion.get("digestPath")
    digest_path = Path(str(digest_value)) if isinstance(digest_value, str) and digest_value else None
    return initial_promotion_metadata(
        project_id=str(payload["projectId"]),
        project_root=Path(str(payload["projectRoot"])),
        codex_home=Path(str(payload["codexHome"])),
        run_id=str(promotion["runId"]),
        branch=str(promotion.get("branch") or ""),
        worktree_root=Path(str(promotion["worktreeRoot"])),
        digest_path=digest_path,
        report_path=report_path,
    )


def _write_review_state(args, *, state: str) -> int:
    detail = build_promotion_detail_payload(Path(args.project_root), args.promotion, getattr(args, "codex_home", None))
    promotion = detail["promotion"]
    if promotion is None:
        if getattr(args, "json", False):
            print(json.dumps(detail, indent=2, sort_keys=True))
        else:
            print(f"error: {detail['error']}", file=sys.stderr)
        return 1

    metadata_path = Path(str(promotion["metadataPath"]))
    existing = read_promotion_metadata(metadata_path) or _metadata_from_promotion(detail, promotion)
    updated = reviewed_promotion_metadata(
        existing,
        state=state,
        reviewer=getattr(args, "reviewer", None),
        reason=args.reason,
    )
    write_promotion_metadata(metadata_path, updated)
    result = build_promotion_detail_payload(Path(args.project_root), str(promotion["runId"]), getattr(args, "codex_home", None))
    if getattr(args, "json", False):
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"Marked promotion {promotion['runId']} as {state}.")
        print(f"Lifecycle metadata: {metadata_path}")
        print("Git history unchanged; apply repository changes through the normal project Git flow.")
    return 0


def _run_mark_reviewed(args) -> int:
    decision = str(args.decision)
    if decision not in {"accepted", "rejected"}:
        print(f"error: unsupported decision: {decision}", file=sys.stderr)
        return 1
    return _write_review_state(args, state=decision)


def _run_archive(args) -> int:
    detail = build_promotion_detail_payload(Path(args.project_root), args.promotion, getattr(args, "codex_home", None))
    promotion = detail["promotion"]
    if promotion is None:
        if getattr(args, "json", False):
            print(json.dumps(detail, indent=2, sort_keys=True))
        else:
            print(f"error: {detail['error']}", file=sys.stderr)
        return 1

    metadata_path = Path(str(promotion["metadataPath"]))
    existing = read_promotion_metadata(metadata_path) or _metadata_from_promotion(detail, promotion)
    updated = archived_promotion_metadata(existing, reason=getattr(args, "reason", None))
    write_promotion_metadata(metadata_path, updated)
    result = build_promotion_detail_payload(Path(args.project_root), str(promotion["runId"]), getattr(args, "codex_home", None))
    if getattr(args, "json", False):
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"Archived promotion {promotion['runId']} in GovKB lifecycle metadata.")
        print(f"Lifecycle metadata: {metadata_path}")
        print("Git worktree and history unchanged.")
    return 0
