#!/usr/bin/env bash
set -euo pipefail

usage() {
  echo "Usage: $(basename "$0") DIRECTORY" >&2
}

if [[ $# -ne 1 ]]; then
  usage
  exit 2
fi

TARGET_DIR="$1"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PALETTE="$SCRIPT_DIR/palette.json"

if [[ ! -f "$PALETTE" ]]; then
  echo "Error: palette file not found: $PALETTE" >&2
  exit 1
fi

if [[ ! -d "$TARGET_DIR" ]]; then
  echo "Error: directory not found: $TARGET_DIR" >&2
  exit 1
fi

find "$TARGET_DIR" -type f -name '*.svg' -print0 | while IFS= read -r -d '' svg; do
  python "$SCRIPT_DIR/recolor_svg.py" \
    --input "$svg" \
    --output "$svg" \
    --palette "$PALETTE"
done
