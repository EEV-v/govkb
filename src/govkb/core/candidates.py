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

BACKEND_ROUTING_TOKENS = {"backend", "api", "dotnet"}
FRONTEND_ROUTING_TOKENS = {"frontend", "web", "ui"}
AUTH_ROUTING_TOKENS = {"auth", "login", "keycloak", "e2e", "playwright"}
COMPATIBLE_DOMAIN_GROUPS = (frozenset({"api", "backend"}),)

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

PATH_CONTEXT_TOKENS = {
    "adapters",
    "app",
    "apps",
    "capabilities",
    "candidate",
    "candidates",
    "config",
    "doc",
    "docs",
    "governed",
    "knowledge",
    "lib",
    "packages",
    "reference",
    "references",
    "script",
    "scripts",
    "service",
    "services",
    "source",
    "src",
    "test",
    "tests",
}

PATH_SUFFIX_TOKENS = {
    "cs",
    "csproj",
    "json",
    "md",
    "py",
    "sln",
    "toml",
    "ts",
    "tsx",
    "yaml",
    "yml",
}

COMMAND_PREFIXES = (
    "cargo ",
    "dotnet ",
    "go ",
    "just ",
    "make ",
    "npm ",
    "pnpm ",
    "python ",
    "python3 ",
    "pytest",
    "yarn ",
)

REPO_PATH_PATTERN = re.compile(
    r"(?:`)?("
    r"[A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.-]+)+"
    r"|[A-Za-z0-9_.-]+\.(?:csproj|json|md|py|sln|toml|tsx?|ya?ml)"
    r")(?:`)?"
)

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


def _repo_paths_from_text(text: str, *, limit: int = 12) -> tuple[str, ...]:
    """Extract portable repo-relative paths from mixed-language session text."""
    ordered: list[str] = []
    for match in REPO_PATH_PATTERN.finditer(text):
        start = match.start(1)
        if start > 0 and text[start - 1] in {"/", "~"}:
            continue
        normalized = _normalize_repo_relative_path(match.group(1))
        if not normalized or normalized in ordered:
            continue
        ordered.append(normalized)
        if len(ordered) >= limit:
            break
    return tuple(ordered)


def _path_topic_tokens(text: str, ignored_tokens: set[str]) -> tuple[str, ...]:
    """Derive a topic from observed repo artifacts before prompt wording."""
    fallback_topic: tuple[str, ...] = ()
    for path_value in _repo_paths_from_text(text):
        path = Path(path_value)
        tokens: list[str] = []
        for part in path.parts:
            if part in {".", ""}:
                continue
            stem = Path(part).stem
            for token in _tokenize(stem.replace(".", " ").replace("_", " ").replace("-", " ")):
                if token in ignored_tokens or token in PATH_CONTEXT_TOKENS or token in PATH_SUFFIX_TOKENS:
                    continue
                if token in STOP_WORDS or token in GENERIC_DESCRIPTOR_TOKENS:
                    continue
                if token not in tokens:
                    tokens.append(token)
        if len(tokens) >= 2:
            topic_core = [token for token in tokens if token not in TOPIC_SUFFIX_TOKENS]
            if len(topic_core) < 2:
                fallback_topic = fallback_topic or tuple(tokens[:3])
                continue
            topic = topic_core[:3]
            if topic[-1] not in TOPIC_SUFFIX_TOKENS:
                topic.append("workflow")
            return tuple(topic)
    if fallback_topic:
        topic = list(fallback_topic)
        if topic[-1] not in TOPIC_SUFFIX_TOKENS:
            topic.append("workflow")
        return tuple(topic)
    return ()


def _path_hints(text: str, ignored_tokens: set[str], *, limit: int = 10) -> tuple[str, ...]:
    hints: list[str] = []
    for path_value in _repo_paths_from_text(text):
        for token in _path_topic_tokens(path_value, ignored_tokens) or _tokenize(path_value):
            if token in ignored_tokens or token in PATH_CONTEXT_TOKENS or token in PATH_SUFFIX_TOKENS:
                continue
            if token in STOP_WORDS or token in GENERIC_DESCRIPTOR_TOKENS:
                continue
            if token not in hints:
                hints.append(token)
                if len(hints) >= limit:
                    return tuple(hints)
    return tuple(hints)


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


def _canonical_routing_hints(capability_id: str, hints: tuple[str, ...], ignored_tokens: set[str]) -> tuple[str, ...]:
    signal_tokens = _ordered_signal_tokens(capability_id, hints, ignored_tokens)
    token_set = set(signal_tokens)
    ordered: list[str] = []

    def add(*values: str) -> None:
        for value in values:
            normalized = value.strip().lower()
            if not normalized or normalized in ordered:
                continue
            ordered.append(normalized)

    if capability_id == "auth-e2e-workflow" or ("e2e" in token_set and AUTH_ROUTING_TOKENS & token_set):
        add("auth", "e2e", "login", "keycloak", "playwright", "frontend", "compose", "ports", "verification")
        return tuple(ordered)

    if capability_id.endswith("-local-stack-workflow"):
        domain = capability_id[: -len("-local-stack-workflow")].replace("-", " ").strip()
        if domain:
            add(*_tokenize(domain))
        add("compose", "docker", "ports", "stack", "startup", "workflow")
        if "dotnet" in token_set:
            add("dotnet")
        if "postgres" in token_set:
            add("postgres")
        return tuple(ordered)

    if capability_id.endswith("-compose-workflow"):
        add("compose", "docker", "ports", "stack", "startup", "workflow")
        return tuple(ordered)

    preferred_domain = next((token for token in DOMAIN_PRIORITY_TOKENS if token in token_set), None)
    if preferred_domain:
        add(preferred_domain)
    for token in signal_tokens:
        if token in TOPIC_BOUNDARY_TOKENS or token in TOPIC_SUFFIX_TOKENS:
            continue
        add(token)
        if len(ordered) >= 8:
            break
    return tuple(ordered) or hints


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
        topic = _repeated_work_topic(summary)
        scope_summary = f"Reusable {topic}." if topic else summary
        if topic:
            in_scope.append(f"repeatable {topic} steps and evidence observed across sessions")
            in_scope.append(f"{topic} commands, artifacts, and conventions that should be reused in future work")
        else:
            in_scope.append("reusable workflow and verification steps proven across sessions")
            in_scope.append("stable commands or conventions that should change future work in this topic area")
        out_of_scope.extend(
            [
                "one-off task notes or ticket-specific status",
                "broader project knowledge that does not belong to this workflow",
            ]
        )

    return scope_summary, tuple(dict.fromkeys(in_scope)), tuple(dict.fromkeys(out_of_scope))


def _repeated_work_topic(summary: str) -> str | None:
    prefix = "Repeated work around "
    suffix = " may need a dedicated governed capability."
    if not summary.startswith(prefix) or not summary.endswith(suffix):
        return None
    topic = summary[len(prefix) : -len(suffix)].strip()
    return topic or None


def _should_refresh_proposal(candidate_id: str, default_capability_id: str, hints: tuple[str, ...], ignored_tokens: set[str]) -> bool:
    signal_tokens = set(_ordered_signal_tokens(candidate_id, hints, ignored_tokens))
    if "e2e" in signal_tokens and {"auth", "authentication", "login", "keycloak"} & signal_tokens:
        return default_capability_id.endswith("-local-stack-workflow") or default_capability_id in {
            "auth-workflow",
            "frontend-workflow",
            candidate_id,
        }
    return False


def _domains_conflict(
    candidate_id: str,
    hints: tuple[str, ...],
    existing_id: str,
    existing_hints: tuple[str, ...],
    ignored_tokens: set[str],
) -> bool:
    requested_tokens = set(_ordered_signal_tokens(candidate_id, hints, ignored_tokens))
    existing_tokens = set(_ordered_signal_tokens(existing_id, existing_hints, ignored_tokens))
    requested_auth = bool(AUTH_ROUTING_TOKENS & requested_tokens)
    existing_auth = bool(AUTH_ROUTING_TOKENS & existing_tokens)
    if requested_auth != existing_auth:
        return True

    requested_domain = next((token for token in DOMAIN_PRIORITY_TOKENS if token in requested_tokens), None)
    existing_domain = next((token for token in DOMAIN_PRIORITY_TOKENS if token in existing_tokens), None)
    if not requested_domain or not existing_domain or requested_domain == existing_domain:
        return False
    if frozenset({requested_domain, existing_domain}) in COMPATIBLE_DOMAIN_GROUPS:
        return False
    return True


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
        existing_hint_values = tuple(str(item) for item in existing_hints)

        if _domains_conflict(candidate_id, hints, existing_id, existing_hint_values, ignored_tokens):
            continue

        id_overlap = len(requested_id_tokens & _core_tokens([existing_id], ignored_tokens))
        hint_overlap = len(requested_hint_tokens & _core_tokens(existing_hint_values, ignored_tokens))
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
    path_topic = _path_topic_tokens(f"{user_text}\n{assistant_text}", ignored_tokens)
    if path_topic:
        return normalize_identifier("-".join(path_topic))
    topic = _topic_tokens(user_text, ignored_tokens) or _topic_tokens(f"{user_text}\n{assistant_text}", ignored_tokens)
    if topic:
        return normalize_identifier("-".join(topic))
    keywords = _keywords(f"{user_text}\n{assistant_text}", limit=5, ignored_tokens=ignored_tokens)
    if keywords:
        return normalize_identifier("-".join(keywords))
    return "project-knowledge-candidate"


def _candidate_summary(candidate_id: str, user_text: str, assistant_text: str, ignored_tokens: set[str]) -> str:
    feature = _feature_name(user_text)
    if feature:
        return f"Repeated work around {feature} may need a dedicated governed capability."
    path_topic = _path_topic_tokens(f"{user_text}\n{assistant_text}", ignored_tokens)
    if path_topic:
        return f"Repeated work around {' '.join(path_topic)} may need a dedicated governed capability."
    topic = _topic_tokens(user_text, ignored_tokens)
    if topic:
        return f"Repeated work around {' '.join(topic)} may need a dedicated governed capability."
    snippet = _compact(user_text, limit=240)
    if snippet:
        return f"Repeated unmatched project work may need a dedicated governed capability: {snippet}"
    return f"Repeated unmatched project work may need a dedicated governed capability for {candidate_id}."


def _semantic_seed_text(seed: dict[str, Any] | None, key: str) -> str | None:
    if not isinstance(seed, dict):
        return None
    value = seed.get(key)
    if not isinstance(value, str):
        return None
    compact = re.sub(r"\s+", " ", value.strip())
    return compact or None


def _semantic_seed_string_list(seed: dict[str, Any] | None, key: str, *, limit: int = 12) -> tuple[str, ...]:
    if not isinstance(seed, dict):
        return ()
    value = seed.get(key)
    if not isinstance(value, list):
        return ()
    ordered: list[str] = []
    for item in value:
        if not isinstance(item, str):
            continue
        compact = re.sub(r"\s+", " ", item.strip())
        if not compact or compact in ordered:
            continue
        ordered.append(compact)
        if len(ordered) >= limit:
            break
    return tuple(ordered)


def _semantic_seed_identifier(seed: dict[str, Any] | None, key: str) -> str | None:
    value = _semantic_seed_text(seed, key)
    if not value:
        return None
    normalized = normalize_identifier(value)
    return normalized or None


def _semantic_scope_metadata(seed: dict[str, Any] | None) -> tuple[str | None, tuple[str, ...], tuple[str, ...]]:
    return (
        _semantic_seed_text(seed, "scope_summary"),
        _semantic_seed_string_list(seed, "in_scope", limit=8),
        _semantic_seed_string_list(seed, "out_of_scope", limit=8),
    )


def _normalize_repo_relative_path(path: str) -> str | None:
    normalized = path.replace("\\", "/").strip().strip("`'\"")
    normalized = normalized.rstrip(".,;:)]}")
    if not normalized or normalized.startswith("/"):
        return None
    normalized = re.sub(r"^\./+", "", normalized)
    if normalized.startswith("../") or "/../" in normalized or normalized == "..":
        return None
    if normalized.startswith(".codex/"):
        return None
    return normalized or None


def _semantic_fact_rows(
    seed: dict[str, Any] | None,
    *,
    source_sessions: tuple[str, ...],
) -> tuple[dict[str, object], ...]:
    if not isinstance(seed, dict):
        return ()
    value = seed.get("facts")
    if not isinstance(value, list):
        return ()
    rows: list[dict[str, object]] = []
    seen: set[tuple[str, str]] = set()
    for index, item in enumerate(value, start=1):
        if not isinstance(item, dict):
            continue
        section = _semantic_seed_text(item, "section")
        fact = _semantic_seed_text(item, "fact")
        if not section or not fact:
            continue
        key = (section, fact)
        if key in seen:
            continue
        seen.add(key)
        confidence_value = item.get("confidence")
        if isinstance(confidence_value, (int, float)) and not isinstance(confidence_value, bool):
            confidence = max(0.0, min(float(confidence_value), 1.0))
        else:
            confidence = 0.74
        repo_paths = tuple(
            normalized
            for normalized in (
                _normalize_repo_relative_path(str(path_value))
                for path_value in (item.get("repo_paths") if isinstance(item.get("repo_paths"), list) else [])
            )
            if normalized
        )
        grouping_key = _semantic_seed_text(item, "grouping_key") or f"semantic-fact-{index}"
        rows.append(
            {
                "grouping_key": grouping_key,
                "section": section,
                "fact": fact,
                "confidence": confidence,
                "provenance_sessions": list(source_sessions),
                "repo_paths": list(repo_paths),
            }
        )
    return tuple(rows)


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
    has_backend = bool(BACKEND_ROUTING_TOKENS & tokens)
    has_frontend = bool(FRONTEND_ROUTING_TOKENS & tokens)
    has_auth = bool(AUTH_ROUTING_TOKENS & tokens)
    if has_backend and not has_frontend and not has_auth:
        negatives.extend(["auth", "login", "keycloak", "e2e", "playwright", "frontend"])
    if has_frontend and not has_backend and not has_auth:
        negatives.extend(["backend", "dotnet", "migration", "postgres", "database"])
    if has_auth:
        negatives.extend(["migration", "database schema", "backend stack"])
    return tuple(dict.fromkeys(negatives))


def _workflow_sections_for_capability(capability_id: str) -> tuple[str, ...]:
    if capability_id.endswith("project-knowledge-steward"):
        return (
            "Project Working Agreement",
            "Stable Workflows",
            "Commands And Verification",
            "Repo Conventions",
            "Code And Docs Map",
            "Authority Rules",
            "Candidate Skill Signals",
        )
    return (
        "Working Agreement",
        "Stable Workflows",
        "Commands And Verification",
        "Code And Docs Map",
        "Authority Rules",
    )


def _bootstrap_profile_for_capability(capability_id: str) -> str:
    if capability_id.endswith("project-knowledge-steward"):
        return "steward"
    return "workflow"


def _bootstrap_seed_paths(capability_id: str, hints: tuple[str, ...]) -> tuple[str, ...]:
    tokens = set(_tokenize(capability_id))
    tokens.update(_tokenize(" ".join(hints)))
    seed_paths = ["README.md", "docs"]
    if {"backend", "api", "dotnet"} & tokens:
        seed_paths.extend(["backend", "backend-dotnet", "src", "tests"])
    if {"frontend", "web", "ui"} & tokens:
        seed_paths.extend(["frontend", "web", "app", "src", "tests"])
    if {"auth", "login", "keycloak", "e2e", "playwright"} & tokens:
        seed_paths.extend(["auth", "tests", "e2e", "playwright"])
    if {"compose", "docker", "stack", "startup"} & tokens:
        seed_paths.extend(["docker-compose.yml", "docker-compose.yaml", "compose.yml", "compose.yaml", "scripts"])
    if capability_id.endswith("project-knowledge-steward"):
        seed_paths.extend(["src", "tests"])
    return tuple(dict.fromkeys(seed_paths))


def _bootstrap_authority_paths(capability_id: str, hints: tuple[str, ...]) -> tuple[str, ...]:
    tokens = set(_tokenize(capability_id))
    tokens.update(_tokenize(" ".join(hints)))
    paths = ["README.md"]
    if {"compose", "docker", "stack", "startup"} & tokens:
        paths.extend(["docker-compose.yml", "docker-compose.yaml", "compose.yml", "compose.yaml"])
    return tuple(dict.fromkeys(paths))


def _kb_health_block(capability_id: str) -> tuple[bool, bool, tuple[str, ...]]:
    if capability_id.endswith("project-knowledge-steward"):
        return False, True, (
            "Project Working Agreement",
            "Stable Workflows",
            "Code And Docs Map",
            "Candidate Skill Signals",
        )
    return True, True, (
        "Working Agreement",
        "Stable Workflows",
        "Commands And Verification",
        "Code And Docs Map",
    )


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
    sections = _workflow_sections_for_capability(capability_id)
    bootstrap_profile = _bootstrap_profile_for_capability(capability_id)
    seed_paths = _bootstrap_seed_paths(capability_id, hints)
    authority_paths = _bootstrap_authority_paths(capability_id, hints)
    requires_verification_commands, requires_repo_map, required_sections = _kb_health_block(capability_id)
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
sections = {_toml_string_list(sections)}

[bootstrap]
profile = "{bootstrap_profile}"
repo_roots = ["."]
authority_paths = {_toml_string_list(authority_paths)}
seed_paths = {_toml_string_list(seed_paths)}

[kb_health]
requires_verification_commands = {'true' if requires_verification_commands else 'false'}
requires_repo_map = {'true' if requires_repo_map else 'false'}
required_sections = {_toml_string_list(required_sections)}
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

## Stable Workflows

- Use this section for recurring project workflow patterns observed across sessions.

## Commands And Verification

- Use this section for durable validation commands, evidence expectations, and safety checks.

## Code And Docs Map

- Use this section for durable repo-relative code, test, and docs locations.

## Authority Rules

- Use this section for durable authority rules when one governed source should win.
"""


def _sentence_case(text: str) -> str:
    text = re.sub(r"\s+", " ", text.strip())
    if not text:
        return text
    return text[0].upper() + text[1:]


def _fact_text_for_scope(scope_summary: str) -> str:
    summary = re.sub(r"\s+", " ", scope_summary.strip()).rstrip(".")
    if not summary:
        return "Focus this capability on stable, reusable project workflow knowledge."
    lowered = summary[0].lower() + summary[1:]
    return f"Focus this capability on {lowered}."


def _fact_topic(scope_summary: str) -> str:
    summary = re.sub(r"\s+", " ", scope_summary.strip()).rstrip(".")
    if not summary:
        return "capability"
    lowered = summary[0].lower() + summary[1:]
    if lowered.startswith("reusable "):
        lowered = lowered[len("reusable ") :].strip()
    topic = lowered.split(",", 1)[0].strip()
    if not topic or len(topic) > 80:
        return "capability"
    return topic


def _repo_artifact_fact(path_value: str, fact_topic: str) -> str:
    lowered = path_value.lower()
    topic = fact_topic if fact_topic != "capability" else "capability"
    if lowered.startswith("docs/") or lowered.endswith(".md"):
        return f"Use `{path_value}` as durable {topic} documentation."
    if "test" in lowered or lowered.endswith((".csproj", ".spec.ts", ".test.ts", ".py")):
        return f"Use `{path_value}` as a durable {topic} test artifact."
    return f"Use `{path_value}` as a durable {topic} repo artifact."


def _verification_command_fact(command: str, fact_topic: str) -> str:
    topic = fact_topic if fact_topic != "capability" else "capability"
    return f"Use `{command}` as the {topic} verification command."


def _generic_scope_item(item: str, fact_topic: str) -> bool:
    lowered = item.lower().strip()
    topic = fact_topic.lower()
    return (
        lowered.startswith(f"stable {topic}")
        or lowered.startswith(f"repeatable {topic}")
        or lowered.startswith(f"{topic} commands, artifacts")
        or lowered.startswith("stable commands or conventions")
    )


def _observed_workflow_row(
    *,
    observed_rows: tuple[dict[str, object], ...],
    fact_topic: str,
    source_sessions: tuple[str, ...],
) -> dict[str, object] | None:
    has_repo_artifact = any(row.get("section") == "Code And Docs Map" for row in observed_rows)
    has_verification = any(row.get("section") == "Commands And Verification" for row in observed_rows)
    if not has_repo_artifact or not has_verification:
        return None
    topic = fact_topic if fact_topic != "capability" else "the capability"
    return {
        "grouping_key": "observed-workflow",
        "section": "Stable Workflows",
        "fact": (
            f"For {topic}, update durable documentation and run the verification command "
            "before treating the workflow as complete."
        ),
        "confidence": 0.78,
        "provenance_sessions": list(source_sessions),
        "repo_paths": [],
    }


def _fact_section(item: str) -> str:
    lowered = item.lower()
    if any(token in lowered for token in ("verify", "verification", "health", "readiness", "check", "checks", "signal", "signals")):
        return "Commands And Verification"
    return "Stable Workflows"


def _command_facts_from_text(text: str, *, limit: int = 4) -> tuple[str, ...]:
    commands: list[str] = []
    for match in re.finditer(r"`([^`\n]+)`", text):
        command = _redact(re.sub(r"\s+", " ", match.group(1).strip()))
        if not command:
            continue
        if not command.lower().startswith(COMMAND_PREFIXES):
            continue
        if command not in commands:
            commands.append(command)
            if len(commands) >= limit:
                break
    return tuple(commands)


def _observed_fact_rows(
    *,
    session_text: str,
    source_sessions: tuple[str, ...],
    fact_topic: str,
) -> tuple[dict[str, object], ...]:
    rows: list[dict[str, object]] = []
    for index, path_value in enumerate(_repo_paths_from_text(session_text, limit=6), start=1):
        rows.append(
            {
                "grouping_key": f"repo-artifact-{index}",
                "section": "Code And Docs Map",
                "fact": _repo_artifact_fact(path_value, fact_topic),
                "confidence": 0.74,
                "provenance_sessions": list(source_sessions),
                "repo_paths": [path_value],
            }
        )
    for index, command in enumerate(_command_facts_from_text(session_text), start=1):
        rows.append(
            {
                "grouping_key": f"verification-command-{index}",
                "section": "Commands And Verification",
                "fact": _verification_command_fact(command, fact_topic),
                "confidence": 0.76,
                "provenance_sessions": list(source_sessions),
                "repo_paths": list(_repo_paths_from_text(command, limit=4)),
            }
        )
    return tuple(rows)


def _candidate_fact_rows(
    *,
    scope_summary: str,
    in_scope: tuple[str, ...],
    source_sessions: tuple[str, ...],
    session_text: str = "",
) -> tuple[dict[str, object], ...]:
    rows: list[dict[str, object]] = []
    fact_topic = _fact_topic(scope_summary)
    observed_rows = _observed_fact_rows(
        session_text=session_text,
        source_sessions=source_sessions,
        fact_topic=fact_topic,
    )
    rows.append(
        {
            "grouping_key": "scope-summary",
            "section": "Working Agreement",
            "fact": _fact_text_for_scope(scope_summary),
            "confidence": 0.78,
            "provenance_sessions": list(source_sessions),
        }
    )
    seen_facts = {str(rows[0]["fact"])}
    observed_workflow = _observed_workflow_row(
        observed_rows=observed_rows,
        fact_topic=fact_topic,
        source_sessions=source_sessions,
    )
    if observed_workflow is not None:
        rows.append(observed_workflow)
        seen_facts.add(str(observed_workflow["fact"]))
    for index, item in enumerate(in_scope, start=1):
        if observed_rows and _generic_scope_item(item, fact_topic):
            continue
        fact = _sentence_case(item).rstrip(".") + "."
        if fact in seen_facts:
            continue
        seen_facts.add(fact)
        rows.append(
            {
                "grouping_key": f"in-scope-{index}",
                "section": _fact_section(item),
                "fact": fact,
                "confidence": 0.72 if _fact_section(item) == "Stable Patterns" else 0.74,
                "provenance_sessions": list(source_sessions),
                "repo_paths": [],
            }
        )
    for row in observed_rows:
        fact = str(row["fact"])
        if fact in seen_facts:
            continue
        seen_facts.add(fact)
        rows.append(row)
    return tuple(rows)


def _candidate_facts_toml(
    *,
    scope_summary: str,
    in_scope: tuple[str, ...],
    source_sessions: tuple[str, ...],
    session_text: str = "",
    fact_rows: tuple[dict[str, object], ...] | None = None,
) -> str:
    lines = ["facts_version = 1", ""]
    rows = fact_rows or _candidate_fact_rows(
        scope_summary=scope_summary,
        in_scope=in_scope,
        source_sessions=source_sessions,
        session_text=session_text,
    )
    for row in rows:
        lines.append("[[facts]]")
        lines.append(f'grouping_key = {json.dumps(str(row["grouping_key"]))}')
        lines.append(f'section = {json.dumps(str(row["section"]))}')
        lines.append(f'fact = {json.dumps(str(row["fact"]))}')
        lines.append(f'confidence = {float(row["confidence"]):.2f}')
        lines.append(f'provenance_sessions = {_toml_string_list(tuple(str(item) for item in row["provenance_sessions"]))}')
        repo_paths = row.get("repo_paths")
        if isinstance(repo_paths, list) and repo_paths:
            lines.append(f'repo_paths = {_toml_string_list(tuple(str(item) for item in repo_paths))}')
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def stage_candidate_from_session(
    project_root: Path,
    session_file: Path,
    semantic_seed: dict[str, Any] | None = None,
) -> CandidateStageResult:
    """Create or update a governed capability candidate from a Codex session."""
    resolved_root = resolve_project_root(project_root)
    governed_root = resolved_root / ".governed"
    if not governed_root.is_dir():
        raise FileNotFoundError(f"missing governed root: {governed_root}")

    session_id, timestamp, user_text, assistant_text = _session_text(session_file)
    ignored_tokens = _ignored_tokens(resolved_root)
    candidate_id = _semantic_seed_identifier(semantic_seed, "candidate_id") or _candidate_id(
        user_text,
        assistant_text,
        ignored_tokens,
    )
    proposed_candidate_id = candidate_id
    summary = _semantic_seed_text(semantic_seed, "summary") or _candidate_summary(
        candidate_id,
        user_text,
        assistant_text,
        ignored_tokens,
    )
    session_text = f"{user_text}\n{assistant_text}"
    raw_hints = _semantic_seed_string_list(semantic_seed, "routing_hints", limit=12) or _path_hints(
        session_text,
        ignored_tokens,
        limit=10,
    ) or _keywords(
        session_text,
        limit=10,
        ignored_tokens=ignored_tokens,
    ) or (
        candidate_id.replace("-", " "),
    )
    initial_default_capability_id = _semantic_seed_identifier(semantic_seed, "default_capability_id") or _suggested_capability_ids(
        candidate_id,
        raw_hints,
        ignored_tokens,
    )[0]
    hints = _canonical_routing_hints(initial_default_capability_id, raw_hints, ignored_tokens)
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
            or semantic_seed is not None
        ):
            suggested_capability_ids = _suggested_capability_ids(candidate_id, raw_hints, ignored_tokens)
            seeded_default_capability_id = _semantic_seed_identifier(semantic_seed, "default_capability_id")
            if seeded_default_capability_id:
                suggested_capability_ids = tuple(
                    dict.fromkeys((seeded_default_capability_id, *suggested_capability_ids))
                )
            default_capability_id = suggested_capability_ids[0]
        else:
            default_capability_id = existing_default_capability_id
            suggested_capability_ids = candidate_suggested_capability_ids(existing, candidate_id)
        hints = _canonical_routing_hints(default_capability_id, raw_hints, ignored_tokens)
        existing_summary = proposal.get("summary") if isinstance(proposal, dict) else None
        if semantic_seed is None and isinstance(existing_summary, str) and existing_summary.strip():
            summary = existing_summary
        summary = _narrowed_summary(default_capability_id, summary)
        scope = existing.get("scope") if isinstance(existing.get("scope"), dict) else {}
        existing_scope_summary = scope.get("summary") if isinstance(scope, dict) else None
        in_scope = tuple(str(item) for item in scope.get("in_scope", ()) if isinstance(item, str)) if isinstance(scope, dict) else ()
        out_of_scope = tuple(str(item) for item in scope.get("out_of_scope", ()) if isinstance(item, str)) if isinstance(scope, dict) else ()
        seeded_scope_summary, seeded_in_scope, seeded_out_of_scope = _semantic_scope_metadata(semantic_seed)
        if refresh_proposal or not isinstance(existing_scope_summary, str) or not existing_scope_summary.strip() or not in_scope or not out_of_scope:
            computed_scope_summary, computed_in_scope, computed_out_of_scope = _scope_metadata(
                default_capability_id,
                hints,
                ignored_tokens,
                summary,
            )
            scope_summary = seeded_scope_summary or computed_scope_summary
            in_scope = seeded_in_scope or (computed_in_scope if refresh_proposal else in_scope or computed_in_scope)
            out_of_scope = seeded_out_of_scope or (
                computed_out_of_scope if refresh_proposal else out_of_scope or computed_out_of_scope
            )
        else:
            scope_summary = seeded_scope_summary or existing_scope_summary
            in_scope = seeded_in_scope or in_scope
            out_of_scope = seeded_out_of_scope or out_of_scope
    else:
        suggested_capability_ids = _suggested_capability_ids(candidate_id, raw_hints, ignored_tokens)
        seeded_default_capability_id = _semantic_seed_identifier(semantic_seed, "default_capability_id")
        if seeded_default_capability_id:
            suggested_capability_ids = tuple(dict.fromkeys((seeded_default_capability_id, *suggested_capability_ids)))
        default_capability_id = suggested_capability_ids[0]
        hints = _canonical_routing_hints(default_capability_id, raw_hints, ignored_tokens)
        summary = _narrowed_summary(default_capability_id, summary)
        scope_summary, in_scope, out_of_scope = _scope_metadata(default_capability_id, hints, ignored_tokens, summary)
        seeded_scope_summary, seeded_in_scope, seeded_out_of_scope = _semantic_scope_metadata(semantic_seed)
        scope_summary = seeded_scope_summary or scope_summary
        in_scope = seeded_in_scope or in_scope
        out_of_scope = seeded_out_of_scope or out_of_scope

    _remove_stale_session_candidates(governed_root, candidate_root, session_id)
    semantic_fact_rows = _semantic_fact_rows(semantic_seed, source_sessions=tuple(source_sessions))
    candidate_root.mkdir(parents=True, exist_ok=True)
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
    (candidate_root / "candidate-facts.toml").write_text(
        _candidate_facts_toml(
            scope_summary=scope_summary,
            in_scope=in_scope,
            source_sessions=tuple(source_sessions),
            session_text=session_text,
            fact_rows=semantic_fact_rows or None,
        ),
        encoding="utf-8",
    )

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
