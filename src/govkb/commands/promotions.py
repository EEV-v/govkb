"""Promotion review commands."""

from __future__ import annotations

import json
from pathlib import Path
import shutil
import subprocess
import sys
from typing import Any

from govkb.core.contracts import load_project_bundle
from govkb.core.ids import normalize_identifier
from govkb.core.install_state import default_codex_home
from govkb.core.promotion_lifecycle import applied_promotion_metadata
from govkb.core.promotion_lifecycle import archived_promotion_metadata
from govkb.core.promotion_lifecycle import cleaned_promotion_metadata
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


def _git_status_output(cwd: Path, args: list[str]) -> str | None:
    proc = subprocess.run(
        ["git", *args],
        cwd=cwd,
        text=True,
        capture_output=True,
        check=False,
    )
    if proc.returncode != 0:
        return None
    return proc.stdout.rstrip("\n")


def _git_status(worktree_root: Path) -> list[str]:
    output = _git_status_output(worktree_root, ["status", "--short", "--", ".governed"])
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
        "apply": metadata.get("apply") if metadata else None,
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
    if action == "apply":
        return _run_apply(args)
    if action == "archive":
        return _run_archive(args)
    if action == "cleanup":
        return _run_cleanup(args)
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


def _is_under_root(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
    except ValueError:
        return False
    return True


def _cleanup_reason(promotion: dict[str, Any]) -> str | None:
    state = str(promotion.get("state") or "")
    if state in {"applied", "archived", "rejected", "clean"}:
        return f"state is {state}"
    if state == "cleaned":
        return "already cleaned"
    return None


def _cleanup_item(
    promotion: dict[str, Any],
    *,
    eligible: bool,
    reason: str,
) -> dict[str, Any]:
    return {
        "runId": promotion.get("runId"),
        "state": promotion.get("state"),
        "worktreeRoot": promotion.get("worktreeRoot"),
        "metadataPath": promotion.get("metadataPath"),
        "eligible": eligible,
        "reason": reason,
    }


def _remove_promotion_worktree(worktree_root: Path, active_project_root: Path) -> tuple[bool, str | None]:
    git_root = _git_root(active_project_root)
    if git_root is not None:
        proc = subprocess.run(
            ["git", "-C", str(git_root), "worktree", "remove", "--force", str(worktree_root)],
            text=True,
            capture_output=True,
            check=False,
        )
        if proc.returncode == 0:
            return True, None
        detail = (proc.stderr or proc.stdout).strip()
        if worktree_root.exists():
            try:
                shutil.rmtree(worktree_root)
                return True, None
            except OSError as error:
                return False, f"git worktree remove failed: {detail}; fallback removal failed: {error}"
        return True, None
    try:
        shutil.rmtree(worktree_root)
    except OSError as error:
        return False, str(error)
    return True, None


def build_promotion_cleanup_payload(
    project_root: Path,
    codex_home: Path | None = None,
    *,
    apply: bool = False,
    reason: str | None = None,
) -> dict[str, Any]:
    """Preview or apply cleanup for non-actionable isolated promotion worktrees."""
    payload = build_promotions_payload(project_root, codex_home)
    promotions_root = Path(str(payload["promotionsRoot"])).resolve()
    cleanup_reason_text = reason or "promotion cleanup"
    result: dict[str, Any] = {
        "schemaVersion": 1,
        "projectRoot": payload["projectRoot"],
        "codexHome": payload["codexHome"],
        "projectId": payload["projectId"],
        "promotionsRoot": str(promotions_root),
        "mode": "apply" if apply else "preview",
        "eligible": [],
        "skipped": [],
        "removed": [],
        "metadataUpdated": [],
        "error": None,
    }

    for promotion in payload["promotions"]:
        cleanup_reason_value = _cleanup_reason(promotion)
        if cleanup_reason_value is None:
            result["skipped"].append(
                _cleanup_item(
                    promotion,
                    eligible=False,
                    reason="state is actionable; use review, reject, finalize, or archive first",
                )
            )
            continue
        worktree_root = Path(str(promotion["worktreeRoot"])).resolve()
        if not _is_under_root(worktree_root, promotions_root):
            result["skipped"].append(
                _cleanup_item(
                    promotion,
                    eligible=False,
                    reason="worktree path is outside the computed promotions root",
                )
            )
            continue
        if not worktree_root.is_dir():
            result["skipped"].append(
                _cleanup_item(
                    promotion,
                    eligible=False,
                    reason="worktree path is already missing",
                )
            )
            continue
        result["eligible"].append(_cleanup_item(promotion, eligible=True, reason=cleanup_reason_value))

    if not apply:
        return result

    for item in list(result["eligible"]):
        worktree_root = Path(str(item["worktreeRoot"])).resolve()
        ok, error = _remove_promotion_worktree(worktree_root, Path(str(payload["projectRoot"])).resolve())
        if not ok:
            item["eligible"] = False
            item["reason"] = f"cleanup failed: {error}"
            result["skipped"].append(item)
            result["error"] = error or "cleanup failed"
            continue
        result["removed"].append(str(worktree_root))
        metadata_path = Path(str(item["metadataPath"]))
        existing = read_promotion_metadata(metadata_path)
        if existing is None:
            matching = next(
                promotion for promotion in payload["promotions"] if str(promotion["runId"]) == str(item["runId"])
            )
            existing = _metadata_from_promotion(payload, matching)
        write_promotion_metadata(
            metadata_path,
            cleaned_promotion_metadata(existing, removed_paths=[worktree_root], reason=cleanup_reason_text),
        )
        result["metadataUpdated"].append(str(metadata_path))
    return result


def _run_cleanup(args) -> int:
    result = build_promotion_cleanup_payload(
        Path(args.project_root),
        getattr(args, "codex_home", None),
        apply=getattr(args, "apply", False),
        reason=getattr(args, "reason", None),
    )
    if getattr(args, "json", False):
        print(json.dumps(result, indent=2, sort_keys=True))
        return 1 if result["error"] else 0
    action = "Removed" if result["mode"] == "apply" else "Would remove"
    if not result["eligible"]:
        print(f"No cleanup-eligible promotion worktrees found under {result['promotionsRoot']}")
    else:
        for item in result["eligible"]:
            print(f"{action} {item['runId']}: {item['reason']} ({item['worktreeRoot']})")
    if result["skipped"]:
        print("Skipped:")
        for item in result["skipped"]:
            print(f"  {item['runId']}: {item['reason']}")
    return 1 if result["error"] else 0


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
    apply = promotion.get("apply")
    if isinstance(apply, dict):
        print(f"Applied at: {apply.get('appliedAt', '<unknown>')}")
        if apply.get("projectRoot"):
            print(f"Applied project: {apply['projectRoot']}")
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


def _git_root(cwd: Path) -> Path | None:
    output = _git_output(cwd, ["rev-parse", "--show-toplevel"])
    return Path(output).resolve() if output else None


def _git_head(cwd: Path) -> str | None:
    return _git_output(cwd, ["rev-parse", "--verify", "HEAD"])


def _governed_status(project_root: Path) -> list[str] | None:
    output = _git_status_output(project_root, ["status", "--porcelain", "--", ".governed"])
    if output is None:
        return None
    return [line for line in output.splitlines() if line.strip()]


def _status_paths(status: list[str]) -> set[str]:
    paths: set[str] = set()
    for line in status:
        raw_path = line[3:].strip()
        if " -> " in raw_path:
            raw_path = raw_path.rsplit(" -> ", 1)[1]
        paths.add(raw_path.rstrip("/"))
    return paths


def _paths_overlap(left: str, right: str) -> bool:
    left = left.rstrip("/")
    right = right.rstrip("/")
    return left == right or left.startswith(f"{right}/") or right.startswith(f"{left}/")


def _promotion_project_root(active_project_root: Path, promotion: dict[str, Any]) -> Path:
    worktree_root = Path(str(promotion["worktreeRoot"])).resolve()
    active_git_root = _git_root(active_project_root)
    if active_git_root is not None:
        try:
            relative_project_root = active_project_root.resolve().relative_to(active_git_root)
        except ValueError:
            relative_project_root = Path()
        candidate = worktree_root / relative_project_root
        if (candidate / ".governed").exists():
            return candidate
    if (worktree_root / ".governed").exists():
        return worktree_root
    return worktree_root


def _changed_governed_files(project_root: Path) -> tuple[list[Path], list[str]]:
    status = _governed_status(project_root)
    if status is None:
        return [], ["git status unavailable for promotion worktree"]
    files: list[Path] = []
    errors: list[str] = []
    seen: set[str] = set()
    for line in status:
        code = line[:2]
        raw_path = line[3:].strip()
        if " -> " in raw_path:
            raw_path = raw_path.rsplit(" -> ", 1)[1]
        if not raw_path.startswith(".governed/") and raw_path != ".governed":
            errors.append(f"unsupported non-governed promotion path: {raw_path}")
            continue
        if "D" in code:
            errors.append(f"delete changes are not supported by apply: {raw_path}")
            continue

        source = project_root / raw_path
        candidates: list[Path]
        if source.is_dir():
            candidates = sorted(path.relative_to(project_root) for path in source.rglob("*") if path.is_file())
        elif source.is_file():
            candidates = [source.relative_to(project_root)]
        else:
            errors.append(f"changed path is missing in promotion worktree: {raw_path}")
            continue
        for candidate in candidates:
            key = candidate.as_posix()
            if key not in seen:
                files.append(candidate)
                seen.add(key)
    return sorted(files, key=lambda path: path.as_posix()), errors


def build_promotion_apply_payload(
    project_root: Path,
    target: str,
    codex_home: Path | None = None,
    *,
    force: bool = False,
) -> dict[str, Any]:
    """Apply an accepted isolated promotion into the active project without committing it."""
    detail = build_promotion_detail_payload(project_root, target, codex_home)
    promotion = detail["promotion"]
    base: dict[str, Any] = {
        "schemaVersion": 1,
        "projectRoot": detail["projectRoot"],
        "codexHome": detail["codexHome"],
        "projectId": detail["projectId"],
        "promotion": promotion,
        "appliedFiles": [],
        "activeStatusBefore": [],
        "activeStatusAfter": [],
        "error": detail["error"],
        "noop": False,
        "message": None,
    }
    if promotion is None:
        return base

    state = str(promotion.get("state") or "")
    if state == "applied" and not force:
        active_project_root = Path(str(detail["projectRoot"])).resolve()
        base["activeStatusBefore"] = _governed_status(active_project_root) or []
        base["activeStatusAfter"] = list(base["activeStatusBefore"])
        base["appliedFiles"] = []
        base["noop"] = True
        base["message"] = "promotion is already applied"
        base["error"] = None
        return base
    if state != "accepted" and not force:
        base["error"] = f"promotion must be accepted before apply; current state is {state or '<unknown>'}"
        return base

    active_project_root = Path(str(detail["projectRoot"])).resolve()
    promotion_project_root = _promotion_project_root(active_project_root, promotion)
    active_status_before = _governed_status(active_project_root)
    if active_status_before is None:
        base["error"] = "active project git status is unavailable"
        return base
    base["activeStatusBefore"] = active_status_before

    active_git_root = _git_root(active_project_root)
    promotion_git_root = _git_root(promotion_project_root)
    active_head = _git_head(active_project_root) if active_git_root is not None else None
    promotion_head = _git_head(promotion_project_root) if promotion_git_root is not None else None
    if active_head and promotion_head and active_head != promotion_head and not force:
        base["error"] = "promotion worktree HEAD does not match the active project HEAD; use --force to apply anyway"
        return base

    changed_files, errors = _changed_governed_files(promotion_project_root)
    if errors:
        base["error"] = "; ".join(errors)
        return base
    if not changed_files:
        base["error"] = "promotion has no .governed file changes to apply"
        return base
    if active_status_before and not force:
        active_paths = _status_paths(active_status_before)
        changed_paths = {path.as_posix() for path in changed_files}
        overlaps = sorted(
            active_path
            for active_path in active_paths
            if any(_paths_overlap(active_path, changed_path) for changed_path in changed_paths)
        )
        if overlaps:
            base["error"] = (
                "active project .governed has overlapping uncommitted changes; "
                f"use --force to apply anyway: {', '.join(overlaps)}"
            )
            return base

    applied_files: list[str] = []
    for relative_path in changed_files:
        source = promotion_project_root / relative_path
        destination = active_project_root / relative_path
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        applied_files.append(relative_path.as_posix())

    metadata_path = Path(str(promotion["metadataPath"]))
    existing = read_promotion_metadata(metadata_path) or _metadata_from_promotion(detail, promotion)
    write_promotion_metadata(
        metadata_path,
        applied_promotion_metadata(existing, project_root=active_project_root, files=applied_files),
    )
    result = build_promotion_detail_payload(active_project_root, str(promotion["runId"]), Path(str(detail["codexHome"])))
    base["promotion"] = result["promotion"]
    base["appliedFiles"] = applied_files
    base["activeStatusAfter"] = _governed_status(active_project_root) or []
    base["error"] = None
    base["message"] = f"applied {len(applied_files)} file(s)"
    return base


def _detail_with_noop(detail: dict[str, Any], message: str) -> dict[str, Any]:
    updated = dict(detail)
    updated["noop"] = True
    updated["message"] = message
    return updated


def _write_review_state(args, *, state: str) -> int:
    detail = build_promotion_detail_payload(Path(args.project_root), args.promotion, getattr(args, "codex_home", None))
    promotion = detail["promotion"]
    if promotion is None:
        if getattr(args, "json", False):
            print(json.dumps(detail, indent=2, sort_keys=True))
        else:
            print(f"error: {detail['error']}", file=sys.stderr)
        return 1

    if promotion.get("state") == state:
        result = _detail_with_noop(detail, f"promotion is already {state}")
        if getattr(args, "json", False):
            print(json.dumps(result, indent=2, sort_keys=True))
        else:
            print(f"Promotion {promotion['runId']} is already {state}; no lifecycle metadata changed.")
            print(f"Lifecycle metadata: {promotion['metadataPath']}")
        return 0

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
    result["noop"] = False
    result["message"] = f"marked promotion as {state}"
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


def _run_apply(args) -> int:
    result = build_promotion_apply_payload(
        Path(args.project_root),
        args.promotion,
        getattr(args, "codex_home", None),
        force=getattr(args, "force", False),
    )
    if getattr(args, "json", False):
        print(json.dumps(result, indent=2, sort_keys=True))
        return 1 if result["error"] else 0
    if result["error"]:
        print(f"error: {result['error']}", file=sys.stderr)
        return 1
    promotion = result["promotion"] or {}
    if result.get("noop"):
        print(f"Promotion {promotion.get('runId', args.promotion)} is already applied; no files were copied.")
        if result["activeStatusAfter"]:
            print("Active project git status:")
            for line in result["activeStatusAfter"]:
                print(f"  {line}")
        return 0
    print(f"Applied promotion {promotion.get('runId', args.promotion)} into {result['projectRoot']}.")
    print("Git history unchanged; review and commit the active project changes through the normal project flow.")
    if result["appliedFiles"]:
        print("Applied files:")
        for path in result["appliedFiles"]:
            print(f"  {path}")
    if result["activeStatusAfter"]:
        print("Active project git status:")
        for line in result["activeStatusAfter"]:
            print(f"  {line}")
    return 0


def _run_archive(args) -> int:
    detail = build_promotion_detail_payload(Path(args.project_root), args.promotion, getattr(args, "codex_home", None))
    promotion = detail["promotion"]
    if promotion is None:
        if getattr(args, "json", False):
            print(json.dumps(detail, indent=2, sort_keys=True))
        else:
            print(f"error: {detail['error']}", file=sys.stderr)
        return 1

    if promotion.get("state") == "archived":
        result = _detail_with_noop(detail, "promotion is already archived")
        if getattr(args, "json", False):
            print(json.dumps(result, indent=2, sort_keys=True))
        else:
            print(f"Promotion {promotion['runId']} is already archived; no lifecycle metadata changed.")
            print(f"Lifecycle metadata: {promotion['metadataPath']}")
            print("Git worktree and history unchanged.")
        return 0

    metadata_path = Path(str(promotion["metadataPath"]))
    existing = read_promotion_metadata(metadata_path) or _metadata_from_promotion(detail, promotion)
    updated = archived_promotion_metadata(existing, reason=getattr(args, "reason", None))
    write_promotion_metadata(metadata_path, updated)
    result = build_promotion_detail_payload(Path(args.project_root), str(promotion["runId"]), getattr(args, "codex_home", None))
    result["noop"] = False
    result["message"] = "archived promotion"
    if getattr(args, "json", False):
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"Archived promotion {promotion['runId']} in GovKB lifecycle metadata.")
        print(f"Lifecycle metadata: {metadata_path}")
        print("Git worktree and history unchanged.")
    return 0
