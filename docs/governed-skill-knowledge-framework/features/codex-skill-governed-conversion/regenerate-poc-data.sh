#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/../../../.."

PYTHON_BIN="${PYTHON_BIN:-/Users/vasilevevgeny/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3}"

"$PYTHON_BIN" -m govkb.cli --help
rg -n "convert" src/govkb tests || true
"$PYTHON_BIN" -m unittest tests.test_apply.ApplyCommandTests.test_apply_uses_migration_fallback_when_repo_files_are_missing -v
"$PYTHON_BIN" -m unittest tests.test_governed_skill_quality_gates_use_cases tests.test_governed_skill_quality_gates_smoke -v
