"""Governed manifest and contract loading."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
import tomllib

from govkb.core.project import governed_root as build_governed_root
from govkb.core.project import resolve_project_root


@dataclass(frozen=True)
class ValidationMessage:
    """Structured validation message."""

    location: str
    message: str


@dataclass
class ValidationResult:
    """Validation warnings and errors."""

    errors: list[ValidationMessage] = field(default_factory=list)
    warnings: list[ValidationMessage] = field(default_factory=list)

    def add_error(self, location: Path | str, message: str) -> None:
        self.errors.append(ValidationMessage(str(location), message))

    def add_warning(self, location: Path | str, message: str) -> None:
        self.warnings.append(ValidationMessage(str(location), message))


@dataclass(frozen=True)
class CapabilityTarget:
    """Configured capability memory target."""

    name: str
    path: str
    sections: tuple[str, ...]


@dataclass(frozen=True)
class CapabilityContract:
    """Validated capability contract."""

    capability_id: str
    capability_name: str
    governed: bool
    description: str
    aliases: tuple[str, ...]
    hints: tuple[str, ...]
    negative_hints: tuple[str, ...]
    memory_enabled: bool
    auto_apply_min_confidence: float
    requires_explicit_acceptance: bool
    targets: tuple[CapabilityTarget, ...]
    capability_root: Path
    migration_source_adapter: str | None
    migration_source_path: Path | None
    migration_status: str | None
    source_path: Path


@dataclass(frozen=True)
class AdapterManifest:
    """Validated assistant adapter manifest."""

    adapter_id: str
    materialization_targets: tuple[str, ...]
    min_confidence_floor: float
    aliases: tuple[str, ...]
    local_state_key: str
    source_path: Path


@dataclass(frozen=True)
class ReleaseManifest:
    """Validated release manifest."""

    release_id: str
    git_revision: str
    adapters: tuple[str, ...]
    notes: str
    source_path: Path


@dataclass
class ProjectBundle:
    """Loaded governed project bundle."""

    project_root: Path
    governed_root: Path
    project_manifest: dict[str, Any] | None
    capabilities: dict[str, CapabilityContract]
    adapters: dict[str, AdapterManifest]
    releases: dict[str, ReleaseManifest]

    @property
    def project_id(self) -> str | None:
        if not self.project_manifest:
            return None
        project = self.project_manifest.get("project", {})
        return project.get("id")

    @property
    def project_manifest_current_release(self) -> str | None:
        if not self.project_manifest:
            return None
        release = self.project_manifest.get("release", {})
        return release.get("current")

    def release_git_revision(self, release_id: str) -> str | None:
        manifest = self.releases.get(release_id)
        return manifest.git_revision if manifest else None


def _parse_toml_file(path: Path, result: ValidationResult) -> dict[str, Any] | None:
    try:
        return tomllib.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        result.add_error(path, "file not found")
    except tomllib.TOMLDecodeError as exc:
        result.add_error(path, f"invalid TOML: {exc}")
    return None


def _expect_table(data: dict[str, Any], key: str, path: Path, result: ValidationResult) -> dict[str, Any] | None:
    value = data.get(key)
    if not isinstance(value, dict):
        result.add_error(path, f"missing table: {key}")
        return None
    return value


def _expect_string(value: Any, path: Path, result: ValidationResult, label: str) -> str | None:
    if not isinstance(value, str) or not value.strip():
        result.add_error(path, f"missing or invalid string: {label}")
        return None
    return value.strip()


def _expect_bool(value: Any, path: Path, result: ValidationResult, label: str) -> bool | None:
    if not isinstance(value, bool):
        result.add_error(path, f"missing or invalid boolean: {label}")
        return None
    return value


def _expect_int(value: Any, path: Path, result: ValidationResult, label: str) -> int | None:
    if isinstance(value, bool) or not isinstance(value, int):
        result.add_error(path, f"missing or invalid integer: {label}")
        return None
    return value


def _expect_float(value: Any, path: Path, result: ValidationResult, label: str) -> float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        result.add_error(path, f"missing or invalid number: {label}")
        return None
    number = float(value)
    if number < 0 or number > 1:
        result.add_error(path, f"number out of range for {label}: expected 0.0-1.0")
        return None
    return number


def _expect_list_of_strings(value: Any, path: Path, result: ValidationResult, label: str) -> tuple[str, ...]:
    if value is None:
        return ()
    if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
        result.add_error(path, f"missing or invalid string list: {label}")
        return ()
    return tuple(item.strip() for item in value if item.strip())


def _validate_relative_path(path_value: str, path: Path, result: ValidationResult, label: str) -> str | None:
    target_path = Path(path_value)
    if target_path.is_absolute():
        result.add_error(path, f"{label} must be relative")
        return None
    if ".." in target_path.parts:
        result.add_error(path, f"{label} may not contain parent traversal")
        return None
    return path_value


def _load_project_manifest(path: Path, result: ValidationResult) -> dict[str, Any] | None:
    starting_errors = len(result.errors)
    data = _parse_toml_file(path, result)
    if data is None:
        return None
    schema_version = data.get("schema_version")
    if not isinstance(schema_version, int):
        result.add_error(path, "missing or invalid integer: schema_version")
    elif schema_version != 1:
        result.add_warning(path, f"unknown schema_version: {schema_version}")

    project = _expect_table(data, "project", path, result)
    if project is not None:
        _expect_string(project.get("id"), path, result, "project.id")
        _expect_string(project.get("name"), path, result, "project.name")

    release = _expect_table(data, "release", path, result)
    if release is not None:
        _expect_string(release.get("current"), path, result, "release.current")

    adapters = _expect_table(data, "adapters", path, result)
    if adapters is not None:
        _expect_list_of_strings(adapters.get("enabled"), path, result, "adapters.enabled")

    automation = data.get("automation")
    if automation is not None:
        if not isinstance(automation, dict):
            result.add_error(path, "invalid table: automation")
        else:
            if "auto_create_capabilities" in automation:
                _expect_bool(
                    automation.get("auto_create_capabilities"),
                    path,
                    result,
                    "automation.auto_create_capabilities",
                )
            if "auto_create_min_occurrences" in automation:
                occurrences = _expect_int(
                    automation.get("auto_create_min_occurrences"),
                    path,
                    result,
                    "automation.auto_create_min_occurrences",
                )
                if occurrences is not None and occurrences < 2:
                    result.add_error(path, "automation.auto_create_min_occurrences must be >= 2")

    if len(result.errors) > starting_errors:
        return None
    return data


def _load_capability_contract(path: Path, result: ValidationResult) -> CapabilityContract | None:
    starting_errors = len(result.errors)
    data = _parse_toml_file(path, result)
    if data is None:
        return None

    contract_version = data.get("contract_version")
    if not isinstance(contract_version, int):
        result.add_error(path, "missing or invalid integer: contract_version")
    elif contract_version != 1:
        result.add_warning(path, f"unknown contract_version: {contract_version}")

    capability = _expect_table(data, "capability", path, result)
    routing = _expect_table(data, "routing", path, result)
    memory = _expect_table(data, "memory", path, result)
    if capability is None or routing is None or memory is None:
        return None

    capability_id = _expect_string(capability.get("id"), path, result, "capability.id")
    capability_name = _expect_string(capability.get("name"), path, result, "capability.name")
    governed = _expect_bool(capability.get("governed"), path, result, "capability.governed")
    description = _expect_string(capability.get("description"), path, result, "capability.description") or ""
    aliases = _expect_list_of_strings(routing.get("aliases"), path, result, "routing.aliases")
    hints = _expect_list_of_strings(routing.get("hints"), path, result, "routing.hints")
    negative_hints = _expect_list_of_strings(routing.get("negative_hints"), path, result, "routing.negative_hints")

    memory_enabled = _expect_bool(memory.get("enabled"), path, result, "memory.enabled")
    auto_apply = _expect_float(memory.get("auto_apply_min_confidence"), path, result, "memory.auto_apply_min_confidence")
    explicit_acceptance = _expect_bool(
        memory.get("requires_explicit_acceptance"),
        path,
        result,
        "memory.requires_explicit_acceptance",
    )

    target_items: list[CapabilityTarget] = []
    targets = memory.get("targets")
    if memory_enabled:
        if not isinstance(targets, dict) or not targets:
            result.add_error(path, "memory.enabled requires at least one memory target")
        else:
            for name, target in sorted(targets.items()):
                if not isinstance(target, dict):
                    result.add_error(path, f"invalid memory target table: {name}")
                    continue
                target_path = _expect_string(target.get("path"), path, result, f"memory.targets.{name}.path")
                sections = _expect_list_of_strings(target.get("sections"), path, result, f"memory.targets.{name}.sections")
                if target_path is None:
                    continue
                safe_path = _validate_relative_path(target_path, path, result, f"memory.targets.{name}.path")
                if safe_path is None:
                    continue
                if not sections:
                    result.add_error(path, f"memory.targets.{name}.sections must not be empty")
                    continue
                target_items.append(CapabilityTarget(name=name, path=safe_path, sections=sections))

    if capability_id is None or governed is None or memory_enabled is None or auto_apply is None or explicit_acceptance is None:
        return None
    if len(result.errors) > starting_errors:
        return None

    migration = data.get("migration")
    migration_source_adapter: str | None = None
    migration_source_path: Path | None = None
    migration_status: str | None = None
    if migration is not None:
        if not isinstance(migration, dict):
            result.add_error(path, "invalid table: migration")
            return None
        migration_source_adapter = _expect_string(
            migration.get("source_adapter"),
            path,
            result,
            "migration.source_adapter",
        )
        migration_source_path_value = _expect_string(
            migration.get("source_path"),
            path,
            result,
            "migration.source_path",
        )
        migration_status = _expect_string(
            migration.get("status"),
            path,
            result,
            "migration.status",
        )
        if migration_source_path_value is not None:
            migration_source_path = Path(migration_source_path_value).expanduser()
            if not migration_source_path.exists():
                result.add_warning(path, f"migration source path does not exist: {migration_source_path}")
        if len(result.errors) > starting_errors:
            return None

    return CapabilityContract(
        capability_id=capability_id,
        capability_name=capability_name or capability_id,
        governed=governed,
        description=description,
        aliases=aliases,
        hints=hints,
        negative_hints=negative_hints,
        memory_enabled=memory_enabled,
        auto_apply_min_confidence=auto_apply,
        requires_explicit_acceptance=explicit_acceptance,
        targets=tuple(target_items),
        capability_root=path.parent,
        migration_source_adapter=migration_source_adapter,
        migration_source_path=migration_source_path,
        migration_status=migration_status,
        source_path=path,
    )


def _load_adapter_manifest(path: Path, result: ValidationResult) -> AdapterManifest | None:
    starting_errors = len(result.errors)
    data = _parse_toml_file(path, result)
    if data is None:
        return None

    adapter = _expect_table(data, "adapter", path, result)
    governance = _expect_table(data, "governance", path, result)
    routing = _expect_table(data, "routing", path, result)
    if adapter is None or governance is None or routing is None:
        return None

    adapter_id = _expect_string(adapter.get("id"), path, result, "adapter.id")
    local_state_key = _expect_string(adapter.get("local_state_key"), path, result, "adapter.local_state_key")
    materialization_targets = _expect_list_of_strings(
        adapter.get("materialization_targets"),
        path,
        result,
        "adapter.materialization_targets",
    )
    min_confidence_floor = _expect_float(
        governance.get("min_confidence_floor"),
        path,
        result,
        "governance.min_confidence_floor",
    )
    aliases = _expect_list_of_strings(routing.get("aliases"), path, result, "routing.aliases")

    if adapter_id is None or local_state_key is None or min_confidence_floor is None:
        return None
    if len(result.errors) > starting_errors:
        return None

    return AdapterManifest(
        adapter_id=adapter_id,
        materialization_targets=materialization_targets,
        min_confidence_floor=min_confidence_floor,
        aliases=aliases,
        local_state_key=local_state_key,
        source_path=path,
    )


def _load_release_manifest(path: Path, result: ValidationResult) -> ReleaseManifest | None:
    starting_errors = len(result.errors)
    data = _parse_toml_file(path, result)
    if data is None:
        return None

    release = _expect_table(data, "release", path, result)
    if release is None:
        return None

    release_id = _expect_string(release.get("id"), path, result, "release.id")
    git_revision = _expect_string(release.get("git_revision"), path, result, "release.git_revision")
    adapters = _expect_list_of_strings(release.get("adapters"), path, result, "release.adapters")
    notes = _expect_string(release.get("notes"), path, result, "release.notes") or ""

    if release_id is None or git_revision is None:
        return None
    if len(result.errors) > starting_errors:
        return None

    return ReleaseManifest(
        release_id=release_id,
        git_revision=git_revision,
        adapters=adapters,
        notes=notes,
        source_path=path,
    )


def load_project_bundle(project_root: Path) -> tuple[ProjectBundle, ValidationResult]:
    """Load a governed project bundle and collect validation issues."""
    resolved_root = resolve_project_root(project_root)
    root = build_governed_root(resolved_root)
    result = ValidationResult()

    if not root.is_dir():
        result.add_error(root, "missing governed root")
        return ProjectBundle(resolved_root, root, None, {}, {}, {}), result

    project_manifest = _load_project_manifest(root / "project.toml", result)

    capabilities: dict[str, CapabilityContract] = {}
    capability_root = root / "capabilities"
    if capability_root.is_dir():
        for contract_path in sorted(capability_root.glob("*/capability.contract.toml")):
            contract = _load_capability_contract(contract_path, result)
            if contract is None:
                continue
            if contract.capability_id in capabilities:
                result.add_error(contract_path, f"duplicate capability id: {contract.capability_id}")
                continue
            capabilities[contract.capability_id] = contract

    adapters: dict[str, AdapterManifest] = {}
    adapter_root = root / "adapters"
    if adapter_root.is_dir():
        for adapter_path in sorted(adapter_root.glob("*/adapter.toml")):
            manifest = _load_adapter_manifest(adapter_path, result)
            if manifest is None:
                continue
            adapters[manifest.adapter_id] = manifest

    releases: dict[str, ReleaseManifest] = {}
    release_root = root / "releases"
    if release_root.is_dir():
        for release_path in sorted(release_root.glob("*.toml")):
            manifest = _load_release_manifest(release_path, result)
            if manifest is None:
                continue
            releases[manifest.release_id] = manifest

    return ProjectBundle(
        project_root=resolved_root,
        governed_root=root,
        project_manifest=project_manifest,
        capabilities=capabilities,
        adapters=adapters,
        releases=releases,
    ), result
