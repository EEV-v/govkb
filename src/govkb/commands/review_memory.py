"""Memory review command."""

from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys

import govkb

from govkb.core.runtime import govkb_import_root


def _packaged_memory_review_script() -> Path:
    package_root = Path(next(iter(govkb.__path__))).resolve()
    return package_root / "adapters" / "codex" / "bin" / "codex-memory-review"


def _memory_review_command(script: Path) -> list[str]:
    """Run Python memory-review scripts with the active GovKB interpreter."""
    try:
        first_line = script.read_text(encoding="utf-8", errors="replace").splitlines()[0]
    except IndexError:
        first_line = ""
    if "python" in first_line.lower():
        return [sys.executable, str(script)]
    return [str(script)]


def run_review_memory(args) -> int:
    """Run the assistant memory-review adapter."""
    if args.assistant != "codex":
        print(f"error: unsupported assistant: {args.assistant}", file=sys.stderr)
        return 1

    codex_home = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")).expanduser()
    default_script = codex_home / "bin" / "codex-memory-review"
    script = Path(os.environ.get("GOVKB_CODEX_MEMORY_REVIEW", str(default_script))).expanduser()
    if not script.is_file() and "GOVKB_CODEX_MEMORY_REVIEW" not in os.environ:
        script = _packaged_memory_review_script()
    if not script.is_file():
        print(f"error: Codex memory-review task not found: {script}", file=sys.stderr)
        return 1

    project_root = Path(args.project_root).resolve()
    cmd = [*_memory_review_command(script), "--once", "--project-root", str(project_root)]
    if getattr(args, "dry_run", False):
        cmd.append("--dry-run")
    if getattr(args, "lookback_days", None) is not None:
        cmd.extend(["--lookback-days", str(args.lookback_days)])
    if getattr(args, "max_sessions", None) is not None:
        cmd.extend(["--max-sessions", str(args.max_sessions)])
    if getattr(args, "verbose", False):
        cmd.append("--verbose")
    if getattr(args, "codex_timeout", None) is not None:
        cmd.extend(["--codex-timeout", str(args.codex_timeout)])
    if getattr(args, "classifier_codex_home", None):
        cmd.extend(["--classifier-codex-home", str(Path(args.classifier_codex_home).expanduser())])
    if getattr(args, "codex_model", None):
        cmd.extend(["--codex-model", str(args.codex_model)])
    if getattr(args, "codex_reasoning", None):
        cmd.extend(["--codex-reasoning", str(args.codex_reasoning)])
    if getattr(args, "session_file", None):
        cmd.extend(["--session-file", str(Path(args.session_file).expanduser())])
    if not getattr(args, "auto_promote", True):
        cmd.append("--no-auto-promote")

    env = os.environ.copy()
    env["GOVKB_PROJECT_ROOT"] = str(project_root)
    import_root = govkb_import_root()
    env["GOVKB_IMPORT_ROOT"] = str(import_root)
    existing_pythonpath = env.get("PYTHONPATH")
    env["PYTHONPATH"] = str(import_root) if not existing_pythonpath else f"{import_root}{os.pathsep}{existing_pythonpath}"
    proc = subprocess.run(cmd, text=True, env=env, check=False)
    return int(proc.returncode)
