#!/usr/bin/env python3
"""Build complete variants; never recolor literal artwork paints."""
import shutil
from templates import manifest, default_output
from theme import BUILD, ROOT, SOURCE, VARIANTS, index_text, recolor


def bundle_files():
    return {'metadata/templates.json', 'metadata/palettes.json',
            'scripts/templates.py', 'scripts/recolor.py', 'REUSE.toml',
            'THIRD_PARTY_NOTICES.md', 'LICENSES/GPL-3.0-or-later.txt',
            *[entry['source'] for entry in manifest(ROOT)]}


def build():
    from validate_icons import validate_source
    errors = validate_source()
    if errors:
        raise ValueError('\n'.join(errors))
    BUILD.mkdir(exist_ok=True)
    templates = {e["output"]: e for e in manifest(ROOT)}
    for name, (variant, _) in VARIANTS.items():
        target = BUILD / name
        if target.exists():
            shutil.rmtree(target)
        shutil.copytree(SOURCE, target, symlinks=True)
        for path in target.rglob('*.svg'):
            if not path.is_symlink():
                entry = templates.get(str(path.relative_to(target)))
                path.write_text(default_output(ROOT, entry, variant) if entry else recolor(path.read_text(), variant))
        (target / 'index.theme').write_text(index_text(name))
        shutil.copytree(ROOT / 'LICENSES', target / 'LICENSES')
        shutil.copy2(ROOT / 'THIRD_PARTY_NOTICES.md', target)
        (target / 'REUSE.toml').write_text((ROOT / 'REUSE.toml').read_text().replace('icons/', ''))
        print(f'Built {target.relative_to(ROOT)}')
    bundle = BUILD / 'holonight-icons'
    if bundle.exists():
        shutil.rmtree(bundle)
    for rel in sorted(bundle_files()):
        dest = bundle / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / rel, dest)


if __name__ == '__main__':
    build()
