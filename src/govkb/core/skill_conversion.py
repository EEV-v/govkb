"""Preview and write conversion from local Codex skills to governed packages."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import re
import shutil
import tempfile

from govkb.core.contracts import load_project_bundle
from govkb.core.governed_skill import StrictIssue
from govkb.core.governed_skill import validate_governed_skill_package
from govkb.core.ids import normalize_identifier
from govkb.core.install_state import iso_utc_now
from govkb.core.project import resolve_project_root


DEFAULT_MEMORY_SECTIONS = (
    "Working Agreement",
    "Stable Workflows",
    "Commands And Verification",
    "Code And Docs Map",
    "Authority Rules",
)
TEXT_SUFFIXES = {".md", ".txt", ".toml", ".json", ".yaml", ".yml", ".py", ".sh"}
TOKEN_PATTERNS = (
    re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b"),
    re.compile(r"\beyJ[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{10,}\b"),
    re.compile(r"(?i)\b[A-Z0-9_]*(TOKEN|SECRET|PASSWORD|API_KEY|APIKEY)[A-Z0-9_]*\b\s*[:=]\s*\S+"),
)
CREDENTIAL_PATTERNS = (
    re.compile(r"(?:^|[\s`])~/(?:\.ssh|\.aws|\.azure|\.config/gcloud|\.kube)(?:/|[\s`]|$)"),
    re.compile(r"(?:^|[/\s`])\.(?:netrc|npmrc|pypirc|env|env\.local)(?:$|[\s`])"),
    re.compile(r"(?:^|[/\s`])(?:id_rsa|id_ed25519)(?:$|[\s`])"),
    re.compile(r"(?i)(?:^|[/\s`])[^`\s]*(?:\.pem|\.key|\.p12)(?:$|[\s`])"),
)
PATH_TOKEN_PATTERN = re.compile(r"`([^`\n]+)`")


@dataclass(frozen=True)
class ConversionItem:
    """One source item classification."""

    source: str
    classification: str
    action: str
    reason: str
    destination: str | None = None

    def as_dict(self) -> dict[str, str | None]:
        return {
            "source": self.source,
            "classification": self.classification,
            "action": self.action,
            "reason": self.reason,
            "destination": self.destination,
        }


@dataclass(frozen=True)
class ConversionPlan:
    """Conversion preview plan."""

    source_path: Path
    project_root: Path
    source_name: str
    capability_id: str
    capability_name: str
    package_path: Path
    instructions_text: str
    memory_text: str
    items: tuple[ConversionItem, ...]
    parity_level: str
    strict_issues: tuple[StrictIssue, ...]
    strict_status: str

    @property
    def planned_items(self) -> tuple[ConversionItem, ...]:
        return tuple(item for item in self.items if item.action in {"transform", "copy", "create"})

    @property
    def rejected_items(self) -> tuple[ConversionItem, ...]:
        return tuple(item for item in self.items if item.action == "reject")

    @property
    def manual_review_items(self) -> tuple[ConversionItem, ...]:
        return tuple(item for item in self.items if item.action == "manual-review")

    def as_dict(self) -> dict[str, object]:
        return {
            "sourcePath": str(self.source_path),
            "projectRoot": str(self.project_root),
            "sourceName": self.source_name,
            "capabilityId": self.capability_id,
            "capabilityName": self.capability_name,
            "packagePath": str(self.package_path),
            "plannedItems": [item.as_dict() for item in self.planned_items],
            "rejectedItems": [item.as_dict() for item in self.rejected_items],
            "manualReviewItems": [item.as_dict() for item in self.manual_review_items],
            "parityLevel": self.parity_level,
            "strictStatus": self.strict_status,
            "strictIssues": [issue.as_dict() for issue in self.strict_issues],
        }


@dataclass(frozen=True)
class ConversionWriteResult:
    """Result of a conversion write."""

    plan: ConversionPlan
    created_package: Path
    strict_issues: tuple[StrictIssue, ...]
    package_removed: bool = False

    def as_dict(self) -> dict[str, object]:
        payload = self.plan.as_dict()
        payload["createdPackage"] = str(self.created_package)
        payload["packageRemoved"] = self.package_removed
        payload["strictIssues"] = [issue.as_dict() for issue in self.strict_issues]
        payload["strictStatus"] = "passed" if not self.strict_issues else self.plan.strict_status
        return payload


def build_conversion_plan(
    source: str,
    *,
    project_root: Path,
    codex_home: Path | None = None,
    capability_id: str | None = None,
) -> ConversionPlan:
    """Build a non-mutating conversion plan for one local Codex skill."""
    resolved_project_root = resolve_project_root(project_root.resolve())
    source_path = resolve_source_skill(source, codex_home=codex_home)
    skill_path = source_path / "SKILL.md"
    if not skill_path.is_file():
        raise FileNotFoundError(f"source skill missing SKILL.md: {source_path}")
    skill_text = skill_path.read_text(encoding="utf-8", errors="replace")
    frontmatter, body = _split_frontmatter(skill_text)
    source_name = _frontmatter_value(frontmatter, "name") or source_path.name
    description = _frontmatter_value(frontmatter, "description") or f"Converted from local Codex skill {source_name}."
    target_id = normalize_identifier(capability_id or source_name or source_path.name)
    package_path = resolved_project_root / ".governed" / "capabilities" / target_id
    capability_name = target_id.replace("-", " ").title()

    copy_items = _classified_copy_items(source_path)
    skill_unsafe_reason = _unsafe_reason(skill_path)
    if skill_unsafe_reason is None:
        instructions_text = _instructions_text(capability_name, body or skill_text, source_name)
        items: list[ConversionItem] = [
            ConversionItem(
                source="SKILL.md",
                classification="governed",
                action="transform",
                reason="canonical governed instructions",
                destination="instructions.md",
            )
        ]
    else:
        instructions_text = _instructions_text(
            capability_name,
            f"Use this governed capability after reviewing the converted `{source_name}` source skill.",
            source_name,
        )
        items = [
            ConversionItem(
                source="SKILL.md",
                classification="unsafe",
                action="reject",
                reason=skill_unsafe_reason,
                destination=None,
            ),
            ConversionItem(
                source="(generated)",
                classification="governed",
                action="create",
                reason="safe placeholder instructions because source SKILL.md was rejected",
                destination="instructions.md",
            ),
        ]
    memory_text, memory_item = _memory_text(source_path, capability_name, resolved_project_root)
    items.append(memory_item)
    items.extend(copy_items)
    if any(item.destination and item.destination.startswith("tools/") for item in items):
        items.append(
            ConversionItem(
                source="(generated)",
                classification="tool",
                action="create",
                reason="tool safety documentation",
                destination="tools/README.md",
            )
        )
    items.append(
        ConversionItem(
            source="(generated)",
            classification="governed",
            action="create",
            reason="strict package initialization prompt",
            destination="prompts/initialize-kb.md",
        )
    )
    items.append(
        ConversionItem(
            source="(generated)",
            classification="governed",
            action="create",
            reason="redacted conversion report",
            destination="docs/conversion-report.md",
        )
    )
    parity = "Governed semantic parity" if any(item.action == "reject" for item in items) else "Exact content copy"
    instructions_text = _repair_converted_text(
        instructions_text,
        project_root=resolved_project_root,
        source_path=source_path,
        items=tuple(items),
    )
    memory_text = _repair_converted_text(
        memory_text,
        project_root=resolved_project_root,
        source_path=source_path,
        items=tuple(items),
    )
    strict_issues = _preview_strict_issues(
        resolved_project_root=resolved_project_root,
        source_path=source_path,
        project_root=resolved_project_root,
        source_name=source_name,
        capability_id=target_id,
        capability_name=capability_name,
        description=description,
        instructions_text=instructions_text,
        memory_text=memory_text,
        items=tuple(items),
        parity_level=parity,
    )
    strict_status = "passed" if not any(issue.severity == "error" for issue in strict_issues) else "failed"
    return ConversionPlan(
        source_path=source_path,
        project_root=resolved_project_root,
        source_name=source_name,
        capability_id=target_id,
        capability_name=capability_name,
        package_path=package_path,
        instructions_text=instructions_text,
        memory_text=memory_text,
        items=tuple(items),
        parity_level=parity,
        strict_issues=strict_issues,
        strict_status=strict_status,
    )


def resolve_source_skill(source: str, *, codex_home: Path | None = None) -> Path:
    """Resolve a source skill name or explicit directory path."""
    source_path = Path(source).expanduser()
    if source_path.is_dir():
        return source_path.resolve()
    if source_path.is_file() and source_path.name == "SKILL.md":
        return source_path.parent.resolve()
    if source_path.exists() and not source_path.is_dir():
        raise NotADirectoryError(f"source skill is not a directory: {source_path}")
    if codex_home is None:
        raise FileNotFoundError(f"source skill path not found and --codex-home not provided: {source}")
    named = (codex_home.expanduser() / "skills" / source).resolve()
    if not named.is_dir():
        raise FileNotFoundError(f"source skill not found: {named}")
    return named


def write_conversion_package(plan: ConversionPlan) -> ConversionWriteResult:
    """Write one converted governed package and validate it."""
    if plan.package_path.exists():
        raise FileExistsError(f"target governed capability already exists: {plan.package_path}")
    plan.package_path.mkdir(parents=True, exist_ok=False)
    try:
        _render_package(plan, plan.package_path)
        bundle, result = load_project_bundle(plan.package_path.parents[2])
        if result.errors:
            message = "; ".join(f"{item.location}: {item.message}" for item in result.errors)
            raise ValueError(f"converted package failed base validation: {message}")
        contract = bundle.capabilities.get(plan.capability_id)
        if contract is None:
            raise ValueError(f"converted package was not loaded: {plan.capability_id}")
        strict = validate_governed_skill_package(bundle.project_root, contract)
        strict_errors = tuple(issue for issue in strict.issues if issue.severity == "error")
        if strict_errors:
            return _fail_strict(plan, strict_errors)
        return ConversionWriteResult(plan=plan, created_package=plan.package_path, strict_issues=())
    except Exception:
        shutil.rmtree(plan.package_path, ignore_errors=True)
        raise


def _fail_strict(plan: ConversionPlan, strict_errors: tuple[StrictIssue, ...]) -> ConversionWriteResult:
    shutil.rmtree(plan.package_path, ignore_errors=True)
    return ConversionWriteResult(plan=plan, created_package=plan.package_path, strict_issues=strict_errors, package_removed=True)


def _preview_strict_issues(
    *,
    resolved_project_root: Path,
    source_path: Path,
    project_root: Path,
    source_name: str,
    capability_id: str,
    capability_name: str,
    description: str,
    instructions_text: str,
    memory_text: str,
    items: tuple[ConversionItem, ...],
    parity_level: str,
) -> tuple[StrictIssue, ...]:
    with tempfile.TemporaryDirectory(prefix="govkb-conversion-preview-") as temp_dir:
        temp_project = Path(temp_dir) / "Project"
        temp_project.mkdir(parents=True, exist_ok=True)
        for name in _project_entrypoint_paths(resolved_project_root):
            source_file = resolved_project_root / name
            if source_file.is_file():
                (temp_project / name).write_text(source_file.read_text(encoding="utf-8", errors="replace"), encoding="utf-8")
        governed_root = temp_project / ".governed"
        governed_root.mkdir(parents=True, exist_ok=True)
        (governed_root / "project.toml").write_text(
            'schema_version = 1\n\n[project]\nid = "preview-project"\nname = "Preview Project"\n\n[release]\ncurrent = "unreleased"\n\n[adapters]\nenabled = ["codex"]\n',
            encoding="utf-8",
        )
        package_root = governed_root / "capabilities" / capability_id
        package_root.mkdir(parents=True, exist_ok=True)
        preview_plan = ConversionPlan(
            source_path=source_path,
            project_root=project_root,
            source_name=source_name,
            capability_id=capability_id,
            capability_name=capability_name,
            package_path=package_root,
            instructions_text=instructions_text,
            memory_text=memory_text,
            items=items,
            parity_level=parity_level,
            strict_issues=(),
            strict_status="pending",
        )
        _render_package(preview_plan, package_root, description=description)
        _copy_referenced_project_files_for_preview(preview_plan, package_root, temp_project)
        bundle, result = load_project_bundle(temp_project)
        if result.errors or capability_id not in bundle.capabilities:
            return ()
        strict = validate_governed_skill_package(temp_project, bundle.capabilities[capability_id])
        return strict.issues


def _render_package(plan: ConversionPlan, package_root: Path, *, description: str | None = None) -> None:
    package_root.mkdir(parents=True, exist_ok=True)
    (package_root / "references").mkdir(parents=True, exist_ok=True)
    (package_root / "prompts").mkdir(parents=True, exist_ok=True)
    (package_root / "docs").mkdir(parents=True, exist_ok=True)
    (package_root / "capability.contract.toml").write_text(
        _contract_text(plan, description=description),
        encoding="utf-8",
    )
    (package_root / "instructions.md").write_text(plan.instructions_text, encoding="utf-8")
    (package_root / "references" / "long-term-memory.md").write_text(plan.memory_text, encoding="utf-8")
    (package_root / "prompts" / "initialize-kb.md").write_text(_initialize_prompt(plan), encoding="utf-8")

    for item in plan.items:
        if item.action != "copy" or item.destination is None:
            continue
        source_path = plan.source_path / item.source
        destination = package_root / item.destination
        destination.parent.mkdir(parents=True, exist_ok=True)
        _copy_source_item(plan, item, source_path, destination)
    if any(item.destination and item.destination.startswith("tools/") for item in plan.items):
        tools_readme = package_root / "tools" / "README.md"
        tools_readme.parent.mkdir(parents=True, exist_ok=True)
        tools_readme.write_text(_tools_readme(plan), encoding="utf-8")
    (package_root / "docs" / "conversion-report.md").write_text(_conversion_report(plan), encoding="utf-8")


def _contract_text(plan: ConversionPlan, *, description: str | None = None) -> str:
    desc = description or f"Converted from local Codex skill {plan.source_name}."
    now = iso_utc_now()
    entrypoints = _project_entrypoint_paths(plan.project_root)
    return f"""contract_version = 1

[capability]
id = "{plan.capability_id}"
name = "{plan.capability_name}"
governed = true
description = {json.dumps(desc)}

[routing]
aliases = ["{plan.capability_id}", "{plan.capability_id.replace("-", " ")}"]
hints = ["converted codex skill", "{plan.capability_id.replace("-", " ")}"]
negative_hints = []

[memory]
enabled = true
auto_apply_min_confidence = 0.85
requires_explicit_acceptance = false

[memory.targets.main]
path = "references/long-term-memory.md"
sections = {_toml_string_list(DEFAULT_MEMORY_SECTIONS)}

[bootstrap]
profile = "workflow"
repo_roots = ["."]
authority_paths = {_toml_string_list(entrypoints[:1])}
seed_paths = {_toml_string_list(entrypoints)}

[kb_health]
requires_verification_commands = true
requires_repo_map = true
required_sections = ["Working Agreement", "Stable Workflows", "Commands And Verification", "Code And Docs Map"]

[lifecycle]
state = "strict-valid"
scope_justification = "Converted one local Codex skill into a governed package for review."

[migration]
source_adapter = "codex"
source_path = {json.dumps(str(plan.source_path))}
status = "converted"
source_name = {json.dumps(plan.source_name)}
converted_at = "{now}"
parity_level = {json.dumps(plan.parity_level)}
rejected_item_count = {len(plan.rejected_items)}
strict_validation_passed = {str(plan.strict_status == "passed").lower()}
"""


def _toml_string_list(values: tuple[str, ...]) -> str:
    return "[" + ", ".join(json.dumps(value) for value in values) + "]"


def _split_frontmatter(text: str) -> tuple[str, str]:
    stripped = text.strip()
    if not stripped.startswith("---"):
        return "", text.strip()
    match = re.match(r"^---\n(.*?)\n---\n?(.*)$", stripped, re.S)
    if not match:
        return "", text.strip()
    return match.group(1), match.group(2).strip()


def _frontmatter_value(frontmatter: str, key: str) -> str | None:
    for line in frontmatter.splitlines():
        if line.startswith(f"{key}:"):
            value = line.split(":", 1)[1].strip().strip('"')
            return value or None
    return None


def _instructions_text(capability_name: str, body: str, source_name: str) -> str:
    body_text = body.strip() or f"Use this governed capability for the converted `{source_name}` workflow."
    if body_text.startswith("# "):
        return body_text.rstrip() + "\n"
    return f"# {capability_name}\n\n{body_text}\n"


def _memory_text(source_path: Path, capability_name: str, project_root: Path) -> tuple[str, ConversionItem]:
    source_memory = source_path / "references" / "long-term-memory.md"
    if source_memory.is_file():
        reason = _unsafe_reason(source_memory)
        if reason is None:
            return source_memory.read_text(encoding="utf-8", errors="replace").rstrip() + "\n", ConversionItem(
                source="references/long-term-memory.md",
                classification="governed",
                action="transform",
                reason="canonical governed memory target",
                destination="references/long-term-memory.md",
            )
        return _generated_memory(capability_name, project_root), ConversionItem(
            source="references/long-term-memory.md",
            classification="unsafe",
            action="reject",
            reason=reason,
            destination=None,
        )
    return _generated_memory(capability_name, project_root), ConversionItem(
        source="(generated)",
        classification="governed",
        action="create",
        reason="required memory target",
        destination="references/long-term-memory.md",
    )


def _project_entrypoint_paths(project_root: Path) -> tuple[str, ...]:
    preferred = (
        "README.md",
        "AGENTS.md",
        "pyproject.toml",
        "package.json",
        "docs",
        "src",
    )
    return tuple(path for path in preferred if (project_root / path).exists())


def _generated_memory(capability_name: str, project_root: Path) -> str:
    entrypoints = _project_entrypoint_paths(project_root)
    repo_entry = (
        f"- Use `{entrypoints[0]}` as the repository entry point while reviewing converted content."
        if entrypoints
        else "- Use the repository root and governed package files while reviewing converted content."
    )
    return f"""# {capability_name}

## Working Agreement

- Keep this converted capability focused on durable workflow guidance from the source skill.

## Stable Workflows

- Review source skill behavior before relying on converted guidance in future tasks.

## Commands And Verification

- Run `python3 -m unittest tests.test_skill_conversion -v` from the repository root after conversion changes.

## Code And Docs Map

{repo_entry}

## Authority Rules

- Treat governed package files as the source of truth after conversion review.
"""


def _classified_copy_items(source_path: Path) -> tuple[ConversionItem, ...]:
    items: list[ConversionItem] = []
    for path in sorted(source_path.rglob("*")):
        if not path.is_file() or path.name == "SKILL.md":
            continue
        rel = path.relative_to(source_path).as_posix()
        if rel == "references/long-term-memory.md":
            continue
        reason = _unsafe_reason(path)
        if reason is not None:
            items.append(ConversionItem(rel, "unsafe", "reject", reason, None))
            continue
        destination = _destination_for(rel)
        if destination is None:
            items.append(ConversionItem(rel, "manual review", "manual-review", "unsupported or ambiguous source location", None))
            continue
        classification = "tool" if destination.startswith("tools/") else "governed"
        items.append(ConversionItem(rel, classification, "copy", "safe source item", destination))
    return tuple(items)


def _destination_for(rel: str) -> str | None:
    parts = Path(rel).parts
    if not parts:
        return None
    if parts[0] == "references":
        return rel
    if parts[0] == "prompts":
        return rel
    if parts[0] == "tools":
        return rel
    if parts[0] == "scripts":
        return "tools/scripts/" + "/".join(parts[1:])
    if parts[0] == "fixtures":
        return "tools/fixtures/" + "/".join(parts[1:])
    return None


def _unsafe_reason(path: Path) -> str | None:
    if path.suffix and path.suffix not in TEXT_SUFFIXES:
        return None
    text = path.read_text(encoding="utf-8", errors="replace")
    for pattern in TOKEN_PATTERNS:
        if pattern.search(text):
            return "token-like or secret-like content"
    for pattern in CREDENTIAL_PATTERNS:
        if pattern.search(text):
            return "credential path pattern"
    if "raw transcript" in text.lower():
        return "raw transcript reference"
    return None


def _copy_source_item(plan: ConversionPlan, item: ConversionItem, source_path: Path, destination: Path) -> None:
    if source_path.suffix not in TEXT_SUFFIXES:
        shutil.copy2(source_path, destination)
        return
    text = source_path.read_text(encoding="utf-8", errors="replace")
    repaired = _repair_converted_text(text, project_root=plan.project_root, source_path=plan.source_path, items=plan.items)
    destination.write_text(repaired, encoding="utf-8")
    try:
        shutil.copystat(source_path, destination, follow_symlinks=False)
    except OSError:
        pass


def _repair_converted_text(
    text: str,
    *,
    project_root: Path,
    source_path: Path,
    items: tuple[ConversionItem, ...],
) -> str:
    source_map, basename_map = _destination_maps(items)
    project_basename_map = _project_reference_basename_map(project_root=project_root, source_path=source_path)

    def replace(match: re.Match[str]) -> str:
        value = match.group(1).strip()
        replacement = _replacement_for_path_token(
            value,
            project_root=project_root,
            source_path=source_path,
            source_map=source_map,
            basename_map=basename_map,
            project_basename_map=project_basename_map,
        )
        if replacement is None:
            return match.group(0)
        return f"`{replacement}`"

    return PATH_TOKEN_PATTERN.sub(replace, text)


def _destination_maps(items: tuple[ConversionItem, ...]) -> tuple[dict[str, str], dict[str, str]]:
    source_to_destination: dict[str, str] = {}
    basename_to_destinations: dict[str, set[str]] = {}
    for item in items:
        if item.destination is None or item.source == "(generated)":
            continue
        source_to_destination[item.source] = item.destination
        source_to_destination[f"./{item.source}"] = item.destination
        basename_to_destinations.setdefault(Path(item.source).name, set()).add(item.destination)
    basename_to_destination = {
        basename: next(iter(destinations))
        for basename, destinations in basename_to_destinations.items()
        if len(destinations) == 1
    }
    return source_to_destination, basename_to_destination


def _project_reference_basename_map(*, project_root: Path, source_path: Path) -> dict[str, str]:
    by_basename: dict[str, set[str]] = {}
    for path in sorted(source_path.rglob("*")):
        if not path.is_file() or path.suffix not in TEXT_SUFFIXES:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for raw_value in PATH_TOKEN_PATTERN.findall(text):
            value = raw_value.strip()
            source_file = Path(value).expanduser()
            if not source_file.is_absolute():
                continue
            relative = _relative_to(source_file, project_root)
            if relative is None or not source_file.exists():
                continue
            by_basename.setdefault(source_file.name, set()).add(relative.as_posix())
    return {
        basename: next(iter(paths))
        for basename, paths in by_basename.items()
        if len(paths) == 1
    }


def _replacement_for_path_token(
    value: str,
    *,
    project_root: Path,
    source_path: Path,
    source_map: dict[str, str],
    basename_map: dict[str, str],
    project_basename_map: dict[str, str],
) -> str | None:
    if not _looks_like_convertible_path_token(value):
        return None
    normalized = value[2:] if value.startswith("./") else value
    if normalized in source_map:
        return source_map[normalized]
    if value in source_map:
        return source_map[value]

    token_path = Path(value).expanduser()
    if token_path.is_absolute():
        project_relative = _relative_to(token_path, project_root)
        if project_relative is not None and token_path.exists():
            return project_relative.as_posix()
        source_relative = _relative_to(token_path, source_path)
        if source_relative is not None:
            source_key = source_relative.as_posix()
            if source_key in source_map:
                return source_map[source_key]
        return None

    if any(char.isspace() for char in value):
        return None
    if normalized in source_map:
        return source_map[normalized]
    basename = Path(normalized).name
    if normalized == basename and basename in basename_map:
        return basename_map[basename]
    if normalized == basename and basename in project_basename_map:
        return project_basename_map[basename]
    return None


def _copy_referenced_project_files_for_preview(plan: ConversionPlan, package_root: Path, temp_project: Path) -> None:
    copied: set[str] = set()
    for path in sorted(package_root.rglob("*")):
        if not path.is_file() or path.suffix not in {".md", ".toml"}:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for raw_value in PATH_TOKEN_PATTERN.findall(text):
            value = raw_value.strip()
            if not _looks_like_convertible_path_token(value):
                continue
            target = Path(value)
            if target.is_absolute() or value.startswith("~") or ".." in target.parts:
                continue
            if (package_root / target).exists() or (temp_project / target).exists():
                continue
            source = plan.project_root / target
            if not source.exists():
                continue
            destination = temp_project / target
            if source.is_dir():
                destination.mkdir(parents=True, exist_ok=True)
                continue
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
            copied.add(target.as_posix())
    if copied:
        (temp_project / ".governed" / ".conversion-preview-files").write_text(
            "\n".join(sorted(copied)) + "\n",
            encoding="utf-8",
        )


def _relative_to(path: Path, root: Path) -> Path | None:
    try:
        return path.resolve().relative_to(root.resolve())
    except ValueError:
        return None


def _looks_like_convertible_path_token(value: str) -> bool:
    if not value or "\n" in value or "|" in value:
        return False
    if value.startswith(("http://", "https://")):
        return False
    token_path = Path(value).expanduser()
    if token_path.is_absolute() or value.startswith("~") or value.startswith("."):
        return True
    if "/" in value:
        return True
    return token_path.suffix in {".md", ".toml", ".json", ".yaml", ".yml", ".py", ".sh"}


def _initialize_prompt(plan: ConversionPlan) -> str:
    return f"""# Initialize {plan.capability_name}

Review the converted package for `{plan.capability_id}`.

- Confirm converted instructions are reusable and governed.
- Keep unsafe or local-only source content out of governed memory.
- Use `docs/conversion-report.md` as the conversion audit trail.
"""


def _tools_readme(plan: ConversionPlan) -> str:
    copied_tools = [item.destination for item in plan.planned_items if item.destination and item.destination.startswith("tools/")]
    lines = [
        "# Converted Helper Tools",
        "",
        "These helper files were copied from a local Codex skill for review.",
        "",
        "## Safety",
        "",
        "- GovKB conversion does not execute helper tools.",
        "- Review scripts before running them.",
        "- Prefer dry-run or preview modes for mutating helpers.",
        "",
        "## Files",
        "",
    ]
    lines.extend(f"- `{item}`" for item in sorted(set(copied_tools)) if item != "tools/README.md")
    return "\n".join(lines).rstrip() + "\n"


def _conversion_report(plan: ConversionPlan) -> str:
    lines = [
        f"# Conversion Report - {plan.capability_name}",
        "",
        f"- Source adapter: codex",
        f"- Source skill: {plan.source_name}",
        f"- Capability id: {plan.capability_id}",
        f"- Parity level: {plan.parity_level}",
        f"- Strict validation status: {plan.strict_status}",
        "",
        "## Rejected Items",
        "",
    ]
    if plan.rejected_items:
        lines.extend(f"- {item.source}: {item.reason}" for item in plan.rejected_items)
    else:
        lines.append("- None")
    lines.extend(["", "## Manual Review Items", ""])
    if plan.manual_review_items:
        lines.extend(f"- {item.source}: {item.reason}" for item in plan.manual_review_items)
    else:
        lines.append("- None")
    lines.extend(["", "## Planned Items", ""])
    lines.extend(
        f"- `{item.destination}` from source item {item.source} ({item.action})"
        for item in plan.planned_items
        if item.destination
    )
    return "\n".join(lines).rstrip() + "\n"
