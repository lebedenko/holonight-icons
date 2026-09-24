#!/usr/bin/env python3
"""Build and validate a system payload without installing into the host."""
import argparse
from pathlib import Path
import shutil
import tempfile

from build import build, bundle_files
from theme import BUILD, ROOT, VARIANTS
from validate_icons import validate_theme


def validate_bundle(bundle):
    paths = list(bundle.rglob('*'))
    if bundle.is_symlink() or any(path.is_symlink() for path in paths):
        raise ValueError('Installed template bundle must not contain symlinks')
    if {str(path.relative_to(bundle)) for path in paths if path.is_file()} != bundle_files():
        raise ValueError('Installed template bundle inventory differs from source')
    for path in paths:
        if path.is_file():
            rel = path.relative_to(bundle)
            if path.read_bytes() != (ROOT / rel).read_bytes():
                raise ValueError(f'Invalid installed template bundle file: {rel}')


def stage(destdir):
    """Package an existing build into unused destinations, preserving aliases."""
    destdir = Path(destdir)
    if not destdir.is_absolute() or '..' in destdir.parts:
        raise ValueError('DESTDIR must be an absolute path without .. components')
    destinations = {name: destdir / 'usr/share/icons' / name for name in VARIANTS}
    destinations['holonight-icons'] = destdir / 'usr/share/holonight-icons'
    for destination in destinations.values():
        if destination.exists() or destination.is_symlink():
            raise ValueError(f'Packaging destination already exists: {destination}')
        if any(parent.is_symlink() for parent in destination.parents):
            raise ValueError(f'Symlinked packaging parent: {destination}')
    # Validate copies before making any payload visible at its final location.
    destdir.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.holonight-package-', dir=destdir) as tmp:
        payload = Path(tmp)
        for name in destinations:
            shutil.copytree(BUILD / name, payload / name, symlinks=True)
        for name in VARIANTS:
            errors = validate_theme(payload / name, name)
            if errors:
                raise ValueError('\n'.join(errors))
        validate_bundle(payload / 'holonight-icons')
        installed = []
        try:
            for name, destination in destinations.items():
                destination.parent.mkdir(parents=True, exist_ok=True)
                (payload / name).rename(destination)
                installed.append(destination)
        except OSError:
            for destination in installed:
                shutil.rmtree(destination)
            raise


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--destdir', required=True, type=Path)
    args = parser.parse_args()
    try:
        build()
        stage(args.destdir)
    except (OSError, ValueError) as exc:
        parser.exit(1, f'error: {exc}\n')
    print(f'Staged both themes and template bundle below {args.destdir}')
