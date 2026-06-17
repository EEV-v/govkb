"""Strict governed skill package validation."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import re
from typing import Iterable

from govkb.core.contracts import CapabilityContract
from govkb.core.contracts import ProjectBundle


STRICT_SEVERITIES = {"error", "warning", "info"}

PLACEHOLDER_PATTERNS = (
    re.compile(r"^\s*-\s*TODO:", re.I),
    re.compile(r"^\s*-\s*Use this section", re.I),
    re.compile(r"^\s*-\s*Add .+ here", re.I),
    re.compile(r"\bTODO:\b", re.I),
)
MARKDOWN_PATH_PATTERN = re.compile(r"`([^`\n]+)`")
TOKEN_PATTERNS = (
    re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b"),
    re.compile(r"\beyJ[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{10,}\b"),
)
RUNTIME_ONLY_PATH_REFERENCES = {
    ".vscode/mcp.json",
}
RUNTIME_ONLY_PATH_PREFIXES = (
    "investigation-results/",
)
RUNTIME_ONLY_CONFIG_SUFFIXES = {
    ".creds",
    ".env",
}
CREDENTIAL_PATH_PATTERNS = (
    re.compile(r"(?:^|[\s`])~/(?:\.ssh|\.aws|\.azure|\.config/gcloud|\.kube)(?:/|[\s`]|$)"),
    re.compile(r"(?:^|[/\s`])\.(?:netrc|npmrc|pypirc|env|env\.local)(?:$|[\s`])"),
    re.compile(r"(?:^|[/\s`])(?:id_rsa|id_ed25519)(?:$|[\s`])"),
    re.compile(r"(?i)(?:^|[/\s`])[^`\s]*(?:\.pem|\.key|\.p12)(?:$|[\s`])"),
    re.compile(
        r"(?i)(?:^|[\s`])(?:~?/|\.?/|[A-Za-z0-9_.-]+/)[^`\s]*"
        r"(?:credential|credentials|secret|secrets|token|service-account)[^`\s]*(?:$|[\s`])"
    ),
)
LIKELY_MUTATION_PATTERNS = (
    re.compile(r"\brm\s+-"),
    re.compile(r"\bmv\s+"),
    re.compile(r"\bcp\s+"),
    re.compile(r"\bsed\s+-i\b"),
    re.compile(r"\b(write_text|unlink|rmtree|remove|rename)\b"),
)
GENERIC_ID_TOKENS = {
    "capability",
    "checklist",
    "governed",
    "knowledge",
    "local",
    "playbook",
    "project",
    "review",
    "runbook",
    "setup",
    "stack",
    "triage",
    "verification",
    "workflow",
}
WEAK_GENERIC_IDS = {"local-stack-workflow", "workflow-review", "project-workflow"}


@dataclass(frozen=True)
class StrictIssue:
    """Structured strict validation issue."""

    severity: str
    rule_id: str
    location: str
    message: str

    def as_dict(self) -> dict[str, str]:
        """Return a JSON-serializable issue payload."""
        return {
            "severity": self.severity,
            "ruleId": self.rule_id,
            "location": self.location,
            "message": self.message,
        }


@dataclass
class StrictValidationResult:
    """Strict governed skill validation result."""

    issues: list[StrictIssue] = field(default_factory=list)

    @property
    def errors(self) -> tuple[StrictIssue, ...]:
        return tuple(issue for issue in self.issues if issue.severity == "error")

    @property
    def warnings(self) -> tuple[StrictIssue, ...]:
        return tuple(issue for issue in self.issues if issue.severity == "warning")

    @property
    def infos(self) -> tuple[StrictIssue, ...]:
        return tuple(issue for issue in self.issues if issue.severity == "info")

    @property
    def ok(self) -> bool:
        return not self.errors

    def add(self, severity: str, rule_id: str, location: Path | str, message: str) -> None:
        if severity not in STRICT_SEVERITIES:
            raise ValueError(f"unknown strict validation severity: {severity}")
        self.issues.append(StrictIssue(severity, rule_id, str(location), message))

    def extend(self, issues: Iterable[StrictIssue]) -> None:
        self.issues.extend(issues)


def validate_governed_skill_bundle(
    project_root: Path,
    bundle: ProjectBundle,
    *,
    activation_required: bool = False,
) -> StrictValidationResult:
    """Validate all loaded governed capability packages."""
    result = StrictValidationResult()
    for contract in bundle.capabilities.values():
        result.extend(
            validate_governed_skill_package(
                project_root,
                contract,
                activation_required=activation_required,
            ).issues
        )
    return result


def validate_governed_skill_package(
    project_root: Path,
    contract: CapabilityContract,
    *,
    activation_required: bool = False,
) -> StrictValidationResult:
    """Validate one governed capability package using strict quality rules."""
    result = StrictValidationResult()
    capability_root = contract.capability_root
    _check_required_files(result, contract)
    _check_identifier(result, contract, activation_required=activation_required)
    _check_lifecycle(result, contract, activation_required=activation_required)
    _check_memory(result, contract)
    _check_markdown_paths(result, project_root, capability_root)
    _check_safety(result, capability_root)
    _check_tools(result, capability_root)
    return result


def _check_required_files(result: StrictValidationResult, contract: CapabilityContract) -> None:
    root = contract.capability_root
    required = [
        root / "capability.contract.toml",
        root / "instructions.md",
        root / "prompts" / "initialize-kb.md",
    ]
    if contract.memory_enabled:
        required.append(root / "references" / "long-term-memory.md")
        required.extend(root / target.path for target in contract.targets)
    for path in dict.fromkeys(required):
        if not path.is_file():
            result.add("error", "GSK-PACKAGE-001", path, "required governed skill package file is missing")


def _check_identifier(
    result: StrictValidationResult,
    contract: CapabilityContract,
    *,
    activation_required: bool,
) -> None:
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", contract.capability_id):
        result.add("error", "GSK-ID-001", contract.source_path, "capability id must be lower kebab-case")
    if not _is_generic_identifier(contract.capability_id):
        return
    if activation_required and not contract.lifecycle.scope_justification:
        result.add(
            "error",
            "GSK-ID-002",
            contract.source_path,
            "generic capability id requires explicit scope justification before activation",
        )
    elif not contract.lifecycle.scope_justification:
        result.add(
            "warning",
            "GSK-ID-002",
            contract.source_path,
            "generic capability id should document why it is intentionally generic",
        )


def _is_generic_identifier(capability_id: str) -> bool:
    if capability_id in WEAK_GENERIC_IDS:
        return True
    tokens = [token for token in capability_id.split("-") if token]
    domain_tokens = [token for token in tokens if token not in GENERIC_ID_TOKENS]
    return not domain_tokens


def _check_lifecycle(
    result: StrictValidationResult,
    contract: CapabilityContract,
    *,
    activation_required: bool,
) -> None:
    state = contract.lifecycle.state
    if state and state not in {"draft", "strict-valid", "approved", "active", "rejected", "deprecated"}:
        result.add("warning", "GSK-LIFECYCLE-002", contract.source_path, f"unknown lifecycle state: {state}")
    if state == "deprecated":
        result.add("info", "GSK-LIFECYCLE-003", contract.source_path, "capability is deprecated")
    if not activation_required:
        return
    approval = contract.lifecycle.approval
    if approval.status != "approved" or not approval.reviewer or not approval.approved_at:
        result.add(
            "error",
            "GSK-LIFECYCLE-001",
            contract.source_path,
            "activation requires approved lifecycle metadata with reviewer and approved_at",
        )
    if state not in {"approved", "active"}:
        result.add(
            "error",
            "GSK-LIFECYCLE-001",
            contract.source_path,
            "activation requires lifecycle state approved or active",
        )


def _check_memory(result: StrictValidationResult, contract: CapabilityContract) -> None:
    for target in contract.targets:
        path = contract.capability_root / target.path
        if not path.is_file():
            result.add("error", "GSK-MEMORY-001", path, "configured memory target file is missing")
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        sections = _markdown_sections(text)
        for section in target.sections:
            if section not in sections:
                result.add("error", "GSK-MEMORY-001", path, f"memory target is missing section: {section}")
        for line_number, line in enumerate(text.splitlines(), start=1):
            if _is_placeholder(line):
                result.add(
                    "error",
                    "GSK-MEMORY-001",
                    f"{path}:{line_number}",
                    "memory contains scaffold placeholder content",
                )
    instructions = contract.capability_root / "instructions.md"
    if instructions.is_file():
        for line_number, line in enumerate(instructions.read_text(encoding="utf-8", errors="replace").splitlines(), start=1):
            if _is_placeholder(line):
                result.add(
                    "error",
                    "GSK-MEMORY-001",
                    f"{instructions}:{line_number}",
                    "instructions contain scaffold placeholder content",
                )


def _markdown_sections(text: str) -> set[str]:
    return {line[3:].strip() for line in text.splitlines() if line.startswith("## ")}


def _is_placeholder(line: str) -> bool:
    return any(pattern.search(line) for pattern in PLACEHOLDER_PATTERNS)


def _scan_text_files(capability_root: Path) -> tuple[Path, ...]:
    suffixes = {".md", ".toml", ".txt", ".sh", ".py"}
    paths: list[Path] = []
    for path in capability_root.rglob("*"):
        if path.is_file() and path.suffix in suffixes:
            paths.append(path)
    return tuple(sorted(paths))


def _check_markdown_paths(result: StrictValidationResult, project_root: Path, capability_root: Path) -> None:
    for path in _scan_text_files(capability_root):
        if path.suffix not in {".md", ".toml"}:
            continue
        for line_number, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), start=1):
            if "planned" in line.lower():
                continue
            for raw_value in MARKDOWN_PATH_PATTERN.findall(line):
                value = raw_value.strip()
                if not _looks_like_path_reference(value):
                    continue
                target = Path(value)
                if target.is_absolute() or value.startswith("~") or ".." in target.parts:
                    result.add("error", "GSK-PATH-001", f"{path}:{line_number}", "package path reference must be safe and relative")
                    continue
                if _is_runtime_only_path_reference(value):
                    continue
                if not (project_root / target).exists() and not (capability_root / target).exists():
                    result.add(
                        "error",
                        "GSK-PATH-001",
                        f"{path}:{line_number}",
                        f"repo-relative or package-relative path does not exist: {value}",
                    )


def _looks_like_path_reference(value: str) -> bool:
    if any(char.isspace() for char in value):
        return False
    if "/" in value or value.startswith("~") or value.startswith("."):
        return True
    return Path(value).suffix in {".md", ".toml", ".json", ".yaml", ".yml", ".py", ".sh"}


def _is_runtime_only_path_reference(value: str) -> bool:
    normalized = value.rstrip("/")
    if normalized in RUNTIME_ONLY_PATH_REFERENCES:
        return True
    if value.startswith(".config/") and Path(value).suffix in RUNTIME_ONLY_CONFIG_SUFFIXES:
        return True
    return any(value.startswith(prefix) for prefix in RUNTIME_ONLY_PATH_PREFIXES)


def _check_safety(result: StrictValidationResult, capability_root: Path) -> None:
    for path in _scan_text_files(capability_root):
        for line_number, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), start=1):
            for pattern in CREDENTIAL_PATH_PATTERNS:
                if pattern.search(line):
                    result.add(
                        "error",
                        "GSK-SAFETY-001",
                        f"{path}:{line_number}",
                        "forbidden credential path pattern found",
                    )
                    break
            for pattern in TOKEN_PATTERNS:
                if pattern.search(line):
                    result.add(
                        "error",
                        "GSK-SAFETY-001",
                        f"{path}:{line_number}",
                        "token-like or secret-like content found",
                    )
                    break


def _check_tools(result: StrictValidationResult, capability_root: Path) -> None:
    tools_root = capability_root / "tools"
    scripts_root = tools_root / "scripts"
    fixtures_root = tools_root / "fixtures"
    if (scripts_root.exists() or fixtures_root.exists()) and not (tools_root / "README.md").is_file():
        result.add("warning", "GSK-TOOLS-001", tools_root / "README.md", "tools require README with purpose, safety, and usage")
    if not scripts_root.is_dir():
        return
    for script in sorted(path for path in scripts_root.rglob("*") if path.is_file()):
        text = script.read_text(encoding="utf-8", errors="replace")
        if "--dry-run" in text or "--preview" in text:
            continue
        if any(pattern.search(text) for pattern in LIKELY_MUTATION_PATTERNS):
            result.add(
                "warning",
                "GSK-TOOLS-002",
                script,
                "mutating helper script should document --dry-run or --preview behavior",
            )
