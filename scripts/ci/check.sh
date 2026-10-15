#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later
set -euo pipefail
export HOLONIGHT_QT_SOURCE=/work/providers/holonight-qt
export GDK_BACKEND=x11 GSK_RENDERER=cairo GTK_A11Y=none
task validate
task test
task test:render
task test:gtk
task preview:icons
task format-check
python3 scripts/quality.py tidy --build build/rendering
task license-check
