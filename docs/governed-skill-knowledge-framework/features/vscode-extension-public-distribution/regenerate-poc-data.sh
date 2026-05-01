#!/usr/bin/env bash
set -euo pipefail

FEATURE_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "${FEATURE_DIR}/../../../.." && pwd)"
ARTIFACT_DIR="${FEATURE_DIR}/poc-artifacts"

mkdir -p "${ARTIFACT_DIR}"
cd "${REPO_ROOT}"

export PYTHONDONTWRITEBYTECODE=1
if [[ -n "${PYTHONPATH:-}" ]]; then
  export PYTHONPATH="${REPO_ROOT}/src:${PYTHONPATH}"
else
  export PYTHONPATH="${REPO_ROOT}/src"
fi

{
  echo "# Current GovKB CLI Baseline"
  echo
  echo "Working directory: ${REPO_ROOT}"
  echo
  echo "## govkb --help"
  python3 -m govkb.cli --help
  echo
  echo "## govkb install --help"
  python3 -m govkb.cli install --help
  echo
  echo "## govkb init-kb --help"
  python3 -m govkb.cli init-kb --help
  echo
  echo "## govkb status --help"
  python3 -m govkb.cli status --help
  echo
  echo "## govkb apply codex --help"
  python3 -m govkb.cli apply codex --help
  echo
  echo "## govkb review-memory --help"
  python3 -m govkb.cli review-memory --help
  echo
  echo "## govkb candidates list --help"
  python3 -m govkb.cli candidates list --help
} > "${ARTIFACT_DIR}/current-cli-baseline.txt"

python3 -m unittest \
  tests/test_install.py \
  tests/test_apply.py \
  tests/test_init_kb.py \
  tests/test_candidates.py \
  tests/test_review_memory_command.py \
  -v > "${ARTIFACT_DIR}/targeted-python-tests.txt" 2>&1

echo "Wrote ${ARTIFACT_DIR}/current-cli-baseline.txt"
echo "Wrote ${ARTIFACT_DIR}/targeted-python-tests.txt"

