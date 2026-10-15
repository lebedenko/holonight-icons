#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Run rendering regressions against an explicitly supplied Qt source checkout."""
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def render(arguments):
    source = os.environ.get('HOLONIGHT_QT_SOURCE')
    if not source:
        raise SystemExit('Set HOLONIGHT_QT_SOURCE to a Qt checkout, or use task check for pinned sources.')
    build = ROOT / 'build/rendering'
    subprocess.run(['cmake', '-S', str(ROOT / 'tests/rendering'), '-B', str(build), '-G', 'Ninja',
                    '-DHOLONIGHT_RENDERER_FIXTURE=' + str(Path(source).resolve())], check=True)
    subprocess.run(['cmake', '--build', str(build), '--parallel', os.environ.get('JOBS', '2')], check=True)
    subprocess.run([str(build / 'render-check'), str(ROOT / 'build'), *arguments], check=True,
                   env=dict(os.environ, QT_QPA_PLATFORM='offscreen', QT_QPA_PLATFORMTHEME=''))


if __name__ == '__main__':
    if sys.argv[1:2] != ['render']:
        raise SystemExit('Usage: dependencies.py render [renderer arguments]')
    render(sys.argv[2:])
