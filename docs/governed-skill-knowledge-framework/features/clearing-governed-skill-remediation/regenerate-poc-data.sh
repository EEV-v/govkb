#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/../../../.."

if [[ -n "${PYTHON:-}" ]]; then
  PYTHON_BIN="$PYTHON"
elif command -v python3 >/dev/null 2>&1 && python3 -c 'import tomllib' >/dev/null 2>&1; then
  PYTHON_BIN="python3"
elif [[ -x "/Users/vasilevevgeny/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3" ]]; then
  PYTHON_BIN="/Users/vasilevevgeny/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"
else
  echo "error: could not find a Python runtime with tomllib support" >&2
  exit 1
fi

"$PYTHON_BIN" -m unittest tests.test_clearing_governed_skill_remediation_use_cases tests.test_clearing_governed_skill_remediation_smoke -v
