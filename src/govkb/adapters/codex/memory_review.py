"""Contract-derived helpers for the Codex memory-review adapter."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import re
from typing import Any

from govkb.core.contracts import ValidationResult
from govkb.core.contracts import load_project_bundle
from govkb.core.project import resolve_project_root


GENERIC_RELEVANCE_PATTERNS = [
    re.compile(r"(?i)\bseverity:\b"),
    re.compile(r"(?i)\bretrospective\b"),
    re.compile(r"(?i)\broot cause\b"),
    re.compile(r"(?i)\bregression\b"),
    re.compile(r"(?i)\brecommendation\b"),
    re.compile(r"(?i)\bimplementation-plan\b"),
    re.compile(r"(?i)\bverification:\b"),
    re.compile(r"(?i)\breview\b"),
    re.compile(r"(?i)\bbugfix\b"),
    re.compile(r"(?i)\bworkflow\b"),
    re.compile(r"(?i)\brunbook\b"),
    re.compile(r"(?i)\bplaybook\b"),
    re.compile(r"(?i)\bstartup\b"),
    re.compile(r"(?i)\b(integration|unit) tests?\b"),
    re.compile(r"(?i)\b(dotnet test|go test|cargo test|pytest|python3? -m pytest|python3? -m unittest|npm (?:run )?test|pnpm test|yarn test)\b"),
    re.compile(r"(?i)\bverification commands?\b"),
    re.compile(r"(?i)\beffective ports?\b"),
]


SELF_REFERENTIAL_PATTERNS = [
    re.compile(r"(?i)codex-memory-review"),
    re.compile(r"(?i)\.codex/memories/codex-memory-review"),
    re.compile(r"(?i)\bsession_index\.jsonl\b"),
    re.compile(r"(?i)\bstate\.json\b"),
    re.compile(r"(?i)\bcron\.log\b"),
    re.compile(r"(?i)\blatest report\b"),
    re.compile(r"(?i)\bshow me .*report\b"),
    re.compile(r"(?i)\bhow .*task works\b"),
    re.compile(r"(?i)\bgoal of that task\b"),
    re.compile(r"(?i)\bwhere it could be improved\b"),
    re.compile(r"(?i)\bwhat is the schedule\b"),
]


@dataclass(frozen=True)
class GovernedMemoryTarget:
    """Resolved governed memory target for one capability."""

    skill: str
    path: Path
    requires_explicit_acceptance: bool
    headings: tuple[str, ...]
    content: str
    aliases: tuple[str, ...]
    hints: tuple[str, ...]
    negative_hints: tuple[str, ...]


@dataclass(frozen=True)
class SessionSignals:
    """Contract-derived signals for one session."""

    explicit_skills: tuple[str, ...]
    hinted_skills: tuple[str, ...]
    generic_relevance: bool
    self_referential: bool


def _dedupe_keep_order(items: list[str]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(item for item in items if item))


def _extract_headings(text: str) -> tuple[str, ...]:
    return tuple(match.group(1).strip() for match in re.finditer(r"^##\s+(.+?)\s*$", text, re.M))


def _memory_source_path(capability_root: Path, relative_path: str, fallback_root: Path | None) -> Path | None:
    repo_path = capability_root / relative_path
    if repo_path.is_file():
        return repo_path
    if fallback_root is not None:
        fallback_path = fallback_root / relative_path
        if fallback_path.is_file():
            return fallback_path
    return None


def discover_governed_memory_targets(project_root: Path) -> tuple[dict[str, GovernedMemoryTarget], ValidationResult]:
    """Load governed memory targets for a repo package."""
    bundle, result = load_project_bundle(project_root)
    targets: dict[str, GovernedMemoryTarget] = {}

    for capability_id, contract in sorted(bundle.capabilities.items()):
        if not contract.memory_enabled or not contract.targets:
            continue
        primary_target = contract.targets[0]
        if len(contract.targets) > 1:
            result.add_warning(contract.source_path, f"multiple memory targets defined; using first target for {capability_id}")
        source_path = _memory_source_path(
            contract.capability_root,
            primary_target.path,
            contract.migration_source_path,
        )
        if source_path is None:
            result.add_warning(contract.source_path, f"memory target file not found: {primary_target.path}")
            continue
        content = source_path.read_text(encoding="utf-8", errors="replace")
        targets[capability_id] = GovernedMemoryTarget(
            skill=capability_id,
            path=source_path,
            requires_explicit_acceptance=contract.requires_explicit_acceptance,
            headings=_extract_headings(content),
            content=content,
            aliases=contract.aliases,
            hints=contract.hints,
            negative_hints=contract.negative_hints,
        )

    return targets, result


def resolve_session_project_root(session_path: Path) -> Path | None:
    """Resolve the governed project root from a session JSONL file."""
    try:
        with session_path.open("r", encoding="utf-8", errors="replace") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    row = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if row.get("type") != "session_meta":
                    continue
                payload = row.get("payload") or {}
                if not isinstance(payload, dict):
                    continue
                cwd = payload.get("cwd")
                if isinstance(cwd, str) and cwd.strip():
                    resolved = resolve_project_root(Path(cwd).expanduser())
                    if (resolved / ".governed").is_dir():
                        return resolved
    except FileNotFoundError:
        return None
    return None


def collect_session_signals(
    user_text: str,
    assistant_text: str,
    task_complete_text: str,
    targets: dict[str, GovernedMemoryTarget],
) -> SessionSignals:
    """Collect contract-derived skill routing signals from session text."""
    user_and_assistant = f"{user_text}\n{assistant_text}".lower()
    combined = f"{user_text}\n{assistant_text}\n{task_complete_text}".lower()

    explicit_skills = _dedupe_keep_order(
        [
            target.skill
            for target in targets.values()
            if any(alias.lower() in user_and_assistant for alias in ((target.skill, f"${target.skill}") + target.aliases))
        ]
    )
    hinted_skills = _dedupe_keep_order(
        [
            target.skill
            for target in targets.values()
            if target.hints
            and any(hint.lower() in combined for hint in target.hints)
            and not any(negative.lower() in combined for negative in target.negative_hints)
        ]
    )
    generic_relevance = any(pattern.search(combined) for pattern in GENERIC_RELEVANCE_PATTERNS)
    self_referential = any(pattern.search(user_text) for pattern in SELF_REFERENTIAL_PATTERNS)
    return SessionSignals(
        explicit_skills=explicit_skills,
        hinted_skills=hinted_skills,
        generic_relevance=generic_relevance,
        self_referential=self_referential,
    )


def prompt_targets_for_session(
    targets: dict[str, GovernedMemoryTarget],
    signals: SessionSignals,
) -> dict[str, GovernedMemoryTarget]:
    """Prioritize explicit or hinted capabilities without making hints the only prompt path."""
    if signals.explicit_skills:
        return {skill: targets[skill] for skill in signals.explicit_skills if skill in targets}
    ordered = list(signals.hinted_skills) + [skill for skill in targets if skill not in signals.hinted_skills]
    return {skill: targets[skill] for skill in ordered if skill in targets}
