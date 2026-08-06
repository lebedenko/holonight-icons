#!/usr/bin/env sh
set -eu

ROOT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
THEME_NAME=HoloNight
SOURCE_DIR="$ROOT_DIR/$THEME_NAME"
TARGET_BASE="${XDG_DATA_HOME:-$HOME/.local/share}/icons"
TARGET_DIR="$TARGET_BASE/$THEME_NAME"

if [ ! -f "$SOURCE_DIR/index.theme" ]; then
  echo "Missing theme metadata: $SOURCE_DIR/index.theme" >&2
  exit 1
fi

mkdir -p "$TARGET_BASE"

if command -v rsync >/dev/null 2>&1; then
  rsync -a --delete "$SOURCE_DIR/" "$TARGET_DIR/"
else
  mkdir -p "$TARGET_DIR"
  cp -R "$SOURCE_DIR/." "$TARGET_DIR/"
fi

if command -v gtk-update-icon-cache >/dev/null 2>&1; then
  gtk-update-icon-cache -q -t -f "$TARGET_DIR" || true
fi

echo "Installed $THEME_NAME to $TARGET_DIR"
