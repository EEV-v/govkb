#!/usr/bin/env bash
set -euo pipefail

feature_dir="$(cd "$(dirname "$0")" && pwd)"
repo_root="$(cd "$feature_dir/../../../.." && pwd)"
evidence_dir="$feature_dir/poc-evidence"

mkdir -p "$evidence_dir"

python_candidates=()
if [[ -n "${GOVKB_POC_PYTHON:-}" ]]; then
  python_candidates+=("$GOVKB_POC_PYTHON")
fi
python_candidates+=(
  "python3.12"
  "python3.11"
  "$HOME/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"
  "python3"
)

selected_python=""
for candidate in "${python_candidates[@]}"; do
  if command -v "$candidate" >/dev/null 2>&1; then
    candidate_path="$(command -v "$candidate")"
  elif [[ -x "$candidate" ]]; then
    candidate_path="$candidate"
  else
    continue
  fi
  if "$candidate_path" - <<'PY' >/dev/null 2>&1
import sys
raise SystemExit(0 if sys.version_info >= (3, 11) else 1)
PY
  then
    selected_python="$candidate_path"
    break
  fi
done

if [[ -z "$selected_python" ]]; then
  echo "No Python 3.11+ interpreter found. Set GOVKB_POC_PYTHON to a compatible interpreter." >&2
  exit 1
fi

cd "$repo_root"

{
  echo "Python: $selected_python"
  "$selected_python" -V
} >"$evidence_dir/python-version.txt" 2>&1

PYTHONPATH=src "$selected_python" -m govkb.cli review-memory --help \
  >"$evidence_dir/review-memory-help.txt" 2>&1

PYTHONPATH=src "$selected_python" -m unittest \
  tests.test_review_memory_command \
  tests.test_memory_review.MemoryReviewHelperTests.test_packaged_scheduler_falls_back_to_file_only_sessions_when_index_is_missing \
  tests.test_memory_review.MemoryReviewHelperTests.test_packaged_scheduler_skips_index_rows_without_session_files \
  tests.test_memory_review.MemoryReviewHelperTests.test_packaged_scheduler_defers_sessions_when_classifier_times_out \
  tests.test_memory_review.MemoryReviewHelperTests.test_packaged_scheduler_defers_sessions_when_classifier_hits_usage_limit \
  -v >"$evidence_dir/python-targeted-tests.txt" 2>&1

if command -v rg >/dev/null 2>&1; then
  rg -n "inventory-json|progress-jsonl|reviewMemoryCommand|reviewMaxSessions|lookback-days|max-sessions" \
    src/govkb/cli.py \
    src/govkb/commands/review_memory.py \
    src/govkb/adapters/codex/bin/codex-memory-review \
    vscode-extension/src \
    >"$evidence_dir/source-inventory.txt" 2>&1 || true
fi

(
  cd "$repo_root/vscode-extension"
  npm test
) >"$evidence_dir/vscode-extension-tests.txt" 2>&1

"$selected_python" - "$evidence_dir" <<'PY'
from pathlib import Path
import sys

replacements = {
    "\u2714": "PASS",
    "\u2716": "FAIL",
    "\u2139": "INFO",
}

for path in Path(sys.argv[1]).glob("*.txt"):
    text = path.read_text(encoding="utf-8", errors="replace")
    for source, target in replacements.items():
        text = text.replace(source, target)
    path.write_text(text, encoding="utf-8")
PY

echo "PoC evidence written to $evidence_dir"
