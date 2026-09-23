"""Shared, offline theme metadata and semantic stylesheet generation."""
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'icons'
BUILD = ROOT / 'build'
VARIANTS = {'HoloNight': ('light', 'Papirus,breeze,hicolor'),
            'HoloNight-Dark': ('dark', 'Papirus-Dark,Papirus,breeze-dark,hicolor')}
CONTEXTS = {'actions':'Actions', 'apps':'Applications', 'categories':'Categories',
            'devices':'Devices', 'mimetypes':'MimeTypes', 'places':'Places', 'status':'Status'}
PALETTES = json.loads((ROOT / 'metadata/palettes.json').read_text())
ROLES = set(PALETTES['light'])
PLACES = json.loads((ROOT / 'metadata/places.json').read_text())
STYLE = re.compile(r'''(<style\b[^>]*\bid\s*=\s*["']current-color-scheme["'][^>]*>)(.*?)(</style>)''', re.S)


def stylesheet(variant):
    return '\n' + '\n'.join(f' .ColorScheme-{role} {{ color:{color}; }}'
                            for role, color in PALETTES[variant].items()) + '\n'


def recolor(text, variant):
    """Only replace the semantic stylesheet body; artwork stays byte-identical."""
    return STYLE.sub(lambda m: m[1] + stylesheet(variant) + m[3], text)


def directories(source=SOURCE):
    # Full-color names precede same-size symbolic aliases, as in the old index.
    dirs = {str(p.parent.relative_to(source)) for p in source.rglob('*.svg')}
    for alias in [*map(str, PLACES['authored_sizes']), *PLACES['directory_aliases']]:
        for suffix in ('', '/symbolic'):
            if (source / 'places' / (alias + suffix)).is_dir():
                dirs.add('places/' + alias + suffix)
    return sorted(dirs,
                  key=lambda s: ('symbolic' in s.split('/'), s))


def directory_metadata(directory):
    scaled = directory.endswith('/.')
    context, native, *suffix = directory.removesuffix('/.').split('/')
    size = int(native)
    if size < 16 or size > 512 or suffix not in ([], ['symbolic']):
        raise ValueError('invalid native size or representation directory')
    maximum = max(size, 32 if suffix or context in ('actions','status','devices') else 512)
    result = {'Context':CONTEXTS[context], 'Size':str(size), 'Type':'Scalable',
            'MinSize':str(size) if context == 'places' else '16',
            'MaxSize':str(size) if context == 'places' else str(maximum)}
    if scaled:
        result['Scale'] = '2'
    return result


def index_text(name, source=SOURCE):
    dirs = directories(source)
    result = f'[Icon Theme]\nName={name}\nComment=HoloNight {VARIANTS[name][0]} icon theme\nInherits={VARIANTS[name][1]}\nFollowsColorScheme=true\nDirectories={",".join(dirs)}\n'
    # Distinct index keys, same directory: QSettings normalizes trailing slashes.
    # Explicit DPR entries avoid Qt nearest-size fallback shadowing exact masters.
    scaled = [d + '/.' for d in dirs if d.startswith('places/')]
    result += 'ScaledDirectories=' + ','.join(scaled) + '\n'
    for directory in dirs + scaled:
        result += f'\n[{directory}]\n' + ''.join(f'{k}={v}\n' for k,v in directory_metadata(directory).items())
    return result
