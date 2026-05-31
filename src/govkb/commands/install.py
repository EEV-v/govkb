"""Project install command."""

from __future__ import annotations

import os
import sys
from pathlib import Path
import shlex
import subprocess

import govkb

from govkb.adapters.codex.materialize import apply_codex_materialization
from govkb.adapters.codex.materialize import preview_codex_materialization
from govkb.core.contracts import load_project_bundle
from govkb.core.ids import normalize_identifier
from govkb.core.install_state import default_codex_home
from govkb.core.templates import copy_project_template


DEFAULT_CRON_SCHEDULE = "15 8 * * *"


def _ensure_governed(project_root: Path, project_id: str | None, project_name: str | None, preview: bool) -> int:
    governed_root = project_root / ".governed"
    if governed_root.exists():
        print(f"Found existing {governed_root}")
        return 0
    resolved_name = project_name or project_root.name
    resolved_id = project_id or normalize_identifier(resolved_name)
    print(f"Will scaffold {governed_root}")
    print(f"Project id: {resolved_id}")
    if preview:
        return 0
    copy_project_template(
        project_root,
        {
            "__PROJECT_ID__": resolved_id,
            "__PROJECT_NAME__": resolved_name,
        },
    )
    print(f"Scaffolded {governed_root}")
    return 0


def _is_env_assignment(token: str) -> bool:
    key, separator, _ = token.partition("=")
    if not separator or not key:
        return False
    first = key[0]
    if not (first == "_" or "A" <= first <= "Z" or "a" <= first <= "z"):
        return False
    return all(
        char == "_" or "A" <= char <= "Z" or "a" <= char <= "z" or "0" <= char <= "9"
        for char in key
    )


def _cron_settings_from_line(line: str) -> tuple[str | None, dict[str, str]]:
    try:
        parts = shlex.split(line)
    except ValueError:
        return None, {}
    if len(parts) < 6:
        return None, {}

    env: dict[str, str] = {}
    for token in parts[5:]:
        if not _is_env_assignment(token):
            break
        key, value = token.split("=", 1)
        env[key] = value
    return " ".join(parts[:5]), env


def _managed_cron_lines(project_root: Path, current: str) -> list[str]:
    managed_marker = f"--project-root {project_root}"
    return [entry for entry in current.splitlines() if entry.strip() and managed_marker in entry]


def _read_project_cron_settings(project_root: Path) -> tuple[str | None, dict[str, str]]:
    existing = subprocess.run(["crontab", "-l"], text=True, capture_output=True, check=False)
    current = existing.stdout if existing.returncode == 0 else ""
    managed_lines = _managed_cron_lines(project_root, current)
    if not managed_lines:
        return None, {}
    return _cron_settings_from_line(managed_lines[-1])


def _cron_line(project_root: Path, codex_home: Path, schedule: str, inherited_env: dict[str, str] | None = None) -> str:
    script = codex_home / "bin" / "codex-memory-review"
    project_id = _project_id(project_root)
    log_path = codex_home / "memories" / "govkb" / "projects" / project_id / "codex-memory-review" / "cron.log"
    env = dict(inherited_env or {})
    env["CODEX_HOME"] = str(codex_home)
    env_parts = [f"CODEX_HOME={shlex.quote(str(codex_home))}"]
    env_parts.extend(f"{key}={shlex.quote(value)}" for key, value in env.items() if key != "CODEX_HOME")
    return (
        f"{schedule} "
        f"{' '.join(env_parts)} "
        f"{shlex.quote(str(script))} --once --project-root {shlex.quote(str(project_root))} "
        f">> {shlex.quote(str(log_path))} 2>&1"
    )


def _project_id(project_root: Path) -> str:
    bundle, _ = load_project_bundle(project_root)
    return normalize_identifier(bundle.project_id or project_root.name)


def _packaged_memory_review_script() -> Path:
    package_root = Path(next(iter(govkb.__path__))).resolve()
    return package_root / "adapters" / "codex" / "bin" / "codex-memory-review"


def _render_installed_memory_review_script(source_text: str, codex_home: Path) -> str:
    pinned_home = str(codex_home.resolve())
    injection = f'import os\n\nos.environ["CODEX_HOME"] = {pinned_home!r}\n'
    anchor = "import os\n"
    if anchor not in source_text:
        raise ValueError("packaged Codex memory-review task is missing `import os` anchor")
    return source_text.replace(anchor, injection, 1)


def _install_memory_review_script(codex_home: Path, preview: bool) -> int:
    source = _packaged_memory_review_script()
    target = codex_home / "bin" / "codex-memory-review"
    if not source.is_file():
        print(f"error: packaged Codex memory-review task not found: {source}", file=sys.stderr)
        return 1

    target_exists = target.is_file()
    current_text = target.read_text(encoding="utf-8", errors="replace") if target_exists else None
    source_text = source.read_text(encoding="utf-8")
    target_text = _render_installed_memory_review_script(source_text, codex_home)
    if current_text == target_text:
        print(f"Memory review task: current at {target}")
        return 0

    action = "refresh" if target_exists else "install"
    print(f"Memory review task: will {action} {target}")
    if preview:
        return 0

    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(target_text, encoding="utf-8")
    target.chmod(0o755)
    print(f"Memory review task: {action}ed {target}")
    return 0


def _resolve_install_codex_home(args, project_root: Path) -> Path:
    if args.codex_home:
        return Path(args.codex_home).expanduser().resolve()
    if os.environ.get("CODEX_HOME"):
        return default_codex_home()
    if getattr(args, "cron", False):
        _, existing_env = _read_project_cron_settings(project_root)
        existing_codex_home = existing_env.get("CODEX_HOME")
        if existing_codex_home:
            return Path(os.path.expandvars(existing_codex_home)).expanduser().resolve()
    return default_codex_home()


def _install_cron(project_root: Path, codex_home: Path, schedule: str | None, preview: bool) -> int:
    existing = subprocess.run(["crontab", "-l"], text=True, capture_output=True, check=False)
    current = existing.stdout if existing.returncode == 0 else ""
    managed_marker = f"--project-root {project_root}"
    current_lines = [entry for entry in current.splitlines() if entry.strip()]
    managed_lines = _managed_cron_lines(project_root, current)
    existing_schedule, existing_env = _cron_settings_from_line(managed_lines[-1]) if managed_lines else (None, {})
    resolved_schedule = schedule or existing_schedule or DEFAULT_CRON_SCHEDULE
    line = _cron_line(project_root, codex_home, resolved_schedule, inherited_env=existing_env)
    if any(entry.strip() == line for entry in managed_lines):
        print("Cron: project-scoped memory-review job already exists")
        return 0
    action = "update" if managed_lines else "add"
    print(f"Cron: will {action} `{line}`")
    if preview:
        return 0
    next_lines = [entry for entry in current_lines if managed_marker not in entry]
    next_lines.append(line)
    next_cron = "\n".join(next_lines).rstrip() + "\n"
    proc = subprocess.run(["crontab", "-"], input=next_cron, text=True, capture_output=True, check=False)
    if proc.returncode != 0:
        print(f"error: failed to update crontab: {proc.stderr.strip()}", file=sys.stderr)
        return 1
    print(f"Cron: {'updated' if managed_lines else 'installed'} project-scoped memory-review job")
    return 0


def run_install(args) -> int:
    """Install governed knowledge support into a project."""
    project_root = Path(args.project_root).resolve()
    codex_home = _resolve_install_codex_home(args, project_root)
    preview = bool(args.preview)

    if not project_root.is_dir():
        print(f"error: project root not found: {project_root}", file=sys.stderr)
        return 1

    print(f"Project root: {project_root}")
    print(f"Codex home: {codex_home}")
    print(f"Mode: {'preview' if preview else 'apply'}")

    script_exit = _install_memory_review_script(codex_home, preview)
    if script_exit != 0:
        return script_exit

    scaffold_exit = _ensure_governed(project_root, args.project_id, args.project_name, preview)
    if scaffold_exit != 0:
        return scaffold_exit

    if preview and not (project_root / ".governed").exists():
        print("Validation: skipped because .governed would be created in apply mode")
        print("Apply: skipped because this is preview")
    else:
        bundle, result = load_project_bundle(project_root)
        for message in result.warnings:
            print(f"warning: {message.location}: {message.message}")
        for message in result.errors:
            print(f"error: {message.location}: {message.message}", file=sys.stderr)
        if result.errors:
            print(f"Validation failed with {len(result.errors)} error(s).", file=sys.stderr)
            return 1
        print(
            f"Validation passed: capabilities={len(bundle.capabilities)} "
            f"adapters={len(bundle.adapters)} releases={len(bundle.releases)}"
        )

        if preview:
            planned = preview_codex_materialization(
                project_root=project_root,
                bundle=bundle,
                codex_home_override=codex_home,
                requested_release=args.release,
                requested_revision=args.revision,
            )
            print(f"Apply preview: {len(planned.capabilities)} Codex skill(s)")
            for item in planned.capabilities:
                print(f"- {item.capability_id} -> {item.materialized_skill_id}: {item.target_path}")
            for warning in planned.warnings:
                print(f"warning: {warning}")
        else:
            applied = apply_codex_materialization(
                project_root=project_root,
                bundle=bundle,
                codex_home_override=codex_home,
                requested_release=args.release,
                requested_revision=args.revision,
            )
            print(f"Applied Codex materialization: {len(applied.capabilities)} skill(s)")
            print(f"Install state: {applied.state_path}")
            for item in applied.capabilities:
                print(f"- {item.capability_id} -> {item.materialized_skill_id}: {item.target_path}")
            for warning in applied.warnings:
                print(f"warning: {warning}")

    if args.cron:
        cron_exit = _install_cron(project_root, codex_home, args.schedule, preview)
        if cron_exit != 0:
            return cron_exit
    else:
        print("Cron: skipped; pass --cron to install the project-scoped memory-review job")

    print("Done.")
    return 0
