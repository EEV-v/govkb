"""Read-only project health and freshness diagnostics."""

from __future__ import annotations

import json
from pathlib import Path
import re
import subprocess
from typing import Any

from govkb.commands.status import build_status_payload
from govkb.core.ids import normalize_identifier
from govkb.core.install_state import default_codex_home
from govkb.core.proposal_report import build_proposal_review_payload


REPORT_COUNT_KEYS = {
    "Sessions processed": "sessionsProcessed",
    "Skipped before classification": "skippedBeforeClassification",
    "Deferred sessions": "deferredSessions",
    "Applied": "applied",
    "Staged": "staged",
    "Capability candidates": "capabilityCandidates",
    "Capability evolution proposals": "capabilityEvolutionProposals",
    "Rejected capability evolution proposals": "rejectedCapabilityEvolutionProposals",
    "Rejected": "rejected",
    "Failed sessions": "failedSessions",
    "Total sessions discovered": "totalSessionsDiscovered",
    "Already processed sessions": "alreadyProcessedSessions",
    "Selected before max-session limit": "selectedBeforeLimit",
    "Indexed rows seen": "indexedRows",
    "Indexed rows missing session file": "indexedRowsMissingSessionFile",
    "File-only recent unprocessed sessions detected": "fileOnlyRecentUnprocessedSessions",
    "Selected from indexed path": "selectedFromIndexedPath",
    "Selected from file-only path": "selectedFromFileOnlyPath",
}
REPORT_STRING_KEYS = {
    "Mode": "mode",
    "Classifier model": "classifierModel",
    "Classifier reasoning": "classifierReasoning",
    "Classifier timeout seconds": "classifierTimeoutSeconds",
}


def build_doctor_payload(project_root: Path, codex_home: Path | None = None) -> dict[str, Any]:
    """Build one read-only health payload for a governed project."""
    resolved_home = (codex_home or default_codex_home()).resolve()
    bundle, validation, status = build_status_payload(project_root.resolve(), resolved_home)
    project_id = normalize_identifier(bundle.project_id or bundle.project_root.name)
    proposals = build_proposal_review_payload(bundle.project_root)
    memory_review = _memory_review_payload(resolved_home, project_id)
    cron = _cron_payload(bundle.project_root, resolved_home, project_id)
    recommendations = _recommendations(bundle.project_root, resolved_home, status, proposals, memory_review, cron)
    state = _overall_state(status, proposals, memory_review, cron, recommendations)
    return {
        "schemaVersion": 1,
        "projectRoot": status["projectRoot"],
        "codexHome": str(resolved_home),
        "state": state,
        "project": status["project"],
        "validation": status["validation"],
        "installState": status["installState"],
        "skillUpdates": status["skillUpdates"],
        "proposalQueue": {
            "summary": proposals["summary"],
            "reviewGroups": [
                {
                    "id": group["id"],
                    "recommendedAction": group["recommendedAction"],
                    "proposalIds": group["proposalIds"],
                    "warningCodes": group["warningCodes"],
                }
                for group in proposals["groups"]
            ],
        },
        "memoryReview": memory_review,
        "cron": cron,
        "recommendations": recommendations,
    }


def run_doctor(args) -> int:
    """Show read-only project health and freshness diagnostics."""
    codex_home = Path(args.codex_home).resolve() if args.codex_home else None
    payload = build_doctor_payload(Path(args.project_root).resolve(), codex_home)
    if getattr(args, "json", False):
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 1 if payload["validation"]["status"] == "error" else 0

    project = payload["project"]
    proposals = payload["proposalQueue"]["summary"]
    memory = payload["memoryReview"]
    cron = payload["cron"]
    print(f"Project: {payload['projectRoot']}")
    print(f"State: {payload['state']}")
    print(f"Validation: {payload['validation']['status']}")
    print(f"Repo revision: {project.get('gitRevision') or '<unknown>'}")
    print(f"Installed revision: {payload['installState']['codex'].get('appliedRevision') or '<none>'}")
    print(f"Skill updates: {payload['skillUpdates']['state']}")
    print(
        "Proposals: "
        f"{proposals['proposalCount']} | groups={proposals['groupCount']} | warnings={proposals['warningCount']}"
    )
    print(
        "Memory review: "
        f"state={memory['state']['status']} | latest={memory['latestRun']['status']} | "
        f"processed={memory['state']['processedSessionCount']}"
    )
    if memory["latestRun"]["path"]:
        print(f"Latest memory-review report: {memory['latestRun']['path']}")
    print(f"Cron: {cron['status']}")
    if payload["recommendations"]:
        print("")
        print("Next:")
        for item in payload["recommendations"]:
            print(f"- {item['message']}")
            if item.get("command"):
                print(f"  {item['command']}")
    return 1 if payload["validation"]["status"] == "error" else 0


def _memory_review_payload(codex_home: Path, project_id: str) -> dict[str, Any]:
    state_dir = codex_home / "memories" / "govkb" / "projects" / project_id / "codex-memory-review"
    state_path = state_dir / "state.json"
    report_dir = state_dir / "reports"
    return {
        "stateDir": str(state_dir),
        "statePath": str(state_path),
        "reportDir": str(report_dir),
        "state": _state_payload(state_path),
        "latestRun": _latest_report_payload(report_dir),
    }


def _state_payload(state_path: Path) -> dict[str, Any]:
    if not state_path.is_file():
        return {
            "status": "missing",
            "lastRunAt": None,
            "lastSuccessfulUpdatedAt": None,
            "processedSessionCount": 0,
            "error": None,
        }
    try:
        data = json.loads(state_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return {
            "status": "invalid",
            "lastRunAt": None,
            "lastSuccessfulUpdatedAt": None,
            "processedSessionCount": 0,
            "error": str(exc),
        }
    processed = data.get("processed_sessions") if isinstance(data, dict) else None
    return {
        "status": "present" if isinstance(data, dict) else "invalid",
        "lastRunAt": data.get("last_run_at") if isinstance(data, dict) else None,
        "lastSuccessfulUpdatedAt": data.get("last_successful_updated_at") if isinstance(data, dict) else None,
        "processedSessionCount": len(processed) if isinstance(processed, dict) else 0,
        "error": None if isinstance(data, dict) else "state root is not an object",
    }


def _latest_report_payload(report_dir: Path) -> dict[str, Any]:
    reports = sorted(report_dir.glob("*-report.md")) if report_dir.is_dir() else []
    if not reports:
        return {
            "status": "missing",
            "path": None,
            "runId": None,
            "counts": {},
            "metadata": {},
        }
    latest = max(reports, key=lambda path: (path.stat().st_mtime, path.name))
    counts: dict[str, int] = {}
    metadata: dict[str, str] = {}
    for line in latest.read_text(encoding="utf-8", errors="replace").splitlines():
        match = re.match(r"^- ([^:]+):\s*(.*)$", line)
        if not match:
            continue
        label = match.group(1)
        value = match.group(2).strip()
        if label in REPORT_COUNT_KEYS:
            try:
                counts[REPORT_COUNT_KEYS[label]] = int(value)
            except ValueError:
                continue
        elif label in REPORT_STRING_KEYS:
            metadata[REPORT_STRING_KEYS[label]] = value
    status = "completed"
    if counts.get("failedSessions", 0) > 0:
        status = "failed"
    elif counts.get("deferredSessions", 0) > 0:
        status = "deferred"
    run_id = latest.name.removesuffix("-report.md")
    return {
        "status": status,
        "path": str(latest),
        "runId": run_id,
        "counts": counts,
        "metadata": metadata,
    }


def _cron_payload(project_root: Path, codex_home: Path, project_id: str) -> dict[str, Any]:
    script_path = codex_home / "bin" / "codex-memory-review"
    log_path = codex_home / "memories" / "govkb" / "projects" / project_id / "codex-memory-review" / "cron.log"
    try:
        returncode, stdout, stderr = _read_crontab()
    except FileNotFoundError:
        return {
            "status": "unavailable",
            "scriptPath": str(script_path),
            "logPath": str(log_path),
            "matchingLines": [],
            "error": "crontab command not found",
        }
    if returncode != 0 and not stdout.strip():
        return {
            "status": "missing",
            "scriptPath": str(script_path),
            "logPath": str(log_path),
            "matchingLines": [],
            "error": stderr.strip() or None,
        }
    lines = [line.strip() for line in stdout.splitlines() if line.strip()]
    matching = [line for line in lines if "codex-memory-review" in line and str(project_root) in line]
    status = "missing"
    if matching:
        status = "installed" if any(str(codex_home) in line for line in matching) else "stale"
    return {
        "status": status,
        "scriptPath": str(script_path),
        "logPath": str(log_path),
        "matchingLines": matching,
        "error": None,
    }


def _read_crontab() -> tuple[int, str, str]:
    proc = subprocess.run(["crontab", "-l"], text=True, capture_output=True, check=False)
    return proc.returncode, proc.stdout, proc.stderr


def _recommendations(
    project_root: Path,
    codex_home: Path,
    status: dict[str, Any],
    proposals: dict[str, Any],
    memory_review: dict[str, Any],
    cron: dict[str, Any],
) -> list[dict[str, str]]:
    recommendations: list[dict[str, str]] = []
    if status["validation"]["status"] == "error":
        recommendations.append(
            {
                "kind": "validation",
                "message": "Fix governed package validation errors before applying or reviewing memory.",
                "command": f"govkb validate {project_root}",
            }
        )
    if status["installState"]["codex"]["status"] == "missing":
        recommendations.append(
            {
                "kind": "install-state",
                "message": "Materialize the governed package into the configured Codex home.",
                "command": f"govkb apply codex --project-root {project_root} --codex-home {codex_home}",
            }
        )
    if cron["status"] in {"missing", "stale"}:
        recommendations.append(
            {
                "kind": "cron",
                "message": "Install or refresh the project-scoped memory-review cron job.",
                "command": f"govkb install {project_root} --codex-home {codex_home} --cron",
            }
        )
    if memory_review["latestRun"]["status"] == "missing":
        recommendations.append(
            {
                "kind": "memory-review",
                "message": "Run a bounded dry-run memory review to create the first project report.",
                "command": f"CODEX_HOME={codex_home} govkb review-memory --assistant codex --project-root {project_root} --dry-run --max-sessions 5",
            }
        )
    action_counts = proposals["summary"].get("actionCounts", {})
    if action_counts.get("inspect-safety"):
        recommendations.append(
            {
                "kind": "proposals",
                "message": "Inspect safety-sensitive staged proposals before applying anything.",
                "command": f"govkb proposals review {project_root} --action inspect-safety",
            }
        )
    if action_counts.get("merge-first"):
        recommendations.append(
            {
                "kind": "proposals",
                "message": "Reconcile related staged proposals before applying one artifact.",
                "command": f"govkb proposals review {project_root} --action merge-first",
            }
        )
    return recommendations


def _overall_state(
    status: dict[str, Any],
    proposals: dict[str, Any],
    memory_review: dict[str, Any],
    cron: dict[str, Any],
    recommendations: list[dict[str, str]],
) -> str:
    if status["validation"]["status"] == "error" or memory_review["latestRun"]["status"] == "failed":
        return "error"
    if cron["status"] in {"missing", "stale", "unavailable"}:
        return "warning"
    if proposals["summary"].get("warningCount", 0) or recommendations:
        return "attention"
    return "ok"
