#!/usr/bin/env python3
"""Run native KDE icon recoloring with disposable XDG configuration and caches."""
import argparse
import os
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('svg', nargs='?', type=Path,
                        default=ROOT / 'tests/kde/application-xml.svg')
    parser.add_argument('--output', type=Path, help='Keep a separate comparison/report directory')
    args = parser.parse_args()
    source = args.svg.resolve(strict=True)
    build = ROOT / 'build/kde'
    output = args.output.resolve() if args.output else build / 'results'
    subprocess.run(['cmake', '-S', str(ROOT / 'tests/kde'), '-B', str(build)], check=True)
    subprocess.run(['cmake', '--build', str(build), '--parallel', '2'], check=True)
    output.mkdir(parents=True, exist_ok=True)
    # A failed run must not leave an earlier successful report in place.
    for name in ('comparison.png', 'report.txt'):
        (output / name).unlink(missing_ok=True)
    with tempfile.TemporaryDirectory(prefix='holonight-kde-') as tmp:
        env = dict(os.environ, QT_QPA_PLATFORM='offscreen', QT_QPA_PLATFORMTHEME='')
        for key, suffix in [('XDG_DATA_HOME', 'data'), ('XDG_CONFIG_HOME', 'config'),
                            ('XDG_CACHE_HOME', 'cache'), ('XDG_RUNTIME_DIR', 'runtime')]:
            path = Path(tmp) / suffix
            path.mkdir(mode=0o700)
            env[key] = str(path)
        result = subprocess.run([str(build / 'kde-check'), str(source), str(output)], env=env)
    print(f'KDE comparison and report: {output}', flush=True)
    raise SystemExit(result.returncode)


if __name__ == '__main__':
    main()
