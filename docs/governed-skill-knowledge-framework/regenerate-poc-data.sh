#!/usr/bin/env bash
set -euo pipefail

FEATURE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILLS_ROOT="${SKILLS_ROOT:-/mnt/c/Users/Ev/.codex/skills}"
OUTPUT_DIR="${OUTPUT_DIR:-${FEATURE_DIR}/poc-artifacts}"

if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 is required" >&2
  exit 1
fi

if [[ ! -d "${SKILLS_ROOT}" ]]; then
  echo "skills root not found: ${SKILLS_ROOT}" >&2
  exit 1
fi

python3 "${FEATURE_DIR}/poc/skill_inventory_dry_run.py" \
  --skills-root "${SKILLS_ROOT}" \
  --output-dir "${OUTPUT_DIR}"

echo
echo "Generated PoC artifacts:"
echo "- ${OUTPUT_DIR}/summary.json"
echo "- ${OUTPUT_DIR}/skill-inventory.json"
echo "- ${OUTPUT_DIR}/skill-inventory.md"
echo "- ${OUTPUT_DIR}/proposed-contracts/"
