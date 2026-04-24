"""Contract-driven KB bootstrap and health helpers."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import re
import tomllib

from govkb.core.contracts import CapabilityContract
from govkb.core.contracts import ProjectBundle
from govkb.core.contracts import ValidationMessage


GENERIC_TOKENS = {
    "agreement",
    "candidate",
    "capability",
    "code",
    "commands",
    "docs",
    "documentation",
    "governed",
    "kb",
    "knowledge",
    "local",
    "map",
    "notes",
    "project",
    "repo",
    "review",
    "rules",
    "signals",
    "stable",
    "steward",
    "verification",
    "workflow",
    "workflows",
}

INTERESTING_FILENAMES = {
    "README.md",
    "README.txt",
    "README.rst",
    "package.json",
    "pyproject.toml",
    "Makefile",
    "justfile",
    "docker-compose.yml",
    "docker-compose.yaml",
    "compose.yml",
    "compose.yaml",
}
INTERESTING_SUFFIXES = {".md", ".sln", ".csproj", ".yml", ".yaml", ".json", ".toml"}
INTERESTING_DIRS = {"app", "apps", "backend", "docs", "doc", "e2e", "frontend", "scripts", "services", "src", "test", "tests"}
NOISY_PATH_PARTS = {
    ".git",
    ".hg",
    ".pytest_cache",
    ".ruff_cache",
    ".svn",
    ".tox",
    ".venv",
    "__pycache__",
    "bin",
    "build",
    "coverage",
    "dist",
    "node_modules",
    "obj",
    "out",
    "venv",
}
DOC_CONTEXT_PARTS = {"adr", "adrs", "architecture", "decision-records", "design"}
PLACEHOLDER_PATTERNS = (
    re.compile(r"^- TODO:", re.I),
    re.compile(r"^- Use this section", re.I),
    re.compile(r"^- Add .+ here", re.I),
)
COMMAND_FACT_PATTERN = re.compile(
    r"`[^`]+`|\b(dotnet test|npm (?:run|--prefix)|pnpm |yarn |make |just |cargo test|go test|python3? -m (?:pytest|unittest))\b",
    re.I,
)


@dataclass(frozen=True)
class KBBootstrapResult:
    """Result of one capability KB bootstrap pass."""

    capability_id: str
    memory_path: Path
    added_facts: tuple[str, ...]
    evidence_paths: tuple[Path, ...]
    warnings: tuple[str, ...]

    @property
    def updated(self) -> bool:
        return bool(self.added_facts)


def _tokenize(value: str) -> tuple[str, ...]:
    return tuple(re.findall(r"[A-Za-z][A-Za-z0-9]*", value.lower()))


def _capability_tokens(contract: CapabilityContract) -> tuple[str, ...]:
    ordered: list[str] = []
    seen: set[str] = set()
    for value in (contract.capability_id, *contract.aliases, *contract.hints):
        for token in _tokenize(value):
            if len(token) < 3 or token in GENERIC_TOKENS:
                continue
            if token in seen:
                continue
            ordered.append(token)
            seen.add(token)
    return tuple(ordered)


def _relpath(project_root: Path, path: Path) -> str:
    try:
        relative = path.relative_to(project_root)
    except ValueError:
        return path.as_posix()
    text = relative.as_posix()
    return text or "."


def _context_parts(project_root: Path, path: Path) -> tuple[str, ...]:
    try:
        parts = path.relative_to(project_root).parts
    except ValueError:
        parts = path.parts
    return tuple(part.lower() for part in parts)


def _has_noisy_context(project_root: Path, path: Path) -> bool:
    for part in _context_parts(project_root, path):
        if part == ".":
            continue
        if part.startswith("."):
            return True
        if part in NOISY_PATH_PARTS:
            return True
    return False


def _has_doc_context(project_root: Path, path: Path) -> bool:
    return any(part in DOC_CONTEXT_PARTS for part in _context_parts(project_root, path))


def _command_prefix_for_dir(project_root: Path, parent: Path, *, package_manager: str) -> str:
    relative_parent = _relpath(project_root, parent)
    if relative_parent == ".":
        return package_manager
    if package_manager == "npm":
        return f"npm --prefix {relative_parent}"
    if package_manager == "pnpm":
        return f"pnpm --dir {relative_parent}"
    if package_manager == "yarn":
        return f"yarn --cwd {relative_parent}"
    return package_manager


def _is_placeholder_bullet(text: str) -> bool:
    stripped = text.strip()
    return any(pattern.search(stripped) for pattern in PLACEHOLDER_PATTERNS)


def _looks_like_command_fact(text: str) -> bool:
    return bool(COMMAND_FACT_PATTERN.search(text))


def _section_aliases(contract: CapabilityContract) -> dict[str, str]:
    available = {section for target in contract.targets for section in target.sections}

    def resolve(*preferred: str) -> str | None:
        for name in preferred:
            if name in available:
                return name
        return None

    mapping: dict[str, str] = {}
    pairs = {
        "working": ("Working Agreement", "Project Working Agreement"),
        "workflows": ("Stable Workflows", "Stable Patterns"),
        "commands": ("Commands And Verification", "Verification Notes"),
        "repo_map": ("Code And Docs Map", "Repo Conventions"),
        "authority": ("Authority Rules",),
        "candidate_signals": ("Candidate Skill Signals",),
    }
    for key, names in pairs.items():
        section = resolve(*names)
        if section is not None:
            mapping[key] = section
    return mapping


def _parse_markdown_sections(text: str) -> tuple[str | None, list[str], list[str], dict[str, list[str]]]:
    title: str | None = None
    preamble: list[str] = []
    order: list[str] = []
    sections: dict[str, list[str]] = {}
    current: str | None = None
    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        if title is None and line.startswith("# "):
            title = line[2:].strip()
            continue
        if line.startswith("## "):
            current = line[3:].strip()
            if current not in sections:
                order.append(current)
                sections[current] = []
            continue
        if current is None:
            preamble.append(line)
        else:
            sections[current].append(line)
    return title, preamble, order, sections


def _section_real_facts(lines: list[str]) -> tuple[str, ...]:
    facts: list[str] = []
    for line in lines:
        stripped = line.strip()
        if not stripped.startswith("- "):
            continue
        bullet = stripped[2:].strip()
        if not bullet or _is_placeholder_bullet(stripped):
            continue
        facts.append(bullet)
    return tuple(facts)


def _read_candidate_facts(candidate_root: Path | None) -> tuple[tuple[str, str], ...]:
    if candidate_root is None:
        return ()
    facts_path = candidate_root / "candidate-facts.toml"
    if not facts_path.is_file():
        return ()
    try:
        data = tomllib.loads(facts_path.read_text(encoding="utf-8"))
    except tomllib.TOMLDecodeError:
        return ()
    facts: list[tuple[str, str]] = []
    for row in data.get("facts", ()):
        if not isinstance(row, dict):
            continue
        fact = row.get("fact")
        section = row.get("section")
        confidence = row.get("confidence")
        if not isinstance(fact, str) or not fact.strip():
            continue
        if not isinstance(section, str) or not section.strip():
            continue
        if isinstance(confidence, (int, float)) and float(confidence) < 0.70:
            continue
        facts.append((section.strip(), fact.strip()))
    return tuple(facts)


def _repo_roots(project_root: Path, contract: CapabilityContract) -> tuple[Path, ...]:
    roots: list[Path] = []
    for item in contract.bootstrap.repo_roots:
        root = (project_root / item).resolve()
        if root.exists():
            roots.append(root)
    return tuple(dict.fromkeys(roots))


def _explicit_paths(project_root: Path, contract: CapabilityContract) -> tuple[Path, ...]:
    paths: list[Path] = []
    for item in (*contract.bootstrap.authority_paths, *contract.bootstrap.seed_paths):
        path = (project_root / item).resolve()
        if path.exists():
            paths.append(path)
    return tuple(dict.fromkeys(paths))


def _interesting_candidate_paths(project_root: Path, contract: CapabilityContract) -> tuple[Path, ...]:
    tokens = set(_capability_tokens(contract))
    candidates: dict[Path, int] = {}
    roots = _repo_roots(project_root, contract)
    explicit = set(_explicit_paths(project_root, contract))

    for path in explicit:
        candidates[path] = 500 if _relpath(project_root, path) in contract.bootstrap.authority_paths else 400

    for root in roots:
        if not root.exists():
            continue
        if root.is_file():
            candidates.setdefault(root, 250)
            continue
        for path in root.rglob("*"):
            try:
                relative_parts = path.relative_to(root).parts
            except ValueError:
                continue
            if len(relative_parts) > 4:
                continue
            if ".governed" in relative_parts:
                continue
            if _has_noisy_context(root, path):
                continue
            if _has_doc_context(root, path):
                continue
            name = path.name
            lower_name = name.lower()
            if path.is_dir():
                if lower_name not in INTERESTING_DIRS and not tokens.intersection(part.lower() for part in path.parts):
                    continue
            else:
                if name not in INTERESTING_FILENAMES and path.suffix not in INTERESTING_SUFFIXES:
                    continue
                if path.suffix in {".md", ".rst", ".txt"} and not lower_name.startswith("readme."):
                    continue
            score = 0
            if tokens:
                matches = sum(1 for part in path.parts if any(token in part.lower() for token in tokens))
                score += matches * 40
            if path.is_dir():
                score += 40 if lower_name in INTERESTING_DIRS else 10
            else:
                score += 30
                if name in INTERESTING_FILENAMES:
                    score += 50
                if path.suffix == ".sln":
                    score += 120
                elif path.suffix == ".csproj":
                    score += 120 if "test" in path.stem.lower() else 40
                if lower_name.endswith((".md", ".rst", ".txt")):
                    score += 20
            if score:
                current = candidates.get(path)
                candidates[path] = score if current is None else max(current, score)

    ordered = sorted(candidates.items(), key=lambda item: (-item[1], _relpath(project_root, item[0])))
    return tuple(path for path, _ in ordered[:12])


def _facts_from_directory(project_root: Path, path: Path, section_aliases: dict[str, str]) -> tuple[tuple[str, str], ...]:
    relative = _relpath(project_root, path)
    lower_name = path.name.lower()
    facts: list[tuple[str, str]] = []
    repo_map_section = section_aliases.get("repo_map")
    commands_section = section_aliases.get("commands")
    if repo_map_section is not None:
        if lower_name in {"docs", "doc"}:
            facts.append((repo_map_section, f"Project docs for this capability live under `{relative}/`."))
        elif lower_name in {"src", "backend", "frontend", "services", "app", "apps"}:
            facts.append((repo_map_section, f"Relevant source code for this capability lives under `{relative}/`."))
        elif lower_name in {"test", "tests", "e2e"}:
            facts.append((repo_map_section, f"Automated tests for this capability live under `{relative}/`."))
    if commands_section is not None and lower_name == "scripts":
        facts.append((commands_section, f"Reusable project scripts for this capability live under `{relative}/`."))
    return tuple(facts)


def _facts_from_package_json(project_root: Path, path: Path, section_aliases: dict[str, str]) -> tuple[tuple[str, str], ...]:
    facts: list[tuple[str, str]] = []
    repo_map_section = section_aliases.get("repo_map")
    commands_section = section_aliases.get("commands")
    relative = _relpath(project_root, path)
    if repo_map_section is not None:
        parent_rel = _relpath(project_root, path.parent)
        if parent_rel == ".":
            facts.append((repo_map_section, f"Node workspace entrypoint for this capability is `{relative}`."))
        else:
            facts.append((repo_map_section, f"Node workspace for this capability is rooted at `{parent_rel}/` with scripts in `{relative}`."))
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return tuple(facts)
    scripts = data.get("scripts")
    if not isinstance(scripts, dict) or commands_section is None:
        return tuple(facts)
    prefix = _command_prefix_for_dir(project_root, path.parent, package_manager="npm")
    for script_name in ("test", "e2e", "lint", "build", "dev", "start"):
        if script_name not in scripts:
            continue
        facts.append((commands_section, f"Use `{prefix} run {script_name}` for the `{script_name}` workflow in `{relative}`."))
    return tuple(facts)


def _facts_from_makefile(project_root: Path, path: Path, section_aliases: dict[str, str]) -> tuple[tuple[str, str], ...]:
    commands_section = section_aliases.get("commands")
    if commands_section is None:
        return ()
    relative_dir = _relpath(project_root, path.parent)
    if path.name.lower() == "justfile":
        prefix = "just" if relative_dir == "." else f"just --justfile { _relpath(project_root, path) }"
    else:
        prefix = "make" if relative_dir == "." else f"make -C {relative_dir}"
    targets: list[str] = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        match = re.match(r"^([A-Za-z0-9_.-]+):", line)
        if not match:
            continue
        target = match.group(1)
        if target in {"test", "check", "lint", "dev", "run", "up"} and target not in targets:
            targets.append(target)
    return tuple((commands_section, f"Use `{prefix} {target}` from `{_relpath(project_root, path)}`.") for target in targets)


def _facts_from_pyproject(project_root: Path, path: Path, section_aliases: dict[str, str]) -> tuple[tuple[str, str], ...]:
    facts: list[tuple[str, str]] = []
    repo_map_section = section_aliases.get("repo_map")
    commands_section = section_aliases.get("commands")
    relative = _relpath(project_root, path)
    if repo_map_section is not None:
        facts.append((repo_map_section, f"Python project metadata for this capability is defined in `{relative}`."))
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError):
        return tuple(facts)
    tests_dir = path.parent / "tests"
    uses_pytest = "tool" in data and isinstance(data.get("tool"), dict) and "pytest" in data["tool"]
    if commands_section is not None and tests_dir.is_dir() and uses_pytest:
        facts.append((commands_section, f"Use `python3 -m pytest { _relpath(project_root, tests_dir) }` for Python test verification."))
    return tuple(facts)


def _facts_from_dotnet(project_root: Path, path: Path, section_aliases: dict[str, str], *, search_root: Path) -> tuple[tuple[str, str], ...]:
    facts: list[tuple[str, str]] = []
    repo_map_section = section_aliases.get("repo_map")
    commands_section = section_aliases.get("commands")
    workflows_section = section_aliases.get("workflows")
    relative = _relpath(project_root, path)
    if repo_map_section is not None and path.suffix == ".sln":
        facts.append((repo_map_section, f"Dotnet solution entrypoint for this capability is `{relative}`."))
    if path.suffix == ".csproj" and repo_map_section is not None and "test" not in path.stem.lower():
        facts.append((repo_map_section, f"Relevant dotnet project file for this capability is `{relative}`."))
    if path.suffix == ".csproj" and "test" in path.stem.lower():
        if workflows_section is not None:
            facts.append((workflows_section, f"Primary .NET verification workflow for this capability runs through `{relative}`."))
        if commands_section is not None:
            facts.append((commands_section, f"Use `dotnet test {relative} --no-restore` for targeted verification."))
        return tuple(facts)
    if commands_section is None:
        return tuple(facts)
    if path.suffix == ".sln":
        test_projects = sorted(search_root.rglob("*.csproj"))
        for project in test_projects:
            if "test" not in project.stem.lower():
                continue
            facts.append((commands_section, f"Use `dotnet test {_relpath(project_root, project)} --no-restore` for targeted verification."))
            break
    return tuple(facts)


def _facts_from_compose(project_root: Path, path: Path, section_aliases: dict[str, str], authority_paths: tuple[str, ...]) -> tuple[tuple[str, str], ...]:
    if _has_noisy_context(project_root, path) or _has_doc_context(project_root, path.parent):
        return ()
    facts: list[tuple[str, str]] = []
    relative = _relpath(project_root, path)
    workflows_section = section_aliases.get("workflows")
    authority_section = section_aliases.get("authority")
    if workflows_section is not None:
        facts.append((workflows_section, f"Local stack wiring for this capability is defined in `{relative}`."))
    if authority_section is not None and relative in authority_paths:
        facts.append((authority_section, f"Treat `{relative}` as authoritative for effective local stack wiring and ports."))
    return tuple(facts)


def _facts_from_readme(project_root: Path, path: Path, section_aliases: dict[str, str]) -> tuple[tuple[str, str], ...]:
    if _has_noisy_context(project_root, path):
        return ()
    repo_map_section = section_aliases.get("repo_map")
    if repo_map_section is None:
        return ()
    lower_name = path.name.lower()
    if not lower_name.startswith("readme."):
        return ()
    return ((repo_map_section, f"Setup and reference notes for this capability start in `{_relpath(project_root, path)}`."),)


def _facts_from_path(
    project_root: Path,
    path: Path,
    contract: CapabilityContract,
    section_aliases: dict[str, str],
    *,
    search_root: Path,
) -> tuple[tuple[str, str], ...]:
    if _has_noisy_context(project_root, path):
        return ()
    if path.is_dir():
        return _facts_from_directory(project_root, path, section_aliases)
    lower_name = path.name.lower()
    if path.name in {"README.md", "README.txt", "README.rst"} or lower_name.endswith((".md", ".rst")):
        return _facts_from_readme(project_root, path, section_aliases)
    if lower_name == "package.json":
        return _facts_from_package_json(project_root, path, section_aliases)
    if lower_name == "pyproject.toml":
        return _facts_from_pyproject(project_root, path, section_aliases)
    if lower_name in {"makefile", "justfile"}:
        return _facts_from_makefile(project_root, path, section_aliases)
    if path.suffix in {".sln", ".csproj"}:
        return _facts_from_dotnet(project_root, path, section_aliases, search_root=search_root)
    if lower_name in {"docker-compose.yml", "docker-compose.yaml", "compose.yml", "compose.yaml"}:
        return _facts_from_compose(project_root, path, section_aliases, contract.bootstrap.authority_paths)
    return ()


def _write_memory(path: Path, contract: CapabilityContract, facts_by_section: dict[str, list[str]]) -> tuple[str, ...]:
    title, preamble, order, sections = _parse_markdown_sections(path.read_text(encoding="utf-8"))
    desired_order = list(dict.fromkeys([*(contract.targets[0].sections if contract.targets else ()), *order]))
    added: list[str] = []

    for section_name in desired_order:
        section_lines = sections.setdefault(section_name, [])
        existing_real = set(_section_real_facts(section_lines))
        new_facts = [fact for fact in facts_by_section.get(section_name, []) if fact not in existing_real]
        if not new_facts:
            continue
        placeholder_only = not existing_real and any(line.strip().startswith("- ") for line in section_lines)
        if placeholder_only:
            section_lines = [line for line in section_lines if not _is_placeholder_bullet(line.strip())]
        updated_lines = list(section_lines)
        if updated_lines and updated_lines[-1].strip():
            updated_lines.append("")
        for fact in new_facts:
            updated_lines.append(f"- {fact}")
            added.append(f"{section_name}: {fact}")
        sections[section_name] = updated_lines

    lines: list[str] = []
    if title:
        lines.append(f"# {title}")
        lines.append("")
    preamble_copy = list(preamble)
    while preamble_copy and not preamble_copy[-1].strip():
        preamble_copy.pop()
    if preamble_copy:
        lines.extend(preamble_copy)
        lines.append("")
    for section_name in desired_order:
        lines.append(f"## {section_name}")
        lines.append("")
        section_lines = sections.get(section_name, [])
        while section_lines and not section_lines[-1].strip():
            section_lines.pop()
        if section_lines:
            lines.extend(section_lines)
        lines.append("")
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return tuple(added)


def bootstrap_capability(
    project_root: Path,
    contract: CapabilityContract,
    *,
    candidate_root: Path | None = None,
) -> KBBootstrapResult:
    """Bootstrap one capability KB from candidate facts and repo facts."""
    if not contract.targets:
        raise ValueError(f"capability has no memory target: {contract.capability_id}")
    memory_path = contract.capability_root / contract.targets[0].path
    if not memory_path.is_file():
        raise FileNotFoundError(f"memory target not found: {memory_path}")

    section_aliases = _section_aliases(contract)
    facts_by_section: dict[str, list[str]] = {}
    evidence_paths: list[Path] = []

    for section_name, fact in _read_candidate_facts(candidate_root):
        if section_name not in contract.targets[0].sections:
            continue
        facts_by_section.setdefault(section_name, [])
        if fact not in facts_by_section[section_name]:
            facts_by_section[section_name].append(fact)
    if candidate_root is not None:
        facts_path = candidate_root / "candidate-facts.toml"
        if facts_path.is_file():
            evidence_paths.append(facts_path)

    paths = _interesting_candidate_paths(project_root, contract)
    roots = _repo_roots(project_root, contract)
    search_root = roots[0] if roots and roots[0].is_dir() else project_root
    for path in paths:
        facts = _facts_from_path(project_root, path, contract, section_aliases, search_root=search_root)
        if not facts:
            continue
        if path not in evidence_paths:
            evidence_paths.append(path)
        for section_name, fact in facts:
            if section_name not in contract.targets[0].sections:
                continue
            facts_by_section.setdefault(section_name, [])
            if fact not in facts_by_section[section_name]:
                facts_by_section[section_name].append(fact)

    added = _write_memory(memory_path, contract, facts_by_section)
    warnings = capability_kb_health_warnings(project_root, contract)
    return KBBootstrapResult(
        capability_id=contract.capability_id,
        memory_path=memory_path,
        added_facts=added,
        evidence_paths=tuple(evidence_paths),
        warnings=tuple(warnings),
    )


def capability_kb_health_warnings(project_root: Path, contract: CapabilityContract) -> tuple[str, ...]:
    """Return thin-KB warnings for one capability."""
    if not contract.targets:
        return ("no memory target configured",)
    memory_path = contract.capability_root / contract.targets[0].path
    if not memory_path.is_file():
        return (f"memory target missing: {_relpath(project_root, memory_path)}",)
    _, _, _, sections = _parse_markdown_sections(memory_path.read_text(encoding="utf-8"))
    real_entries = {section: _section_real_facts(lines) for section, lines in sections.items()}
    warnings: list[str] = []

    total_real = sum(len(entries) for entries in real_entries.values())
    if total_real <= 1:
        warnings.append("KB is still scaffold-thin")

    for section in contract.kb_health.required_sections:
        if not real_entries.get(section):
            warnings.append(f"missing durable entries in section `{section}`")

    if contract.kb_health.requires_verification_commands:
        command_entries = real_entries.get("Commands And Verification") or real_entries.get("Verification Notes") or ()
        if not any(_looks_like_command_fact(item) for item in command_entries):
            warnings.append("missing verification command")

    if contract.kb_health.requires_repo_map:
        repo_map_entries = real_entries.get("Code And Docs Map") or real_entries.get("Repo Conventions") or ()
        if not repo_map_entries:
            warnings.append("missing repo map fact")

    return tuple(dict.fromkeys(warnings))


def bundle_kb_health_messages(project_root: Path, bundle: ProjectBundle) -> tuple[ValidationMessage, ...]:
    """Convert thin-KB warnings into validation-style messages."""
    messages: list[ValidationMessage] = []
    for contract in bundle.capabilities.values():
        for warning in capability_kb_health_warnings(project_root, contract):
            messages.append(
                ValidationMessage(
                    location=str(contract.capability_root / contract.targets[0].path),
                    message=f"{contract.capability_id}: {warning}",
                )
            )
    return tuple(messages)
