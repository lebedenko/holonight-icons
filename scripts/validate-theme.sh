#!/usr/bin/env sh
set -eu

ROOT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
THEME_DIR="$ROOT_DIR/HoloNight"
INDEX_FILE="$THEME_DIR/index.theme"

fail() {
  echo "validate-theme: $*" >&2
  exit 1
}

[ -f "$INDEX_FILE" ] || fail "missing HoloNight/index.theme"

grep -qx 'Name=HoloNight' "$INDEX_FILE" || fail "index.theme must declare Name=HoloNight"
grep -qx 'Inherits=Papirus-Dark,Papirus,breeze-dark,hicolor' "$INDEX_FILE" || fail "unexpected Inherits value"

directories=$(sed -n 's/^Directories=//p' "$INDEX_FILE" | tr ',' '\n')
[ -n "$directories" ] || fail "Directories entry is empty"

for directory in $directories; do
  [ -d "$THEME_DIR/$directory" ] || fail "missing directory listed in index.theme: $directory"
  grep -Fqx "[$directory]" "$INDEX_FILE" || fail "missing metadata section for $directory"
done

echo "HoloNight theme metadata is valid"
