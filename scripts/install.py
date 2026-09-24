#!/usr/bin/env python3
"""Stage and validate both themes, retain backups, roll back failed replacement."""
import argparse
import fcntl
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
from build import build
from stage import validate_bundle
from theme import BUILD, VARIANTS
from validate_icons import validate_theme


def install(base, refresh=True):
    base = Path(base)
    base.mkdir(parents=True, exist_ok=True)
    with (base / '.holonight-install.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        with tempfile.TemporaryDirectory(prefix='.holonight-stage-', dir=base) as tmp:
            stage = Path(tmp)
            for name in VARIANTS:
                shutil.copytree(BUILD / name, stage / name, symlinks=True)
                errors = validate_theme(stage / name, name)
                if errors:
                    raise ValueError('\n'.join(errors))
            bundle = stage / 'holonight-icons'
            shutil.copytree(BUILD / 'holonight-icons', bundle, symlinks=True)
            validate_bundle(bundle)
            destinations = {name: base / name for name in VARIANTS}
            destinations['holonight-icons'] = base.parent / 'holonight-icons'
            # Unique backup directory keeps every previous installation recoverable.
            backup = Path(tempfile.mkdtemp(prefix='.holonight-backup-', dir=base))
            moved, installed = [], []
            try:
                for name, destination in destinations.items():
                    if destination.exists() or destination.is_symlink():
                        destination.rename(backup / name)
                        moved.append(name)
                    (stage / name).rename(destination)
                    installed.append(name)
            except OSError:
                for name in installed:
                    shutil.rmtree(destinations[name])
                for name in moved:
                    (backup / name).rename(destinations[name])
                raise
            if moved:
                print(f'Previous themes retained in {backup}')
            else:
                backup.rmdir()
    if refresh:
        cache = shutil.which('gtk-update-icon-cache')
        if cache:
            for name in VARIANTS:
                subprocess.run([cache, '-q', '-t', '-f', str(base / name)], check=True)
        cache = shutil.which('kbuildsycoca6')
        if cache:
            subprocess.run([cache, '--noincremental'], check=True)
    print(f'Installed both themes in {base}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--no-cache', action='store_true', help='Skip host cache tools (isolated tests)')
    args = parser.parse_args()
    build()
    data = Path(os.environ.get('XDG_DATA_HOME') or Path.home() / '.local/share')
    if not data.is_absolute():
        parser.error('XDG_DATA_HOME must be absolute')
    install(data / 'icons', not args.no_cache)
