"""Tests for KB bootstrap and thin-KB status reporting."""

from __future__ import annotations

import argparse
from contextlib import redirect_stdout
import io
import os
import tempfile
from pathlib import Path
from unittest.mock import patch
import unittest

from govkb.commands.apply import run_codex_apply
from govkb.commands.create_capability import run_create_capability
from govkb.commands.init import run_init
from govkb.commands.init_kb import run_init_kb
from govkb.commands.status import run_status


def _write_demo_repo_files(project_root: Path) -> None:
    (project_root / "README.md").write_text("# Demo Project\n\nSetup notes.\n", encoding="utf-8")
    (project_root / "docs").mkdir(parents=True, exist_ok=True)
    (project_root / "docs" / "backend.md").write_text("# Backend\n\nWorkflow notes.\n", encoding="utf-8")
    solution_root = project_root / "backend-dotnet"
    tests_root = solution_root / "StoryApp.StoryBook.Tests.Unit"
    adr_root = solution_root / "ADR"
    tests_root.mkdir(parents=True, exist_ok=True)
    adr_root.mkdir(parents=True, exist_ok=True)
    (solution_root / "StoryApp.sln").write_text("Microsoft Visual Studio Solution File\n", encoding="utf-8")
    (tests_root / "StoryApp.StoryBook.Tests.Unit.csproj").write_text(
        "<Project Sdk=\"Microsoft.NET.Sdk\"></Project>\n",
        encoding="utf-8",
    )
    (project_root / "docker-compose.yml").write_text("services:\n  api:\n    image: demo\n", encoding="utf-8")
    (solution_root / "docker-compose.yml").write_text("services:\n  api:\n    image: backend\n", encoding="utf-8")
    (adr_root / "docker-compose.yml").write_text("services:\n  snapshot:\n    image: archived\n", encoding="utf-8")
    (adr_root / "ADR_30_08_2024_Dotnet_Clean_Architecture-20250128190910.md").write_text("# ADR\n", encoding="utf-8")
    for index in range(1, 6):
        (adr_root / f"ADR_{index:02d}.md").write_text(f"# ADR {index}\n", encoding="utf-8")
    pytest_cache = project_root / "e2e" / ".pytest_cache"
    pytest_cache.mkdir(parents=True, exist_ok=True)
    (pytest_cache / "README.md").write_text("cache metadata\n", encoding="utf-8")


def _write_orgchart_like_repo_files(project_root: Path) -> None:
    (project_root / "README.md").write_text("# OrgChart\n\nRun integration tests to verify org chart changes.\n", encoding="utf-8")
    src_root = project_root / "src"
    tests_root = src_root / "tests" / "OrgChart.IntegrationTests"
    api_root = src_root / "OrgChart.API"
    core_root = src_root / "OrgChart.Core"
    infra_root = src_root / "OrgChart.Infrastructure"
    tests_root.mkdir(parents=True, exist_ok=True)
    api_root.mkdir(parents=True, exist_ok=True)
    core_root.mkdir(parents=True, exist_ok=True)
    infra_root.mkdir(parents=True, exist_ok=True)
    (project_root / "OrgChart.sln").write_text("Microsoft Visual Studio Solution File\n", encoding="utf-8")
    (tests_root / "OrgChart.IntegrationTests.csproj").write_text(
        "<Project Sdk=\"Microsoft.NET.Sdk\"></Project>\n",
        encoding="utf-8",
    )
    (api_root / "OrgChart.API.csproj").write_text("<Project Sdk=\"Microsoft.NET.Sdk.Web\"></Project>\n", encoding="utf-8")
    (core_root / "OrgChart.Core.csproj").write_text("<Project Sdk=\"Microsoft.NET.Sdk\"></Project>\n", encoding="utf-8")
    (infra_root / "OrgChart.Infrastructure.csproj").write_text("<Project Sdk=\"Microsoft.NET.Sdk\"></Project>\n", encoding="utf-8")
    (core_root / "Services").mkdir(parents=True, exist_ok=True)


class InitKBCommandTests(unittest.TestCase):
    """Bootstrap behavior for governed capabilities."""

    def test_init_kb_bootstraps_one_capability_from_repo_facts(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir) / "DemoProject"
            codex_home = Path(temp_dir) / "codex-home"
            project_root.mkdir(parents=True, exist_ok=True)
            codex_home.mkdir(parents=True, exist_ok=True)
            run_init(argparse.Namespace(dest=project_root, project_id="demo-project", project_name="Demo Project"))
            _write_demo_repo_files(project_root)
            run_create_capability(
                argparse.Namespace(
                    capability_id="backend-local-stack-workflow",
                    project_root=project_root,
                    from_candidate=None,
                    no_init_kb=False,
                )
            )

            output = io.StringIO()
            with redirect_stdout(output):
                exit_code = run_init_kb(
                    argparse.Namespace(
                        project_root=project_root,
                        capability="backend-local-stack-workflow",
                        all=False,
                        codex_home=codex_home,
                    )
                )

            self.assertEqual(exit_code, 0)
            memory_text = (
                project_root
                / ".governed"
                / "capabilities"
                / "backend-local-stack-workflow"
                / "references"
                / "long-term-memory.md"
            ).read_text(encoding="utf-8")
            self.assertIn("`docker-compose.yml`", memory_text)
            self.assertIn("`backend-dotnet/docker-compose.yml`", memory_text)
            self.assertIn("`dotnet test backend-dotnet/StoryApp.StoryBook.Tests.Unit/StoryApp.StoryBook.Tests.Unit.csproj --no-restore`", memory_text)
            self.assertIn("`README.md`", memory_text)
            self.assertNotIn("`backend-dotnet/ADR/docker-compose.yml`", memory_text)
            self.assertNotIn("`backend-dotnet/ADR/ADR_30_08_2024_Dotnet_Clean_Architecture-20250128190910.md`", memory_text)
            self.assertNotIn("`.pytest_cache/README.md`", memory_text)
            self.assertIn("Validation command: govkb validate", output.getvalue())

    def test_status_reports_thin_kb_warnings_until_bootstrapped(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir) / "DemoProject"
            codex_home = Path(temp_dir) / "codex-home"
            project_root.mkdir(parents=True, exist_ok=True)
            codex_home.mkdir(parents=True, exist_ok=True)
            run_init(argparse.Namespace(dest=project_root, project_id="demo-project", project_name="Demo Project"))
            _write_demo_repo_files(project_root)

            before = io.StringIO()
            with redirect_stdout(before):
                status_before = run_status(argparse.Namespace(project_root=project_root, codex_home=None))
            self.assertEqual(status_before, 0)
            self.assertIn("KB health warnings:", before.getvalue())
            self.assertIn("missing durable entries in section `Code And Docs Map`", before.getvalue())

            run_init_kb(
                argparse.Namespace(
                    project_root=project_root,
                    capability=None,
                    all=True,
                    codex_home=codex_home,
                )
            )

            after = io.StringIO()
            with redirect_stdout(after):
                status_after = run_status(argparse.Namespace(project_root=project_root, codex_home=None))
            self.assertEqual(status_after, 0)
            self.assertIn("KB health warnings: none", after.getvalue())

    def test_orgchart_like_steward_bootstrap_populates_stable_workflows(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir) / "OrgChart"
            codex_home = Path(temp_dir) / "codex-home"
            project_root.mkdir(parents=True, exist_ok=True)
            codex_home.mkdir(parents=True, exist_ok=True)
            run_init(argparse.Namespace(dest=project_root, project_id="orgchart", project_name="OrgChart"))
            _write_orgchart_like_repo_files(project_root)

            init_exit = run_init_kb(
                argparse.Namespace(
                    project_root=project_root,
                    capability=None,
                    all=True,
                    codex_home=codex_home,
                )
            )
            self.assertEqual(init_exit, 0)

            memory_text = (
                project_root
                / ".governed"
                / "capabilities"
                / "project-knowledge-steward"
                / "references"
                / "long-term-memory.md"
            ).read_text(encoding="utf-8")
            self.assertIn(
                "Primary .NET verification workflow for this capability runs through `src/tests/OrgChart.IntegrationTests/OrgChart.IntegrationTests.csproj`.",
                memory_text,
            )

            status_output = io.StringIO()
            with redirect_stdout(status_output):
                status_exit = run_status(argparse.Namespace(project_root=project_root, codex_home=codex_home))
            self.assertEqual(status_exit, 0)
            self.assertIn("KB health warnings: none", status_output.getvalue())

    def test_init_kb_rematerializes_existing_codex_install(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir) / "DemoProject"
            codex_home = Path(temp_dir) / "codex-home"
            project_root.mkdir(parents=True, exist_ok=True)
            codex_home.mkdir(parents=True, exist_ok=True)
            run_init(argparse.Namespace(dest=project_root, project_id="demo-project", project_name="Demo Project"))
            _write_demo_repo_files(project_root)

            apply_exit = run_codex_apply(
                argparse.Namespace(
                    project_root=project_root,
                    release=None,
                    revision=None,
                    codex_home=codex_home,
                    preview=False,
                )
            )
            self.assertEqual(apply_exit, 0)

            skill_memory_path = (
                codex_home
                / "skills"
                / "govkb-demo-project-project-knowledge-steward"
                / "references"
                / "long-term-memory.md"
            )
            before_text = skill_memory_path.read_text(encoding="utf-8")
            self.assertNotIn("`StoryApp.sln`", before_text)

            output = io.StringIO()
            with patch.dict(os.environ, {"CODEX_HOME": str(codex_home)}):
                with redirect_stdout(output):
                    exit_code = run_init_kb(
                        argparse.Namespace(
                            project_root=project_root,
                            capability=None,
                            all=True,
                            codex_home=None,
                        )
                    )

            self.assertEqual(exit_code, 0)
            after_text = skill_memory_path.read_text(encoding="utf-8")
            self.assertIn("`backend-dotnet/StoryApp.sln`", after_text)
            self.assertIn("Rematerialized Codex capabilities: 1", output.getvalue())


if __name__ == "__main__":
    unittest.main()
