"""Validation edge-case tests."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path
import unittest

from govkb.commands.init import run_init
from govkb.core.contracts import load_project_bundle


class ValidateCommandTests(unittest.TestCase):
    """Validation behavior for bad governed contracts."""

    def test_invalid_capability_path_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir) / "DemoProject"
            project_root.mkdir(parents=True, exist_ok=True)
            run_init(argparse.Namespace(dest=project_root, project_id="demo-project", project_name="Demo Project"))

            capability_root = project_root / ".governed" / "capabilities" / "bad-capability"
            capability_root.mkdir(parents=True, exist_ok=True)
            (capability_root / "capability.contract.toml").write_text(
                """contract_version = 1

[capability]
id = "bad-capability"
name = "Bad Capability"
governed = true
description = "bad target path"

[routing]
aliases = []
hints = ["bad capability"]
negative_hints = []

[memory]
enabled = true
auto_apply_min_confidence = 0.85
requires_explicit_acceptance = false

[memory.targets.main]
path = "../escape.md"
sections = ["Working Agreement"]
""",
                encoding="utf-8",
            )

            bundle, result = load_project_bundle(project_root)
            self.assertTrue(result.errors)
            self.assertNotIn("bad-capability", bundle.capabilities)
            self.assertTrue(any("parent traversal" in message.message for message in result.errors))

    def test_duplicate_capability_ids_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir) / "DemoProject"
            project_root.mkdir(parents=True, exist_ok=True)
            run_init(argparse.Namespace(dest=project_root, project_id="demo-project", project_name="Demo Project"))

            for folder_name in ("cap-one", "cap-two"):
                capability_root = project_root / ".governed" / "capabilities" / folder_name
                references_root = capability_root / "references"
                references_root.mkdir(parents=True, exist_ok=True)
                (references_root / "long-term-memory.md").write_text("# Notes\n\n## Working Agreement\n", encoding="utf-8")
                (capability_root / "capability.contract.toml").write_text(
                    """contract_version = 1

[capability]
id = "duplicate-capability"
name = "Duplicate Capability"
governed = true
description = "duplicate capability"

[routing]
aliases = []
hints = ["duplicate"]
negative_hints = []

[memory]
enabled = true
auto_apply_min_confidence = 0.85
requires_explicit_acceptance = false

[memory.targets.main]
path = "references/long-term-memory.md"
sections = ["Working Agreement"]
""",
                    encoding="utf-8",
                )

            _, result = load_project_bundle(project_root)
            self.assertTrue(any("duplicate capability id" in message.message for message in result.errors))


if __name__ == "__main__":
    unittest.main()
