#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/../../../.."

PYTHON_BIN="${PYTHON_BIN:-/Users/vasilevevgeny/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3}"

"$PYTHON_BIN" -m govkb.cli --help
rg -n -e "--strict|strict validation|strict" src/govkb tests || true
"$PYTHON_BIN" -m unittest tests.test_validate -v
"$PYTHON_BIN" -m unittest tests.test_candidates.CandidateCommandTests.test_auto_create_ready_creates_capability_and_materializes_codex -v
