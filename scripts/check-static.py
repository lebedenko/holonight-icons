#!/usr/bin/env python3
"""Run canonical strict tidy on the explicitly enabled owned renderer tools."""
import argparse
import json
import os
from pathlib import Path
import shlex
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--build', type=Path, default=ROOT / 'build/rendering')
    parser.add_argument('--kde', action='store_true')
    parser.add_argument('--fix', action='store_true', help='Explicitly apply clang-tidy fixes during development')
    args = parser.parse_args()
    entries = json.loads((args.build / 'compile_commands.json').read_text())
    selected = ROOT / ('tests/kde/kde_check.cpp' if args.kde else 'tests/rendering/render_check.cpp')
    filtered = []
    for entry in entries:
        if Path(entry['file']).resolve() != selected:
            continue
        command = entry.get('arguments') or shlex.split(entry['command'])
        # Match the canonical bundle's compiler database adaptation for Clang.
        command = [value for value in command if value not in {'-mno-direct-extern-access', '-fno-keep-inline-dllexport'}]
        filtered.append(dict(directory=entry['directory'], file=entry['file'], arguments=command))
    if not filtered:
        parser.error(f'Missing compile command for {selected}; configure the enabled tool explicitly.')
    target = ROOT / '.cache/tooling/renderer-tidy'
    target.mkdir(parents=True, exist_ok=True)
    (target / 'compile_commands.json').write_text(json.dumps(filtered, indent=2) + '\n')
    command = [os.environ.get('CLANG_TIDY', 'clang-tidy'), str(selected), '-p', str(target),
               '--config-file=' + str(ROOT / '.clang-tidy')]
    if args.fix:
        command += ['--fix']
    subprocess.run(command, check=True)


if __name__ == '__main__':
    main()
