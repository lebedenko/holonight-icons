#!/usr/bin/env python3
"""Explicit, recoverable user-local recoloring from immutable token templates."""
import argparse
import fcntl
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
from templates import manifest, generate, palette

VARIANTS = {'HoloNight': 'light', 'HoloNight-Dark': 'dark'}


def recolor_theme(data, bundle, name, values, refresh=True):
    if name not in VARIANTS:
        raise ValueError('unknown HoloNight variant')
    data, bundle = Path(data), Path(bundle)
    if not data.is_absolute():
        raise ValueError('XDG_DATA_HOME must be absolute')
    values = palette(values)
    entries = manifest(bundle)
    base = data / 'icons'
    theme = base / name
    if not theme.is_dir() or theme.is_symlink():
        raise ValueError('install the user-local target theme first')
    with (base / '.holonight-install.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        # Reject symlinked output paths, including ancestor directories.
        for entry in entries:
            dest = theme / entry['output']
            if not dest.is_file() or any(p.is_symlink() for p in [dest, *dest.parents] if p != data.parent):
                raise ValueError('target artwork must be an existing regular file in real directories')
        with tempfile.TemporaryDirectory(prefix='.holonight-recolor-stage-', dir=base) as tmp:
            stage = Path(tmp)
            for entry in entries:
                dest = stage / entry['output']
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_text(generate(bundle, entry, values, VARIANTS[name]))
                # Parse/validate the serialized result before any installed file is touched.
                from templates import validate_frozen
                validate_frozen(dest.read_text())
            backup = Path(tempfile.mkdtemp(prefix='.holonight-recolor-backup-', dir=base))
            (backup / 'recovery.json').write_text(json.dumps({'theme': name, 'palette': values,
                'outputs': [e['output'] for e in entries]}, indent=2)+'\n')
            for entry in entries:
                saved = backup / entry['output']
                saved.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(theme / entry['output'], saved)
            replaced = []
            try:
                for entry in entries:
                    rel = entry['output']
                    (stage / rel).replace(theme / rel)
                    replaced.append(rel)
                if refresh:
                    cache = shutil.which('gtk-update-icon-cache')
                    if cache:
                        subprocess.run([cache, '-q', '-t', '-f', str(theme)], check=True)
                    cache = shutil.which('kbuildsycoca6')
                    if cache:
                        subprocess.run([cache, '--noincremental'], check=True)
            except (OSError, subprocess.CalledProcessError):
                for rel in replaced:
                    shutil.copy2(backup / rel, stage / rel)
                    (stage / rel).replace(theme / rel)
                raise
    return backup


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('variant', choices=VARIANTS)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--preset', choices=['holonight-light', 'holonight-dark', 'holonight-day', 'holonight-storm'])
    group.add_argument('--palette', type=Path, help='JSON object with six named #RRGGBB tokens')
    parser.add_argument('--no-cache', action='store_true', help='Skip cache tools in isolated tests')
    args = parser.parse_args()
    # Source checkout and installed application-data bundle share the same layout.
    bundle = Path(__file__).resolve().parents[1]
    data = Path(os.environ.get('XDG_DATA_HOME') or Path.home() / '.local/share')
    try:
        config = json.loads((bundle / 'metadata/palettes.json').read_text())
        values = json.loads(args.palette.read_text()) if args.palette else config['presets'][args.preset]
        backup = recolor_theme(data, bundle, args.variant, values, not args.no_cache)
    except (OSError, ValueError, KeyError) as exc:
        parser.exit(1, f'Recoloring failed: {exc}\n')
    print(f'Recolored {args.variant}; recovery data: {backup}')


if __name__ == '__main__':
    main()
