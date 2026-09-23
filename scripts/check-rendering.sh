#!/usr/bin/env sh
set -eu
ROOT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cmake -S "$ROOT_DIR/tests/rendering" -B "$ROOT_DIR/build/rendering" -DHOLONIGHT_QT_SOURCE="${HOLONIGHT_QT_SOURCE:-$ROOT_DIR/../holonight-qt}"
cmake --build "$ROOT_DIR/build/rendering" --parallel 2
QT_QPA_PLATFORM=offscreen QT_QPA_PLATFORMTHEME= "$ROOT_DIR/build/rendering/render-check" "$ROOT_DIR/build" "$@"
