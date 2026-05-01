#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/../../.."

python3 -m unittest discover -s tests -v
python3 -m govkb.cli --help >/tmp/govkb-help.txt
python3 -m govkb.cli validate /home/ev/code/Clearing >/tmp/govkb-clearing-validate.txt
