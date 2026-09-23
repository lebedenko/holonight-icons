#!/usr/bin/env python3
"""Render Qt SVG family sheets on light/dark backgrounds at 1x and 2x."""
import subprocess
import argparse
import shutil
from theme import PLACES
from pathlib import Path
from build import build

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--name', help='Filter by icon name')
    parser.add_argument('--size', type=int, choices=PLACES['authored_sizes'] + list(map(int, PLACES['directory_aliases'])))
    args = parser.parse_args()
    options = []
    if args.name: options += ['--name', args.name]
    if args.size: options += ['--size', str(args.size)]
    build()
    root = Path(__file__).resolve().parents[1]
    if not options:
        shutil.rmtree(root / 'build/previews', ignore_errors=True)
    subprocess.run(['sh', str(root / 'scripts/check-rendering.sh'), '--previews', *options], check=True)
    print(f'Previews: {root / "build/previews"}')
