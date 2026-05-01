ROLE
Senior test engineer generating Python `unittest` scaffolds and a feature helper API from BDD use cases. Output is scaffold code only.

GOAL
From `use-cases.md`, produce three Python files that match GovKB's actual test stack:

1. Use-case coverage tests: one test method per scenario or scenario-outline example.
2. Smoke/manual-exploration tests: one or two happy-path flows that can be run directly.
3. Feature helper API: scaffold-only helper methods grouped by intent.

DOCUMENT CHAIN
- Input: `docs/governed-skill-knowledge-framework/features/<FeatureSlug>/use-cases.md`
- Output 1: `tests/test_<feature_slug>_use_cases.py`
- Output 2: `tests/test_<feature_slug>_smoke.py`
- Output 3: `tests/<feature_slug>_test_helper.py`
- Next: `IMPLEMENT_PROMPT.MD`

INPUT
- FeatureSlug: <kebab-case folder name>
- FeatureName: <human-readable title>
- UseCasesDocument: <BDD scenarios with Background, Scenarios, Scenario Outlines, Examples>
- Optional DomainContext: <CLI commands, files, temp project shape, adapter behavior>

TARGET TEST PATTERNS VERIFIED IN GOVKB
- Framework: stdlib `unittest`.
- Common utilities: `tempfile.TemporaryDirectory`, `pathlib.Path`, `argparse.Namespace`, `contextlib.redirect_stdout`, `io.StringIO`, `unittest.mock.patch`.
- Existing tests often call command functions directly, for example `run_init`, `run_codex_apply`, `run_install`, and `run_validate`.
- No repo-wide custom BDD logger or custom fixture framework exists.

OUTPUT 1: USE-CASE TESTS FILE

File: `tests/test_<feature_slug>_use_cases.py`

Required structure:

```python
"""Use-case scaffold tests for <FeatureName>."""

from __future__ import annotations

import unittest

from <feature_slug>_test_helper import <FeaturePascalName>TestHelper


class <FeaturePascalName>UseCaseTests(unittest.TestCase):
    """Traceable BDD scenario scaffolds."""

    def setUp(self) -> None:
        self.helper = <FeaturePascalName>TestHelper(self)

    def test_uc_1_<snake_title>(self) -> None:
        """UC-1: <scenario title>."""
        self.helper.record_step("Given <exact background or scenario step>")
        self.helper.record_step("When <exact step>")
        self.helper.record_step("Then <exact step>")
        self.skipTest("Scaffold only: implement helper calls and assertions for UC-1.")


if __name__ == "__main__":
    unittest.main()
```

Rules:
- One test method per Scenario.
- One test method per Scenario Outline example row unless a table-driven `subTest` is clearer.
- Preserve exact BDD step text in `record_step(...)`.
- Use `self.skipTest(...)` for scaffold-only tests that are not implemented yet.
- Do not import pytest or third-party libraries.
- Do not depend on real `$HOME`, real `CODEX_HOME`, or existing assistant state.

OUTPUT 2: SMOKE TESTS FILE

File: `tests/test_<feature_slug>_smoke.py`

Required structure:

```python
"""Smoke scaffold tests for <FeatureName>."""

from __future__ import annotations

import tempfile
from pathlib import Path
import unittest

from <feature_slug>_test_helper import <FeaturePascalName>TestHelper


class <FeaturePascalName>SmokeTests(unittest.TestCase):
    """Happy-path scaffolds for local verification."""

    def test_smoke_<snake_title>(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            helper = <FeaturePascalName>TestHelper(self, root=root)
            helper.record_step("Given <exact smoke precondition>")
            helper.record_step("When <exact smoke action>")
            helper.record_step("Then <exact smoke result>")
            self.skipTest("Scaffold only: implement smoke flow.")


if __name__ == "__main__":
    unittest.main()
```

Rules:
- Include only `@smoke` scenarios or the smallest happy-path scenario set.
- Use temp directories for project roots, Codex homes, release files, reports, and fixtures.
- If CLI subprocess behavior is required, use argument-array subprocess calls in implementation, not shell string construction.

OUTPUT 3: HELPER FILE

File: `tests/<feature_slug>_test_helper.py`

Required structure:

```python
"""Helper scaffold for <FeatureName> tests."""

from __future__ import annotations

from pathlib import Path
from typing import Any


class <FeaturePascalName>TestHelper:
    """Feature-specific helper API scaffold."""

    def __init__(self, test_case: Any, root: Path | None = None) -> None:
        self.test_case = test_case
        self.root = root
        self.steps: list[str] = []

    def record_step(self, step: str) -> None:
        self.steps.append(step)

    # Setup
    def configure_<thing>(self, value: str) -> None:
        raise NotImplementedError("TODO: implement setup helper.")

    # Seeding
    def seed_<thing>(self, value: str) -> None:
        raise NotImplementedError("TODO: implement seeding helper.")

    # Execution
    def execute_<action>(self) -> None:
        raise NotImplementedError("TODO: implement execution helper.")

    # Assertions
    def assert_<outcome>(self) -> None:
        raise NotImplementedError("TODO: implement assertion helper.")

    # Cleanup
    def cleanup(self) -> None:
        raise NotImplementedError("TODO: implement cleanup helper.")
```

DERIVATION RULES
1. Extract every Given/When/Then/And step.
2. Cluster helper methods by intent:
   - Setup: project roots, governed packages, config, release state.
   - Seeding: files, contracts, sessions, reports, candidate metadata.
   - Execution: CLI command functions, adapter materialization, review-memory flows.
   - Assertions: files, stdout, reports, install state, candidate status.
   - Cleanup: temp state only.
3. Use `Path` for filesystem paths and plain stdlib types for values.
4. Keep helper methods scaffold-only unless the user explicitly asks for implementation.

FINAL OUTPUT
Produce exactly three Python code blocks in this order:
1. `tests/test_<feature_slug>_use_cases.py`
2. `tests/test_<feature_slug>_smoke.py`
3. `tests/<feature_slug>_test_helper.py`

QUALITY RULES
- Every scenario maps to a test method or `subTest`.
- Every distinct action gets a helper method.
- Step text is preserved in `record_step(...)`.
- Files are syntactically valid Python.
- No third-party test framework imports.
- No source-project paths or framework names.

END
