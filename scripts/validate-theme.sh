#!/usr/bin/env sh
set -eu
ROOT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
python3 "$ROOT_DIR/scripts/build.py"
exec python3 "$ROOT_DIR/scripts/validate_icons.py"
