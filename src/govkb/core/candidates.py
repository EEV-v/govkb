"""Governed capability candidate staging."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import re
import shutil
import tomllib
from typing import Any

from govkb.core.ids import normalize_identifier
from govkb.core.init_prompt import initialize_kb_prompt_text
from govkb.core.install_state import iso_utc_now
from govkb.core.project import resolve_project_root


STOP_WORDS = {
    "about",
    "after",
    "all",
    "again",
    "also",
    "and",
    "confirm",
    "for",
    "from",
    "have",
    "investigation",
    "investigate",
    "into",
    "make",
    "need",
    "note",
    "notes",
    "or",
    "next",
    "please",
    "project",
    "should",
    "that",
    "the",
    "this",
    "with",
    "work",
    "would",
}

GENERIC_DESCRIPTOR_TOKENS = {
    "actual",
    "brief",
    "candidate",
    "capability",
    "codex",
    "concrete",
    "current",
    "daily",
    "dedicated",
    "development",
    "durable",
    "effective",
    "existing",
    "future",
    "governed",
    "grounded",
    "knowledge",
    "latest",
    "local",
    "long",
    "main",
    "matched",
    "primary",
    "real",
    "repo",
    "reusable",
    "same",
    "short",
    "specialized",
    "stable",
    "term",
    "useful",
    "read",
    "only",
}

DOMAIN_PRIORITY_TOKENS = (
    "backend",
    "frontend",
    "worker",
    "api",
    "auth",
    "database",
    "cli",
)

STACK_SIGNAL_TOKENS = {
    "compose",
    "container",
    "containers",
    "debug",
    "docker",
    "health",
    "healthcheck",
    "localhost",
    "local",
    "override",
    "overrides",
    "port",
    "ports",
    "root",
    "stack",
    "startup",
}

TOPIC_SUFFIX_TOKENS = {
    "checklist",
    "debugging",
    "integration",
    "migration",
    "playbook",
    "runbook",
    "setup",
    "startup",
    "triage",
    "verification",
    "workflow",
}

TOPIC_BOUNDARY_TOKENS = {
    "add",
    "analyze",
    "build",
    "capture",
    "check",
    "confirm",
    "create",
    "debug",
    "define",
    "document",
    "draft",
    "evaluate",
    "explain",
    "extract",
    "find",
    "fix",
    "implement",
    "inspect",
    "investigate",
    "investigation",
    "look",
    "map",
    "produce",
    "review",
    "run",
    "show",
    "stage",
    "summarize",
    "trace",
    "update",
    "verify",
    "want",
    "write",
}

GENERIC_CANDIDATE_TOKENS = {
    "candidate",
    "capability",
    "checklist",
    "debugging",
    "governed",
    "integration",
    "knowledge",
    "migration",
    "playbook",
    "runbook",
    "setup",
    "startup",
    "triage",
    "verification",
    "workflow",
}


@dataclass(frozen=True)
class CandidateStageResult:
    """Result of staging or updating a candidate."""

    candidate_id: str
    candidate_root: Path
    status: str
    occurrences: int
    created: bool
    source_session: str
    default_capability_id: str


def _redact(text: str) -> str:
    text = re.sub(r"eyJ[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{10,}", "[REDACTED]", text)
    text = re.sub(r"(?i)\b(bearer|password|client_secret|secret)\b\s*[:=]\s*\S+", "[REDACTED]", text)
    text = re.sub(r"(?i)\b[A-Z0-9_]*(TOKEN|SECRET|PASSWORD|API_KEY|APIKEY|KEY)[A-Z0-9_]*\b\s*[:=]\s*\S+", "[REDACTED]", text)
    text = re.sub(r"\bsk-[A-Za-z0-9_-]{20,}\b", "[REDACTED]", text)
    text = re.sub(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b", "[REDACTED]", text)
    return text


def _compact(text: str, limit: int = 800) -> str:
    compacted = re.sub(r"\s+", " ", _redact(text)).strip()
    if "## My request for Codex:" in compacted:
        compacted = compacted.split("## My request for Codex:", 1)[1].strip()
    return compacted[:limit]


def _session_text(session_file: Path) -> tuple[str, str, str, str]:
    session_id = session_file.stem
    timestamp = ""
    user_parts: list[str] = []
    assistant_parts: list[str] = []
    with session_file.open("r", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            payload = row.get("payload") or {}
            if not isinstance(payload, dict):
                continue
            if row.get("type") == "session_meta":
                session_id = str(payload.get("id") or session_id)
                timestamp = str(payload.get("timestamp") or timestamp)
            payload_type = payload.get("type")
            if row.get("type") == "event_msg" and payload_type == "user_message":
                user_parts.append(str(payload.get("message", "")))
            elif row.get("type") == "event_msg" and payload_type in {"agent_message", "task_complete"}:
                assistant_parts.append(str(payload.get("message") or payload.get("last_agent_message") or ""))
    return session_id, timestamp, "\n".join(user_parts), "\n".join(assistant_parts)


def _feature_name(text: str) -> str | None:
    match = re.search(r"docs/(?:features|bugfixes)/([^/\n\r`]+)", text)
    if match:
        return match.group(1).strip()
    return None


def _tokenize(text: str) -> tuple[str, ...]:
    return tuple(token for token in re.findall(r"[A-Za-z][A-Za-z0-9]*", text.lower()) if re.search(r"[A-Za-z]", token))


def _ignored_tokens(project_root: Path) -> set[str]:
    ignored = set(_tokenize(project_root.name))
    manifest = project_root / ".governed" / "project.toml"
    if manifest.is_file():
        try:
            data = tomllib.loads(manifest.read_text(encoding="utf-8"))
        except tomllib.TOMLDecodeError:
            data = {}
        project_data = data.get("project") if isinstance(data.get("project"), dict) else {}
        for key in ("id", "name"):
            value = project_data.get(key) if isinstance(project_data, dict) else None
            if isinstance(value, str):
                ignored.update(_tokenize(value))
    return ignored


def _keywords(text: str, limit: int = 8, ignored_tokens: set[str] | None = None) -> tuple[str, ...]:
    ignored = ignored_tokens or set()
    tokens = _tokenize(text)
    seen: dict[str, int] = {}
    first_seen: dict[str, int] = {}
    for index, token in enumerate(tokens):
        if len(token) < 4:
            continue
        if token in STOP_WORDS or token in GENERIC_DESCRIPTOR_TOKENS or token in ignored:
            continue
        seen[token] = seen.get(token, 0) + 1
        first_seen.setdefault(token, index)
    ranked = sorted(seen.items(), key=lambda item: (-item[1], first_seen[item[0]]))
    return tuple(token for token, _ in ranked[:limit])


def _canonical_topic_prefix(tokens: list[str]) -> list[str]:
    if "auth" in tokens and "e2e" in tokens:
        ordered = ["auth", "e2e"]
        ordered.extend(token for token in tokens if token not in {"auth", "e2e"})
        return list(dict.fromkeys(ordered))
    return tokens


def _topic_tokens(text: str, ignored_tokens: set[str]) -> tuple[str, ...]:
    tokens = _tokenize(text)
    for index, token in enumerate(tokens):
        if token not in TOPIC_SUFFIX_TOKENS:
            continue
        window: list[str] = []
        cursor = index - 1
        while cursor >= 0 and len(window) < 6:
            current = tokens[cursor]
            if current in TOPIC_BOUNDARY_TOKENS:
                break
            if current in {"for", "from", "into", "to", "with"} and window:
                break
            window.append(current)
            cursor -= 1
        window.reverse()
        cleaned = [
            item
            for item in window
            if item not in STOP_WORDS and item not in GENERIC_DESCRIPTOR_TOKENS and item not in ignored_tokens
        ]
        cleaned = [item for item in cleaned if item not in {"and", "or"}]
        cleaned = cleaned[-4:]
        cleaned = _canonical_topic_prefix(cleaned)
        if cleaned:
            return tuple(cleaned + [token])
        if token in {"setup", "startup", "triage", "verification"}:
            return (token,)
    return ()


def _core_tokens(values: list[str] | tuple[str, ...], ignored_tokens: set[str]) -> set[str]:
    core: set[str] = set()
    for value in values:
        for token in _tokenize(value):
            if token in STOP_WORDS or token in GENERIC_DESCRIPTOR_TOKENS or token in GENERIC_CANDIDATE_TOKENS:
                continue
            if token in ignored_tokens:
                continue
            core.add(token)
    return core


def _ordered_signal_tokens(candidate_id: str, hints: tuple[str, ...], ignored_tokens: set[str]) -> tuple[str, ...]:
    ordered: list[str] = []
    seen: set[str] = set()
    for value in (*hints, candidate_id):
        for token in _tokenize(value):
            if token in STOP_WORDS or token in GENERIC_DESCRIPTOR_TOKENS or token in ignored_tokens:
                continue
            if token in seen:
                continue
            ordered.append(token)
            seen.add(token)
    return tuple(ordered)


def _primary_domain_token(signal_tokens: tuple[str, ...]) -> str | None:
    token_set = set(signal_tokens)
    for token in DOMAIN_PRIORITY_TOKENS:
        if token in token_set:
            return token
    for token in signal_tokens:
        if token in STACK_SIGNAL_TOKENS or token in TOPIC_SUFFIX_TOKENS or token in TOPIC_BOUNDARY_TOKENS:
            continue
        return token
    return None


def _suggested_capability_ids(candidate_id: str, hints: tuple[str, ...], ignored_tokens: set[str]) -> tuple[str, ...]:
    signal_tokens = _ordered_signal_tokens(candidate_id, hints, ignored_tokens)
    token_set = set(signal_tokens)
    if "e2e" in token_set and {"auth", "authentication", "login", "keycloak"} & token_set:
        suggestions = ["auth-e2e-workflow", "auth-workflow", candidate_id]
        return tuple(dict.fromkeys(normalize_identifier(item) for item in suggestions if item))

    preferred_domain = next((token for token in DOMAIN_PRIORITY_TOKENS if token in token_set), None)
    domain = preferred_domain or _primary_domain_token(signal_tokens)
    suggestions: list[str] = []

    if preferred_domain and token_set & STACK_SIGNAL_TOKENS:
        suggestions.append(f"{domain}-local-stack-workflow")
    if preferred_domain and "compose" in token_set:
        suggestions.append(f"{domain}-compose-workflow")
    if preferred_domain and "startup" in token_set:
        suggestions.append(f"{domain}-startup-runbook")
    if preferred_domain and "workflow" in token_set:
        suggestions.append(f"{domain}-workflow")
    if token_set & STACK_SIGNAL_TOKENS:
        suggestions.append("local-stack-workflow")
    suggestions.append(candidate_id)
    return tuple(dict.fromkeys(normalize_identifier(item) for item in suggestions if item))


def _scope_metadata(
    default_capability_id: str,
    hints: tuple[str, ...],
    ignored_tokens: set[str],
    summary: str,
) -> tuple[str, tuple[str, ...], tuple[str, ...]]:
    signal_tokens = _ordered_signal_tokens(default_capability_id, hints, ignored_tokens)
    token_set = set(signal_tokens)
    scope_summary = summary
    in_scope: list[str] = []
    out_of_scope: list[str] = []

    if "e2e" in token_set and {"auth", "authentication", "login", "keycloak"} & token_set:
        scope_summary = "Auth and e2e verification workflow, including stable entrypoints, local URLs, login flow checks, and failure signals."
        in_scope.extend(
            [
                "auth and e2e test entrypoints that are stable across sessions",
                "local URLs, browser/API verification signals, and first checks when login-backed tests fail",
                "safe troubleshooting steps for auth test wiring without storing secrets",
            ]
        )
        out_of_scope.extend(
            [
                "general backend or frontend local stack orchestration unless it directly blocks auth/e2e verification",
                "durable storage of local credentials, bearer tokens, or secret values",
                "feature implementation outside the auth/e2e workflow",
            ]
        )
    elif default_capability_id.endswith("-local-stack-workflow"):
        domain = default_capability_id[: -len("-local-stack-workflow")].replace("-", " ")
        scope_summary = f"Local {domain} stack orchestration, compose entrypoints, effective ports, and startup/debug behavior."
        if "compose" in token_set or "docker" in token_set:
            in_scope.append("stack entrypoint selection across top-level and service-local compose files")
        in_scope.append("effective localhost ports, service URLs, and container-facing endpoints")
        in_scope.append(f"day-to-day local run, restart, and debug flow for the {domain} stack")
        if token_set & {"health", "healthcheck", "startup"}:
            in_scope.append("startup order, health checks, and readiness verification")
        out_of_scope.extend(
            [
                f"feature implementation inside the {domain} service once the stack is already running",
                "project-wide architecture that does not change local stack operation",
                "test design beyond what is required to bootstrap and verify the local stack",
            ]
        )
    elif default_capability_id.endswith("-compose-workflow"):
        scope_summary = "Compose-driven local workflow selection, stack wiring, and operational verification."
        in_scope.extend(
            [
                "which compose entrypoint to use for day-to-day work",
                "service wiring, overrides, and effective local host ports",
                "repeatable commands for bringing the local stack up and verifying it",
            ]
        )
        out_of_scope.extend(
            [
                "feature implementation details inside services started by the compose flow",
                "broader project conventions unrelated to the compose workflow",
            ]
        )
    else:
        scope_summary = summary
        in_scope.extend(
            [
                "reusable workflow and verification steps proven across sessions",
                "stable commands or conventions that should change future work in this topic area",
            ]
        )
        out_of_scope.extend(
            [
                "one-off task notes or ticket-specific status",
                "broader project knowledge that does not belong to this workflow",
            ]
        )

    return scope_summary, tuple(dict.fromkeys(in_scope)), tuple(dict.fromkeys(out_of_scope))


def _should_refresh_proposal(candidate_id: str, default_capability_id: str, hints: tuple[str, ...], ignored_tokens: set[str]) -> bool:
    signal_tokens = set(_ordered_signal_tokens(candidate_id, hints, ignored_tokens))
    if "e2e" in signal_tokens and {"auth", "authentication", "login", "keycloak"} & signal_tokens:
        return default_capability_id.endswith("-local-stack-workflow") or default_capability_id in {
            "auth-workflow",
            "frontend-workflow",
            candidate_id,
        }
    return False


def _remove_stale_session_candidates(governed_root: Path, keep_root: Path, session_id: str) -> None:
    candidates_root = governed_root / "candidates"
    if not candidates_root.is_dir():
        return
    for candidate_root in sorted(candidates_root.iterdir()):
        if candidate_root == keep_root:
            continue
        candidate_path = candidate_root / "candidate.toml"
        existing = _read_existing(candidate_path)
        if not existing:
            continue
        if str(existing.get("status") or "") == "activated":
            continue
        if int(existing.get("occurrences") or 0) > 1:
            continue
        source = existing.get("source") if isinstance(existing.get("source"), dict) else {}
        sessions = source.get("sessions") if isinstance(source.get("sessions"), list) else ()
        if session_id in {str(item) for item in sessions}:
            shutil.rmtree(candidate_root)


def _matching_candidate(
    governed_root: Path,
    candidate_id: str,
    hints: tuple[str, ...],
    summary: str,
    ignored_tokens: set[str],
) -> tuple[Path, dict[str, Any]] | None:
    candidates_root = governed_root / "candidates"
    if not candidates_root.is_dir():
        return None
    requested_id_tokens = _core_tokens([candidate_id], ignored_tokens)
    requested_hint_tokens = _core_tokens(list(hints), ignored_tokens)
    requested_summary_tokens = _core_tokens([summary], ignored_tokens)
    best_match: tuple[int, Path, dict[str, Any]] | None = None
    for candidate_root in sorted(candidates_root.iterdir()):
        candidate_path = candidate_root / "candidate.toml"
        existing = _read_existing(candidate_path)
        if not existing:
            continue
        existing_id = normalize_identifier(str(existing.get("id") or candidate_root.name))
        if existing_id == candidate_id:
            return candidate_root, existing
        if str(existing.get("status") or "") == "activated":
            continue
        proposal = existing.get("proposal") if isinstance(existing.get("proposal"), dict) else {}
        existing_hints = proposal.get("routing_hints") if isinstance(proposal.get("routing_hints"), list) else ()
        existing_summary = str(proposal.get("summary") or "")

        id_overlap = len(requested_id_tokens & _core_tokens([existing_id], ignored_tokens))
        hint_overlap = len(requested_hint_tokens & _core_tokens(tuple(str(item) for item in existing_hints), ignored_tokens))
        summary_overlap = len(requested_summary_tokens & _core_tokens([existing_summary], ignored_tokens))
        if id_overlap < 2 and not (hint_overlap >= 3 and (id_overlap >= 1 or summary_overlap >= 1)):
            continue
        score = (id_overlap * 3) + (hint_overlap * 2) + summary_overlap
        if best_match is None or score > best_match[0]:
            best_match = (score, candidate_root, existing)
    if best_match is None:
        return None
    return best_match[1], best_match[2]


def _candidate_for_session(governed_root: Path, session_id: str) -> tuple[Path, dict[str, Any]] | None:
    candidates_root = governed_root / "candidates"
    if not candidates_root.is_dir():
        return None
    for candidate_root in sorted(candidates_root.iterdir()):
        candidate_path = candidate_root / "candidate.toml"
        existing = _read_existing(candidate_path)
        if not existing:
            continue
        source = existing.get("source") if isinstance(existing.get("source"), dict) else {}
        sessions = source.get("sessions") if isinstance(source.get("sessions"), list) else ()
        if session_id in {str(item) for item in sessions}:
            return candidate_root, existing
    return None


def _candidate_id(user_text: str, assistant_text: str, ignored_tokens: set[str]) -> str:
    feature = _feature_name(user_text)
    if feature:
        return normalize_identifier(feature)
    topic = _topic_tokens(user_text, ignored_tokens) or _topic_tokens(f"{user_text}\n{assistant_text}", ignored_tokens)
    if topic:
        return normalize_identifier("-".join(topic))
    keywords = _keywords(f"{user_text}\n{assistant_text}", limit=5, ignored_tokens=ignored_tokens)
    if keywords:
        return normalize_identifier("-".join(keywords))
    return "project-knowledge-candidate"


def _candidate_summary(candidate_id: str, user_text: str, ignored_tokens: set[str]) -> str:
    feature = _feature_name(user_text)
    if feature:
        return f"Repeated work around {feature} may need a dedicated governed capability."
    topic = _topic_tokens(user_text, ignored_tokens)
    if topic:
        return f"Repeated work around {' '.join(topic)} may need a dedicated governed capability."
    snippet = _compact(user_text, limit=240)
    if snippet:
        return f"Repeated unmatched project work may need a dedicated governed capability: {snippet}"
    return f"Repeated unmatched project work may need a dedicated governed capability for {candidate_id}."


def _narrowed_summary(default_capability_id: str, summary: str) -> str:
    prefix = "Repeated work around "
    suffix = " may need a dedicated governed capability."
    if summary.startswith(prefix) and summary.endswith(suffix):
        topic = default_capability_id.replace("-", " ")
        return f"{prefix}{topic}{suffix}"
    return summary


def candidate_default_capability_id(data: dict[str, Any], fallback_candidate_id: str) -> str:
    proposal = data.get("proposal") if isinstance(data.get("proposal"), dict) else {}
    capability_id = proposal.get("capability_id") if isinstance(proposal, dict) else None
    if isinstance(capability_id, str) and capability_id.strip():
        return normalize_identifier(capability_id)
    suggestions = proposal.get("suggested_capability_ids") if isinstance(proposal, dict) else None
    if isinstance(suggestions, list):
        for item in suggestions:
            if isinstance(item, str) and item.strip():
                return normalize_identifier(item)
    return normalize_identifier(fallback_candidate_id)


def candidate_suggested_capability_ids(data: dict[str, Any], fallback_candidate_id: str) -> tuple[str, ...]:
    proposal = data.get("proposal") if isinstance(data.get("proposal"), dict) else {}
    suggestions = proposal.get("suggested_capability_ids") if isinstance(proposal, dict) else None
    ordered: list[str] = []
    if isinstance(suggestions, list):
        for item in suggestions:
            if isinstance(item, str) and item.strip():
                ordered.append(normalize_identifier(item))
    default_id = candidate_default_capability_id(data, fallback_candidate_id)
    ordered.append(default_id)
    ordered.append(normalize_identifier(fallback_candidate_id))
    return tuple(dict.fromkeys(item for item in ordered if item))


def _read_existing(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    try:
        return tomllib.loads(path.read_text(encoding="utf-8"))
    except tomllib.TOMLDecodeError:
        return None


def _toml_string_list(values: tuple[str, ...] | list[str]) -> str:
    return "[" + ", ".join(json.dumps(value) for value in values) + "]"


def _routing_negative_hints(capability_id: str, hints: tuple[str, ...]) -> tuple[str, ...]:
    negatives = [
        "codex-memory-review",
        "govkb install",
        "govkb apply",
        "report output",
        "cron schedule",
    ]
    tokens = set(_tokenize(capability_id))
    tokens.update(hint.lower() for hint in hints)
    if "backend" in tokens:
        negatives.extend(["auth", "login", "keycloak", "e2e", "playwright", "frontend"])
    if "frontend" in tokens:
        negatives.extend(["backend", "dotnet", "migration", "postgres", "database"])
    if {"auth", "login", "keycloak", "e2e", "playwright"} & tokens:
        negatives.extend(["migration", "database schema", "backend stack"])
    return tuple(dict.fromkeys(negatives))


def _candidate_toml(
    candidate_id: str,
    status: str,
    occurrences: int,
    created_at: str,
    updated_at: str,
    source_sessions: tuple[str, ...],
    default_capability_id: str,
    suggested_capability_ids: tuple[str, ...],
    summary: str,
    scope_summary: str,
    in_scope: tuple[str, ...],
    out_of_scope: tuple[str, ...],
    hints: tuple[str, ...],
    activated_capability_id: str | None = None,
) -> str:
    activation = ""
    if activated_capability_id:
        activation = f"""
[activation]
capability_id = "{activated_capability_id}"
activated_at = "{updated_at}"
"""
    return f"""candidate_version = 1
id = "{candidate_id}"
status = "{status}"
occurrences = {occurrences}
created_at = "{created_at}"
updated_at = "{updated_at}"

[proposal]
capability_id = "{default_capability_id}"
suggested_capability_ids = {_toml_string_list(suggested_capability_ids)}
summary = {json.dumps(summary)}
rationale = "No specialized governed capability matched repeated durable project work."
routing_hints = {_toml_string_list(hints)}

[scope]
summary = {json.dumps(scope_summary)}
in_scope = {_toml_string_list(in_scope)}
out_of_scope = {_toml_string_list(out_of_scope)}

[source]
assistant = "codex"
sessions = {_toml_string_list(source_sessions)}
{activation}"""


def _draft_contract(
    capability_id: str,
    summary: str,
    hints: tuple[str, ...],
    scope_summary: str,
    in_scope: tuple[str, ...],
    out_of_scope: tuple[str, ...],
    candidate_aliases: tuple[str, ...],
) -> str:
    name = capability_id.replace("-", " ").title()
    aliases = (f"${capability_id}", capability_id, capability_id.replace("-", " "), *candidate_aliases)
    negative_hints = _routing_negative_hints(capability_id, hints)
    scope_lines = [f"# Scope summary: {scope_summary}", "# In scope:"]
    scope_lines.extend(f"# - {item}" for item in in_scope)
    scope_lines.append("# Out of scope:")
    scope_lines.extend(f"# - {item}" for item in out_of_scope)
    return f"""contract_version = 1

{chr(10).join(scope_lines)}

[capability]
id = "{capability_id}"
name = "{name}"
governed = true
description = {json.dumps(summary)}

[routing]
aliases = {_toml_string_list(aliases)}
hints = {_toml_string_list(hints)}
negative_hints = {_toml_string_list(negative_hints)}

[memory]
enabled = true
auto_apply_min_confidence = 0.85
requires_explicit_acceptance = false

[memory.targets.main]
path = "references/long-term-memory.md"
sections = ["Working Agreement", "Stable Patterns", "Verification Notes"]
"""


def _draft_instructions(
    capability_id: str,
    summary: str,
    scope_summary: str,
    in_scope: tuple[str, ...],
    out_of_scope: tuple[str, ...],
) -> str:
    title = capability_id.replace("-", " ").title()
    in_scope_lines = "\n".join(f"- {item}" for item in in_scope) or "- TODO: narrow in-scope behavior.\n"
    out_scope_lines = "\n".join(f"- {item}" for item in out_of_scope) or "- TODO: narrow out-of-scope behavior.\n"
    return f"""# {title}

Use this governed capability when the task matches the candidate evidence.

## Intent

{summary}

## Scope Summary

{scope_summary}

## In Scope

{in_scope_lines}

## Out Of Scope

{out_scope_lines}

## Load References First

- Read `references/long-term-memory.md` before acting.

## Workflow

- Ground the task in current repo files and existing project knowledge.
- Preserve evidence for durable lessons that should improve future work.
- Update long-term memory only with stable, reusable project guidance.
"""


def _memory_text(capability_id: str, summary: str, scope_summary: str) -> str:
    title = capability_id.replace("-", " ").title()
    return f"""# {title}

Candidate summary: {summary}

Scope summary: {scope_summary}

## Working Agreement

- Use this section for stable capability-specific operating rules after activation.

## Stable Patterns

- Use this section for recurring project patterns observed across sessions.

## Verification Notes

- Use this section for durable validation commands, evidence expectations, and safety checks.
"""


def stage_candidate_from_session(project_root: Path, session_file: Path) -> CandidateStageResult:
    """Create or update a governed capability candidate from a Codex session."""
    resolved_root = resolve_project_root(project_root)
    governed_root = resolved_root / ".governed"
    if not governed_root.is_dir():
        raise FileNotFoundError(f"missing governed root: {governed_root}")

    session_id, timestamp, user_text, assistant_text = _session_text(session_file)
    ignored_tokens = _ignored_tokens(resolved_root)
    candidate_id = _candidate_id(user_text, assistant_text, ignored_tokens)
    proposed_candidate_id = candidate_id
    summary = _candidate_summary(candidate_id, user_text, ignored_tokens)
    hints = _keywords(f"{user_text}\n{assistant_text}", limit=10, ignored_tokens=ignored_tokens) or (
        candidate_id.replace("-", " "),
    )
    candidate_root = governed_root / "candidates" / candidate_id
    candidate_path = candidate_root / "candidate.toml"
    existing = _read_existing(candidate_path)
    if existing is None:
        session_match = _candidate_for_session(governed_root, session_id)
        if session_match is not None:
            candidate_root, existing = session_match
            candidate_id = normalize_identifier(str(existing.get("id") or candidate_root.name))
            source = existing.get("source") if isinstance(existing.get("source"), dict) else {}
            matched_sessions = source.get("sessions") if isinstance(source.get("sessions"), list) else ()
            matched_occurrences = int(existing.get("occurrences") or 0)
            matched_status = str(existing.get("status") or "")
            rekey_target = governed_root / "candidates" / proposed_candidate_id
            if (
                proposed_candidate_id != candidate_id
                and matched_status != "activated"
                and matched_occurrences <= 1
                and session_id in {str(item) for item in matched_sessions}
            ):
                if rekey_target.exists():
                    merged_existing = _read_existing(rekey_target / "candidate.toml")
                    if merged_existing is not None:
                        shutil.rmtree(candidate_root)
                        candidate_root = rekey_target
                        candidate_id = proposed_candidate_id
                        existing = merged_existing
                else:
                    candidate_root.rename(rekey_target)
                    candidate_root = rekey_target
                    candidate_id = proposed_candidate_id
            candidate_path = candidate_root / "candidate.toml"
    if existing is None:
        matched = _matching_candidate(governed_root, candidate_id, hints, summary, ignored_tokens)
        if matched is not None:
            candidate_root, existing = matched
            candidate_id = normalize_identifier(str(existing.get("id") or candidate_root.name))
            source = existing.get("source") if isinstance(existing.get("source"), dict) else {}
            matched_sessions = source.get("sessions") if isinstance(source.get("sessions"), list) else ()
            matched_occurrences = int(existing.get("occurrences") or 0)
            matched_status = str(existing.get("status") or "")
            rekey_target = governed_root / "candidates" / proposed_candidate_id
            if (
                proposed_candidate_id != candidate_id
                and matched_status != "activated"
                and matched_occurrences <= 1
                and session_id in {str(item) for item in matched_sessions}
            ):
                if rekey_target.exists():
                    merged_existing = _read_existing(rekey_target / "candidate.toml")
                    if merged_existing is not None:
                        shutil.rmtree(candidate_root)
                        candidate_root = rekey_target
                        candidate_id = proposed_candidate_id
                        existing = merged_existing
                else:
                    candidate_root.rename(rekey_target)
                    candidate_root = rekey_target
                    candidate_id = proposed_candidate_id
            candidate_path = candidate_root / "candidate.toml"
    now = iso_utc_now()
    created_at = now
    source_sessions: list[str] = []
    occurrences = 0
    if existing:
        created_at = str(existing.get("created_at") or created_at)
        occurrences = int(existing.get("occurrences") or 0)
        source = existing.get("source")
        if isinstance(source, dict):
            sessions = source.get("sessions")
            if isinstance(sessions, list):
                source_sessions = [str(item) for item in sessions]
    created = not candidate_path.exists()
    already_seen = session_id in source_sessions
    if not already_seen:
        source_sessions.append(session_id)
        occurrences += 1
    existing_status = str(existing.get("status") or "") if existing else ""
    status = "activated" if existing_status == "activated" else "ready-for-review" if occurrences >= 2 else "collecting"
    if existing:
        proposal = existing.get("proposal") if isinstance(existing.get("proposal"), dict) else {}
        legacy_suggestions = proposal.get("suggested_capability_ids") if isinstance(proposal, dict) else None
        existing_default_capability_id = candidate_default_capability_id(existing, candidate_id)
        refresh_proposal = _should_refresh_proposal(candidate_id, existing_default_capability_id, hints, ignored_tokens)
        if (
            not isinstance(legacy_suggestions, list)
            or not any(isinstance(item, str) and item.strip() for item in legacy_suggestions)
            or refresh_proposal
        ):
            suggested_capability_ids = _suggested_capability_ids(candidate_id, hints, ignored_tokens)
            default_capability_id = suggested_capability_ids[0]
        else:
            default_capability_id = existing_default_capability_id
            suggested_capability_ids = candidate_suggested_capability_ids(existing, candidate_id)
        existing_summary = proposal.get("summary") if isinstance(proposal, dict) else None
        if isinstance(existing_summary, str) and existing_summary.strip():
            summary = existing_summary
        summary = _narrowed_summary(default_capability_id, summary)
        scope = existing.get("scope") if isinstance(existing.get("scope"), dict) else {}
        existing_scope_summary = scope.get("summary") if isinstance(scope, dict) else None
        in_scope = tuple(str(item) for item in scope.get("in_scope", ()) if isinstance(item, str)) if isinstance(scope, dict) else ()
        out_of_scope = tuple(str(item) for item in scope.get("out_of_scope", ()) if isinstance(item, str)) if isinstance(scope, dict) else ()
        if refresh_proposal or not isinstance(existing_scope_summary, str) or not existing_scope_summary.strip() or not in_scope or not out_of_scope:
            computed_scope_summary, computed_in_scope, computed_out_of_scope = _scope_metadata(
                default_capability_id,
                hints,
                ignored_tokens,
                summary,
            )
            scope_summary = computed_scope_summary
            in_scope = computed_in_scope if refresh_proposal else in_scope or computed_in_scope
            out_of_scope = computed_out_of_scope if refresh_proposal else out_of_scope or computed_out_of_scope
        else:
            scope_summary = existing_scope_summary
    else:
        suggested_capability_ids = _suggested_capability_ids(candidate_id, hints, ignored_tokens)
        default_capability_id = suggested_capability_ids[0]
        summary = _narrowed_summary(default_capability_id, summary)
        scope_summary, in_scope, out_of_scope = _scope_metadata(default_capability_id, hints, ignored_tokens, summary)

    _remove_stale_session_candidates(governed_root, candidate_root, session_id)
    candidate_root.mkdir(parents=True, exist_ok=True)
    (candidate_root / "references").mkdir(parents=True, exist_ok=True)
    candidate_path.write_text(
        _candidate_toml(
            candidate_id=candidate_id,
            status=status,
            occurrences=occurrences,
            created_at=created_at,
            updated_at=now,
            source_sessions=tuple(source_sessions),
            default_capability_id=default_capability_id,
            suggested_capability_ids=suggested_capability_ids,
            summary=summary,
            scope_summary=scope_summary,
            in_scope=in_scope,
            out_of_scope=out_of_scope,
            hints=tuple(hints),
        ),
        encoding="utf-8",
    )
    evidence_path = candidate_root / "evidence.md"
    evidence_header = f"# Candidate Evidence: {candidate_id}\n\n"
    if not evidence_path.exists():
        evidence_path.write_text(evidence_header, encoding="utf-8")
    if not already_seen:
        with evidence_path.open("a", encoding="utf-8") as fh:
            fh.write(f"## {session_id}\n\n")
            if timestamp:
                fh.write(f"- Timestamp: `{timestamp}`\n")
            fh.write(f"- Session file: `{session_file}`\n")
            fh.write(f"- Summary: {summary}\n\n")
            fh.write("### User Signal\n\n")
            fh.write(_compact(user_text, limit=1200) + "\n\n")
            if assistant_text.strip():
                fh.write("### Assistant Signal\n\n")
                fh.write(_compact(assistant_text, limit=1200) + "\n\n")

    candidate_aliases = tuple(
        dict.fromkeys(
            value
            for value in (
                f"${candidate_id}",
                candidate_id,
                candidate_id.replace("-", " "),
            )
            if normalize_identifier(candidate_id) != normalize_identifier(default_capability_id)
        )
    )
    (candidate_root / "draft-capability.contract.toml").write_text(
        _draft_contract(default_capability_id, summary, tuple(hints), scope_summary, in_scope, out_of_scope, candidate_aliases),
        encoding="utf-8",
    )
    (candidate_root / "draft-instructions.md").write_text(
        _draft_instructions(default_capability_id, summary, scope_summary, in_scope, out_of_scope),
        encoding="utf-8",
    )
    (candidate_root / "draft-initialize-kb.md").write_text(
        initialize_kb_prompt_text(
            capability_id=default_capability_id,
            capability_name=default_capability_id.replace("-", " ").title(),
            summary=summary,
            scope_summary=scope_summary,
            candidate_id=candidate_id,
        ),
        encoding="utf-8",
    )
    (candidate_root / "references" / "long-term-memory.md").write_text(
        _memory_text(default_capability_id, summary, scope_summary),
        encoding="utf-8",
    )
    return CandidateStageResult(
        candidate_id=candidate_id,
        candidate_root=candidate_root,
        status=status,
        occurrences=occurrences,
        created=created,
        source_session=session_id,
        default_capability_id=default_capability_id,
    )


def list_candidates(project_root: Path) -> tuple[Path, ...]:
    """List candidate directories for a governed project."""
    resolved_root = resolve_project_root(project_root)
    candidates_root = resolved_root / ".governed" / "candidates"
    if not candidates_root.is_dir():
        return ()
    return tuple(path for path in sorted(candidates_root.iterdir()) if (path / "candidate.toml").is_file())


def load_candidate(project_root: Path, candidate_id: str) -> tuple[Path, dict[str, Any]]:
    """Load a candidate TOML document."""
    resolved_root = resolve_project_root(project_root)
    candidate_root = resolved_root / ".governed" / "candidates" / normalize_identifier(candidate_id)
    candidate_path = candidate_root / "candidate.toml"
    if not candidate_path.is_file():
        raise FileNotFoundError(f"candidate not found: {candidate_root}")
    return candidate_root, tomllib.loads(candidate_path.read_text(encoding="utf-8"))


def mark_candidate_activated(project_root: Path, candidate_id: str, capability_id: str) -> Path:
    """Mark a candidate as activated by a governed capability."""
    candidate_root, data = load_candidate(project_root, candidate_id)
    proposal = data.get("proposal") if isinstance(data.get("proposal"), dict) else {}
    source = data.get("source") if isinstance(data.get("source"), dict) else {}
    sessions = source.get("sessions") if isinstance(source, dict) else ()
    hints = proposal.get("routing_hints") if isinstance(proposal, dict) else ()
    summary = proposal.get("summary") if isinstance(proposal, dict) else None
    suggested = proposal.get("suggested_capability_ids") if isinstance(proposal, dict) else ()
    scope = data.get("scope") if isinstance(data.get("scope"), dict) else {}
    candidate_path = candidate_root / "candidate.toml"
    candidate_path.write_text(
        _candidate_toml(
            candidate_id=normalize_identifier(str(data.get("id") or candidate_id)),
            status="activated",
            occurrences=int(data.get("occurrences") or 0),
            created_at=str(data.get("created_at") or iso_utc_now()),
            updated_at=iso_utc_now(),
            source_sessions=tuple(str(item) for item in sessions) if isinstance(sessions, list) else (),
            default_capability_id=capability_id,
            suggested_capability_ids=tuple(str(item) for item in suggested) if isinstance(suggested, list) else (capability_id,),
            summary=str(summary or "Candidate activated as a governed capability."),
            scope_summary=str(scope.get("summary") or summary or "Candidate activated as a governed capability."),
            in_scope=tuple(str(item) for item in scope.get("in_scope", ())) if isinstance(scope.get("in_scope"), list) else (),
            out_of_scope=tuple(str(item) for item in scope.get("out_of_scope", ())) if isinstance(scope.get("out_of_scope"), list) else (),
            hints=tuple(str(item) for item in hints) if isinstance(hints, list) else (),
            activated_capability_id=capability_id,
        ),
        encoding="utf-8",
    )
    return candidate_path
