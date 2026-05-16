"""Promote local Codex governed memory changes back into the repo package."""

from __future__ import annotations

from dataclasses import dataclass
import difflib
import json
from pathlib import Path
import subprocess
from typing import Any

from govkb.core.contracts import ProjectBundle
from govkb.core.contracts import load_project_bundle
from govkb.core.install_state import default_codex_home
from govkb.core.install_state import install_state_path
from govkb.core.install_state import iso_utc_now
from govkb.core.install_state import load_install_state
from govkb.core.memory_scaffold import is_scaffold_bullet
from govkb.core.promotion_lifecycle import initial_promotion_metadata
from govkb.core.promotion_lifecycle import promotion_project_key
from govkb.core.promotion_lifecycle import promotion_metadata_path
from govkb.core.promotion_lifecycle import read_promotion_metadata
from govkb.core.promotion_lifecycle import write_promotion_metadata


@dataclass(frozen=True)
class PromotionItem:
    """One capability memory promotion result."""

    capability_id: str
    repo_path: Path
    local_path: Path
    promoted: bool
    reason: str
    additions: tuple[str, ...]


@dataclass(frozen=True)
class GitHygiene:
    """Git status context for promotion visibility."""

    available: bool
    root: Path | None
    status_before: tuple[str, ...]
    status_after: tuple[str, ...]
    message: str


@dataclass(frozen=True)
class WorktreeIsolation:
    """Git worktree used for automated promotion handoff."""

    attempted: bool
    branch: str | None
    worktree_root: Path | None
    project_root: Path | None
    message: str


@dataclass(frozen=True)
class PromotionResult:
    """Summary of one promotion run."""

    project_id: str
    codex_home: Path
    state_path: Path
    preview: bool
    auto: bool
    items: tuple[PromotionItem, ...]
    git: GitHygiene
    report_path: Path | None
    digest_path: Path | None
    isolation: WorktreeIsolation | None = None

    @property
    def promoted_count(self) -> int:
        return sum(1 for item in self.items if item.promoted)

    @property
    def rejected_count(self) -> int:
        return sum(1 for item in self.items if not item.promoted and item.reason.startswith("rejected"))


def _split_sections(text: str) -> tuple[list[str], list[tuple[str, list[str]]]]:
    """Split markdown into preamble and level-2 sections."""
    lines = text.splitlines()
    preamble: list[str] = []
    sections: list[tuple[str, list[str]]] = []
    current_heading: str | None = None
    current_lines: list[str] = []

    for line in lines:
        if line.startswith("## "):
            if current_heading is None:
                preamble = current_lines
            else:
                sections.append((current_heading, current_lines))
            current_heading = line[3:].strip()
            current_lines = []
            continue
        current_lines.append(line)

    if current_heading is None:
        preamble = current_lines
    else:
        sections.append((current_heading, current_lines))
    return preamble, sections


def _validate_append_only(repo_text: str, local_text: str, allowed_sections: tuple[str, ...]) -> tuple[bool, str, tuple[str, ...]]:
    """Allow only inserted bullet lines inside configured memory sections."""
    repo_preamble, repo_sections = _split_sections(repo_text)
    local_preamble, local_sections = _split_sections(local_text)
    if repo_preamble != local_preamble:
        return False, "rejected: preamble changed", ()
    if [heading for heading, _ in repo_sections] != [heading for heading, _ in local_sections]:
        return False, "rejected: section order or headings changed", ()

    allowed = set(allowed_sections)
    additions: list[str] = []
    for (repo_heading, repo_lines), (local_heading, local_lines) in zip(repo_sections, local_sections, strict=True):
        if repo_heading != local_heading:
            return False, "rejected: section heading changed", ()
        if repo_heading not in allowed:
            if repo_lines != local_lines:
                return False, f"rejected: non-target section changed: {repo_heading}", ()
            continue

        normalized_repo = [line for line in repo_lines if line.strip()]
        normalized_local = [line for line in local_lines if line.strip()]
        matcher = difflib.SequenceMatcher(a=normalized_repo, b=normalized_local, autojunk=False)
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == "equal":
                continue
            if tag != "insert":
                return False, f"rejected: existing lines changed in section: {repo_heading}", ()
            inserted = normalized_local[j1:j2]
            for line in inserted:
                stripped = line.strip()
                if stripped and not stripped.startswith("- "):
                    return False, f"rejected: inserted non-bullet line in section: {repo_heading}", ()
                if stripped and not is_scaffold_bullet(stripped):
                    additions.append(stripped)
    if not additions:
        return False, "unchanged", ()
    return True, "promoted: append-only memory additions", tuple(additions)


def _git_root(project_root: Path) -> Path | None:
    proc = subprocess.run(
        ["git", "-C", str(project_root), "rev-parse", "--show-toplevel"],
        text=True,
        capture_output=True,
        check=False,
    )
    if proc.returncode != 0:
        return None
    root = proc.stdout.strip()
    return Path(root).resolve() if root else None


def _git_status(root: Path, project_root: Path) -> tuple[str, ...]:
    try:
        pathspec = str((project_root / ".governed").resolve().relative_to(root))
    except ValueError:
        pathspec = str(project_root / ".governed")
    proc = subprocess.run(
        ["git", "-C", str(root), "status", "--short", "--", pathspec],
        text=True,
        capture_output=True,
        check=False,
    )
    if proc.returncode != 0:
        return (f"git status failed: {proc.stderr.strip()}",)
    return tuple(line for line in proc.stdout.splitlines() if line.strip())


def _git_head(root: Path) -> str | None:
    proc = subprocess.run(
        ["git", "-C", str(root), "rev-parse", "--verify", "HEAD"],
        text=True,
        capture_output=True,
        check=False,
    )
    if proc.returncode != 0:
        return None
    head = proc.stdout.strip()
    return head or None


def _safe_branch_component(value: str) -> str:
    return promotion_project_key(value)


def _worktree_run_id() -> str:
    return iso_utc_now().replace(":", "").replace("-", "").replace(".", "")


def _add_promotion_worktree(git_root: Path, worktree_root: Path, branch: str) -> tuple[bool, str]:
    worktree_root.parent.mkdir(parents=True, exist_ok=True)
    proc = subprocess.run(
        ["git", "-C", str(git_root), "worktree", "add", "-b", branch, str(worktree_root), "HEAD"],
        text=True,
        capture_output=True,
        check=False,
    )
    if proc.returncode == 0:
        return True, "created isolated git worktree for automated promotion review"
    detail = (proc.stderr or proc.stdout).strip()
    return False, f"skipped: git worktree add failed: {detail}"


def _existing_equivalent_isolated_worktree(
    *,
    active_root: Path,
    relative_project_root: Path,
    codex_home: Path,
    project_id: str,
    safe_project_id: str,
    items: tuple[PromotionItem, ...],
) -> WorktreeIsolation | None:
    worktrees_root = codex_home / "memories" / "govkb" / "worktrees" / safe_project_id
    if not worktrees_root.is_dir():
        return None
    comparable = [item for item in items if item.additions]
    if not comparable:
        return None
    for worktree_root in sorted(worktrees_root.iterdir(), reverse=True):
        if not worktree_root.is_dir():
            continue
        metadata = read_promotion_metadata(promotion_metadata_path(codex_home, project_id, worktree_root.name))
        if metadata and metadata.get("state") in {"rejected", "archived"}:
            continue
        project_root = worktree_root / relative_project_root
        if not (project_root / ".governed").exists():
            project_root = worktree_root
        if not (project_root / ".governed").exists():
            continue
        equivalent = True
        for item in comparable:
            try:
                relative_path = item.repo_path.resolve().relative_to(active_root)
            except ValueError:
                equivalent = False
                break
            candidate_path = project_root / relative_path
            if not candidate_path.is_file() or not item.local_path.is_file():
                equivalent = False
                break
            if candidate_path.read_text(encoding="utf-8").rstrip() != item.local_path.read_text(encoding="utf-8").rstrip():
                equivalent = False
                break
        if equivalent:
            branch = str(metadata.get("branch") or "") if metadata else None
            return WorktreeIsolation(
                attempted=True,
                branch=branch or None,
                worktree_root=worktree_root,
                project_root=project_root,
                message=f"skipped: equivalent isolated promotion already exists ({worktree_root.name})",
            )
    return None


def _git_hygiene_before(project_root: Path) -> GitHygiene:
    root = _git_root(project_root)
    if root is None:
        return GitHygiene(
            available=False,
            root=None,
            status_before=(),
            status_after=(),
            message="git unavailable: project root is not inside a git worktree",
        )
    status = _git_status(root, project_root)
    message = "git clean for .governed" if not status else "git already had .governed changes before promotion"
    return GitHygiene(
        available=True,
        root=root,
        status_before=status,
        status_after=(),
        message=message,
    )


def _git_hygiene_after(project_root: Path, before: GitHygiene) -> GitHygiene:
    if not before.available or before.root is None:
        return before
    status_after = _git_status(before.root, project_root)
    if not status_after:
        message = "git clean for .governed"
    elif before.status_before and before.status_before != status_after:
        message = "git .governed status changed; review before commit"
    elif before.status_before:
        message = "git .governed status unchanged from before promotion"
    else:
        message = "git .governed now has promotion changes to review"
    return GitHygiene(
        available=True,
        root=before.root,
        status_before=before.status_before,
        status_after=status_after,
        message=message,
    )


def _write_report(project_root: Path, result: PromotionResult, run_id: str) -> Path:
    report_dir = project_root / ".governed" / "reports" / "promotions"
    report_dir.mkdir(parents=True, exist_ok=True)
    report_path = report_dir / f"{run_id}-promote-report.md"
    lines = [
        f"# GovKB Promotion - {run_id}",
        "",
        f"- Mode: {'preview' if result.preview else 'apply'}",
        f"- Trigger: {'auto' if result.auto else 'manual'}",
        f"- Project: {result.project_id}",
        f"- Codex home: {result.codex_home}",
        f"- Install state: {result.state_path}",
        f"- Promoted: {result.promoted_count}",
        f"- Rejected: {result.rejected_count}",
        f"- Git: {result.git.message}",
    ]
    if result.git.root is not None:
        lines.append(f"- Git root: {result.git.root}")
    if result.isolation is not None:
        lines.append(f"- Isolation: {result.isolation.message}")
        if result.isolation.branch is not None:
            lines.append(f"- Isolation branch: {result.isolation.branch}")
        if result.isolation.worktree_root is not None:
            lines.append(f"- Isolation worktree: {result.isolation.worktree_root}")
    lines.extend(["", "## Git Status Before"])
    if result.git.status_before:
        lines.extend(f"- `{line}`" for line in result.git.status_before)
    else:
        lines.append("- None")
    lines.extend(["", "## Git Status After"])
    if result.git.status_after:
        lines.extend(f"- `{line}`" for line in result.git.status_after)
    else:
        lines.append("- None")
    lines.extend(["", "## Items"])
    if not result.items:
        lines.append("- None")
    for item in result.items:
        lines.append(
            f"- `{item.capability_id}` | {'promoted' if item.promoted else 'not promoted'} | {item.reason}"
        )
        lines.append(f"  Local: `{item.local_path}`")
        lines.append(f"  Repo: `{item.repo_path}`")
        for addition in item.additions:
            lines.append(f"  Addition: {addition[:300]}")
    report_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return report_path


def _promotion_additions_payload(items: tuple[PromotionItem, ...]) -> list[dict[str, object]]:
    """Return promoted additions in a metadata-friendly shape."""
    return [
        {
            "capabilityId": item.capability_id,
            "repoPath": str(item.repo_path),
            "additions": list(item.additions),
        }
        for item in items
        if item.promoted and item.additions
    ]


def _accepted_additions_by_capability(codex_home: Path, project_id: str) -> dict[str, set[str]]:
    """Return additions that already have an accepted lifecycle decision."""
    root = promotion_metadata_path(codex_home, project_id, "placeholder").parent
    accepted: dict[str, set[str]] = {}
    if not root.is_dir():
        return accepted
    for metadata_path in root.glob("*.json"):
        metadata = read_promotion_metadata(metadata_path)
        if not metadata:
            continue
        review = metadata.get("review")
        if not isinstance(review, dict) or review.get("decision") != "accepted":
            continue
        for item in metadata.get("promotedAdditions") or []:
            if not isinstance(item, dict):
                continue
            capability_id = item.get("capabilityId")
            additions = item.get("additions")
            if not isinstance(capability_id, str) or not isinstance(additions, list):
                continue
            accepted.setdefault(capability_id, set()).update(addition for addition in additions if isinstance(addition, str))
    return accepted


def _write_digest(project_root: Path, result: PromotionResult, run_id: str, report_path: Path) -> Path:
    digest_dir = project_root / ".governed" / "reports" / "promotions"
    digest_dir.mkdir(parents=True, exist_ok=True)
    digest_path = digest_dir / "latest-promotion-digest.md"
    lines = [
        "# Latest GovKB Promotion Digest",
        "",
        f"- Run: `{run_id}`",
        f"- Mode: {'preview' if result.preview else 'apply'}",
        f"- Trigger: {'auto' if result.auto else 'manual'}",
        f"- Report: `{report_path}`",
        f"- Digest: `{digest_path}`",
        f"- Promoted: {result.promoted_count}",
        f"- Rejected: {result.rejected_count}",
        f"- Git: {result.git.message}",
    ]
    if result.git.root is not None:
        lines.append(f"- Git root: `{result.git.root}`")
    if result.isolation is not None:
        lines.append(f"- Isolation: {result.isolation.message}")
        if result.isolation.branch is not None:
            lines.append(f"- Isolation branch: `{result.isolation.branch}`")
        if result.isolation.worktree_root is not None:
            lines.append(f"- Isolation worktree: `{result.isolation.worktree_root}`")
    lines.extend(["", "## Changed Files"])
    changed = result.git.status_after or result.git.status_before
    if changed:
        lines.extend(f"- `{line}`" for line in changed)
    else:
        lines.append("- None")
    accepted_additions = _accepted_additions_by_capability(result.codex_home, result.project_id)
    lines.extend(["", "## Review Scope"])
    lines.append("- Review only `New Additions To Review` before accepting or rejecting this promotion.")
    lines.append(
        "- `Previously Accepted Carry-Forward` entries are included because they have not been applied to the active governed package yet."
    )
    lines.append("- Accepting or applying this promotion still acts on the combined change set shown in this digest.")
    lines.extend(["", "## New Additions To Review"])
    promoted_items = [item for item in result.items if item.promoted]
    if not promoted_items:
        lines.append("- None")
    for item in promoted_items:
        new_additions = [addition for addition in item.additions if addition not in accepted_additions.get(item.capability_id, set())]
        if not new_additions:
            continue
        lines.append(f"- `{item.capability_id}` -> `{item.repo_path}`")
        for addition in new_additions:
            lines.append(f"  Addition: {addition[:300]}")
    if promoted_items and not any(
        addition not in accepted_additions.get(item.capability_id, set())
        for item in promoted_items
        for addition in item.additions
    ):
        lines.append("- None")
    carry_forward = [
        (item, [addition for addition in item.additions if addition in accepted_additions.get(item.capability_id, set())])
        for item in promoted_items
    ]
    carry_forward = [(item, additions) for item, additions in carry_forward if additions]
    lines.extend(["", "## Previously Accepted Carry-Forward"])
    if not carry_forward:
        lines.append("- None")
    for item, additions in carry_forward:
        lines.append(f"- `{item.capability_id}` -> `{item.repo_path}`")
        for addition in additions:
            lines.append(f"  Accepted earlier: {addition[:300]}")
    rejected_items = [item for item in result.items if not item.promoted and item.reason.startswith("rejected")]
    lines.extend(["", "## Rejections"])
    if not rejected_items:
        lines.append("- None")
    for item in rejected_items:
        lines.append(f"- `{item.capability_id}`: {item.reason}")
    digest_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return digest_path


def _with_isolation(result: PromotionResult, isolation: WorktreeIsolation) -> PromotionResult:
    return PromotionResult(
        result.project_id,
        result.codex_home,
        result.state_path,
        result.preview,
        result.auto,
        result.items,
        result.git,
        result.report_path,
        result.digest_path,
        isolation,
    )


def promote_codex_memory_in_isolated_worktree(
    project_root: Path,
    codex_home_override: Path | None,
) -> PromotionResult:
    """Promote safe local memory changes into an isolated git worktree branch."""
    active_root = project_root.resolve()
    codex_home = (codex_home_override or default_codex_home()).resolve()
    active_bundle, active_validation = load_project_bundle(active_root)
    if active_validation.errors:
        preview = promote_codex_memory(
            project_root=active_root,
            bundle=active_bundle,
            codex_home_override=codex_home,
            preview=True,
            auto=True,
            write_report=False,
        )
        return _with_isolation(
            preview,
            WorktreeIsolation(
                attempted=True,
                branch=None,
                worktree_root=None,
                project_root=None,
                message="skipped: active governed package has validation errors",
            ),
        )

    preview = promote_codex_memory(
        project_root=active_root,
        bundle=active_bundle,
        codex_home_override=codex_home,
        preview=True,
        auto=True,
        write_report=False,
    )
    if not preview.items:
        return _with_isolation(
            preview,
            WorktreeIsolation(
                attempted=True,
                branch=None,
                worktree_root=None,
                project_root=None,
                message="skipped: no safe local governed memory changes to isolate",
            ),
        )

    git_root = _git_root(active_root)
    if git_root is None:
        return _with_isolation(
            preview,
            WorktreeIsolation(
                attempted=True,
                branch=None,
                worktree_root=None,
                project_root=None,
                message="skipped: project root is not inside a git worktree",
            ),
        )
    if _git_head(git_root) is None:
        return _with_isolation(
            preview,
            WorktreeIsolation(
                attempted=True,
                branch=None,
                worktree_root=None,
                project_root=None,
                message="skipped: git worktree has no committed HEAD",
            ),
        )

    try:
        relative_project_root = active_root.relative_to(git_root)
    except ValueError:
        return _with_isolation(
            preview,
            WorktreeIsolation(
                attempted=True,
                branch=None,
                worktree_root=None,
                project_root=None,
                message="skipped: project root is outside the git root",
            ),
        )

    project_id = active_bundle.project_id or "unknown-project"
    safe_project_id = _safe_branch_component(project_id)
    existing_isolation = _existing_equivalent_isolated_worktree(
        active_root=active_root,
        relative_project_root=relative_project_root,
        codex_home=codex_home,
        project_id=project_id,
        safe_project_id=safe_project_id,
        items=preview.items,
    )
    if existing_isolation is not None:
        return _with_isolation(preview, existing_isolation)

    run_id = _worktree_run_id()
    branch = f"codex/govkb-auto-promote/{safe_project_id}/{run_id}"
    worktree_root = codex_home / "memories" / "govkb" / "worktrees" / safe_project_id / run_id
    ok, message = _add_promotion_worktree(git_root, worktree_root, branch)
    isolation = WorktreeIsolation(
        attempted=True,
        branch=branch if ok else None,
        worktree_root=worktree_root if ok else None,
        project_root=(worktree_root / relative_project_root) if ok else None,
        message=message,
    )
    if not ok or isolation.project_root is None:
        return _with_isolation(preview, isolation)

    isolated_bundle, isolated_validation = load_project_bundle(isolation.project_root)
    if isolated_validation.errors:
        return _with_isolation(
            preview,
            WorktreeIsolation(
                attempted=True,
                branch=branch,
                worktree_root=worktree_root,
                project_root=isolation.project_root,
                message="skipped: isolated governed package has validation errors",
            ),
        )

    isolated_result = promote_codex_memory(
        project_root=isolation.project_root,
        bundle=isolated_bundle,
        codex_home_override=codex_home,
        preview=False,
        auto=True,
        write_report=False,
    )
    final = _with_isolation(isolated_result, isolation)
    if final.items:
        report_path = _write_report(isolation.project_root, final, run_id)
        digest_path = _write_digest(isolation.project_root, final, run_id, report_path)
        final = PromotionResult(
            final.project_id,
            final.codex_home,
            final.state_path,
            final.preview,
            final.auto,
            final.items,
            _git_hygiene_after(isolation.project_root, final.git),
            report_path,
            digest_path,
            final.isolation,
        )
        _write_report(isolation.project_root, final, run_id)
        _write_digest(isolation.project_root, final, run_id, report_path)
        write_promotion_metadata(
            promotion_metadata_path(codex_home, project_id, run_id),
            initial_promotion_metadata(
                project_id=project_id,
                project_root=active_root,
                codex_home=codex_home,
                run_id=run_id,
                branch=branch,
                worktree_root=worktree_root,
                digest_path=digest_path,
                report_path=report_path,
                promoted_additions=_promotion_additions_payload(final.items),
            ),
        )
    return final


def promote_codex_memory(
    project_root: Path,
    bundle: ProjectBundle,
    codex_home_override: Path | None,
    *,
    preview: bool,
    auto: bool,
    write_report: bool = True,
) -> PromotionResult:
    """Promote safe local Codex memory changes into the repo-governed package."""
    project_id = bundle.project_id or "unknown-project"
    codex_home = (codex_home_override or default_codex_home()).resolve()
    state_path = install_state_path(codex_home, project_id, "codex")
    git_before = _git_hygiene_before(project_root)
    state = load_install_state(state_path)
    if state is None:
        result = PromotionResult(
            project_id,
            codex_home,
            state_path,
            preview,
            auto,
            (),
            _git_hygiene_after(project_root, git_before),
            None,
            None,
        )
        if write_report:
            run_id = iso_utc_now().replace(":", "").replace("-", "")
            report_path = _write_report(project_root, result, run_id)
            digest_path = _write_digest(project_root, result, run_id, report_path)
            final = PromotionResult(
                project_id,
                codex_home,
                state_path,
                preview,
                auto,
                (),
                _git_hygiene_after(project_root, git_before),
                report_path,
                digest_path,
            )
            _write_report(project_root, final, run_id)
            _write_digest(project_root, final, run_id, report_path)
            return final
        return result

    items: list[PromotionItem] = []
    for capability_state in state.get("capabilities", []):
        if not isinstance(capability_state, dict):
            continue
        capability_id = str(capability_state.get("capability_id") or "")
        contract = bundle.capabilities.get(capability_id)
        if contract is None or not contract.targets:
            continue
        target = contract.targets[0]
        repo_path = contract.capability_root / target.path
        local_path_value = capability_state.get("memory_path")
        if not isinstance(local_path_value, str) or not local_path_value:
            continue
        local_path = Path(local_path_value)
        if not repo_path.is_file():
            items.append(PromotionItem(capability_id, repo_path, local_path, False, "rejected: repo memory missing", ()))
            continue
        if not local_path.is_file():
            items.append(PromotionItem(capability_id, repo_path, local_path, False, "rejected: local memory missing", ()))
            continue

        repo_text = repo_path.read_text(encoding="utf-8")
        local_text = local_path.read_text(encoding="utf-8")
        if repo_text == local_text:
            continue
        ok, reason, additions = _validate_append_only(repo_text, local_text, target.sections)
        if ok and not preview:
            repo_path.write_text(local_text.rstrip() + "\n", encoding="utf-8")
        promoted = ok
        item_reason = reason
        if ok and preview and auto:
            promoted = False
            item_reason = "staged: auto promotion skipped active worktree mutation"
        items.append(PromotionItem(capability_id, repo_path, local_path, promoted, item_reason, additions))

    interim = PromotionResult(
        project_id,
        codex_home,
        state_path,
        preview,
        auto,
        tuple(items),
        _git_hygiene_after(project_root, git_before),
        None,
        None,
    )
    if write_report and items:
        run_id = iso_utc_now().replace(":", "").replace("-", "")
        report_path = _write_report(project_root, interim, run_id)
        digest_path = _write_digest(project_root, interim, run_id, report_path)
        final = PromotionResult(
            project_id,
            codex_home,
            state_path,
            preview,
            auto,
            tuple(items),
            _git_hygiene_after(project_root, git_before),
            report_path,
            digest_path,
        )
        _write_report(project_root, final, run_id)
        _write_digest(project_root, final, run_id, report_path)
        return final
    return interim


def result_to_json(result: PromotionResult) -> str:
    """Serialize promotion result for tests or automation."""
    payload: dict[str, Any] = {
        "project_id": result.project_id,
        "codex_home": str(result.codex_home),
        "state_path": str(result.state_path),
        "preview": result.preview,
        "auto": result.auto,
        "report_path": str(result.report_path) if result.report_path else None,
        "digest_path": str(result.digest_path) if result.digest_path else None,
        "git": {
            "available": result.git.available,
            "root": str(result.git.root) if result.git.root else None,
            "status_before": list(result.git.status_before),
            "status_after": list(result.git.status_after),
            "message": result.git.message,
        },
        "isolation": None
        if result.isolation is None
        else {
            "attempted": result.isolation.attempted,
            "branch": result.isolation.branch,
            "worktree_root": str(result.isolation.worktree_root) if result.isolation.worktree_root else None,
            "project_root": str(result.isolation.project_root) if result.isolation.project_root else None,
            "message": result.isolation.message,
        },
        "items": [
            {
                "capability_id": item.capability_id,
                "repo_path": str(item.repo_path),
                "local_path": str(item.local_path),
                "promoted": item.promoted,
                "reason": item.reason,
                "additions": list(item.additions),
            }
            for item in result.items
        ],
    }
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"
