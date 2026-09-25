#!/usr/bin/env python3
"""Validate the deliberately small SVG/CSS contract, aliases and theme metadata."""
import argparse
import configparser
import json
import math
import re
import sys
from pathlib import Path
from xml.etree import ElementTree as ET
from templates import manifest, default_output, validate_frozen
from theme import ROOT, SOURCE, BUILD, VARIANTS, ROLES, PLACES, DEVICES, MASTER_CONTEXTS, directories, directory_metadata, recolor

SHAPES = {'path','rect','circle','ellipse','polygon','polyline','line','use','text','image'}
CSS_RULE = re.compile(r'\.ColorScheme-([A-Za-z]+)\s*\{\s*color\s*:\s*(#[0-9a-fA-F]{6})\s*;?\s*\}')


def local(tag):
    return tag.rsplit('}', 1)[-1]


def declarations(text):
    result = {}
    for item in text.split(';'):
        if not item.strip():
            continue
        key, value = item.split(':', 1)
        result[key.strip()] = value.strip()
    return result


def validate_svg(path, exemption=None, native=None):
    errors = []
    try:
        root = ET.fromstring(path.read_text())
        box = [float(x) for x in re.split(r'[ ,]+', root.get('viewBox',''))]
        if local(root.tag) != 'svg' or len(box) != 4 or not all(map(math.isfinite, box)) or min(box[2:]) <= 0:
            raise ValueError('invalid svg root/viewBox')
        if native is not None and max(box[2:]) != native:
            errors.append('canvas does not match native size directory')
    except (OSError, ET.ParseError, ValueError) as exc:
        return [f'invalid SVG: {exc}']
    styles = [e for e in root.iter() if local(e.tag) == 'style']
    fixed_asset = exemption and exemption.get('scope') == 'asset'
    fixed_ids = set(exemption.get('ids', [])) if exemption else set()
    seen_fixed = set()
    if fixed_asset:
        if any('currentColor' in str(e.attrib) or 'ColorScheme-' in str(e.attrib) for e in root.iter()):
            errors.append('whole-asset exemption masks semantic artwork')
    # Fixed artwork also needs the holonight-qt tinting guard.
    if len(styles) != 1 or styles[0].get('id') != 'current-color-scheme' or styles[0].get('type') != 'text/css':
        errors.append('requires exactly one style with current-color-scheme ID and text/css type')
    definitions = []
    for style in styles:
        css = style.text or ''
        definitions.extend(role for role, _ in CSS_RULE.findall(css))
        if CSS_RULE.sub('',css).strip():
            errors.append('unsupported CSS: only semantic color definitions are allowed')
    if set(definitions) != ROLES or len(definitions) != len(ROLES):
        errors.append('missing, duplicate or unsupported stylesheet roles')
    semantic_paints = 0
    fixed_paints = 0
    used_fixed = set()
    ids = [e.get('id') for e in root.iter() if e.get('id')]
    if len(ids) != len(set(ids)):
        errors.append('duplicate element IDs')

    def walk(element, inherited, role=None, exempt=False, hidden=False, owners=frozenset()):
        nonlocal semantic_paints, fixed_paints
        tag = local(element.tag)
        hidden = hidden or tag in {'defs','clipPath','mask'}
        exempt = exempt or fixed_asset or element.get('id') in fixed_ids
        if element.get('id') in fixed_ids:
            seen_fixed.add(element.get('id'))
            owners = owners | {element.get('id')}
        values = dict(inherited)
        classes = element.get('class','').split()
        if classes:
            if len(classes) != 1 or classes[0] not in {'ColorScheme-'+r for r in ROLES}:
                errors.append('unsupported or ambiguous semantic class')
            else:
                role = classes[0]
                if role in {'ColorScheme-Background', 'ColorScheme-HighlightedText'}:
                    errors.append('role not yet supported by holonight-qt renderer')
                values.pop('color', None)  # local class overrides inherited color
        try:
            inline = declarations(element.get('style',''))
        except ValueError:
            errors.append('malformed inline style')
            inline = {}
        for key in ('fill','stroke','stop-color','color'):
            value = inline.get(key,element.get(key))
            if value is not None and value != 'inherit':
                values[key] = value
        if not fixed_asset and ('color' in inline or element.get('color') is not None):
            errors.append('inline/presentation color overrides semantic role')
        if not fixed_asset and (tag in {'script','foreignObject','image','text','use','animate','set'} or any(k.startswith('on') for k in element.attrib)):
            errors.append(f'unsupported semantic element/animation: {tag}')
        if (tag in SHAPES and not hidden) or tag == 'stop':
            for paint in (('stop-color',) if tag == 'stop' else ('fill','stroke')):
                value = values.get(paint, 'none' if paint == 'stroke' else 'black')
                if value == 'none':
                    continue
                if value == 'currentColor':
                    if not role or 'color' in values:
                        errors.append('currentColor without effective semantic role')
                    semantic_paints += 1
                elif (paint != 'stop-color' and re.fullmatch(r'url\(#[\w-]+\)', value)
                      and any(e.get('id') == value[5:-1] and local(e.tag) in {'linearGradient','radialGradient'} for e in root.iter())):
                    continue
                elif not exempt:
                    errors.append(f'unclassified effective {paint}: {value}')
                else:
                    fixed_paints += 1
                    used_fixed.update(owners)
        for child in element:
            walk(child, values, role, exempt, hidden, owners)
    walk(root, {})
    if not fixed_asset and not semantic_paints:
        errors.append('semantic artwork has no effective semantic paints')
    if fixed_asset and not fixed_paints:
        errors.append('stale whole-asset exemption: no fixed paints')
    if fixed_ids != seen_fixed or fixed_ids != used_fixed:
        errors.append('stale element exemption')
    return errors


def alias_errors(tree):
    errors = []
    for path in tree.rglob('*'):
        if not path.is_symlink():
            continue
        try:
            target = path.resolve(strict=True)
            rel = path.relative_to(tree)
            if target.is_dir():
                context = rel.parent.name
                spec = MASTER_CONTEXTS.get(context) if rel.parent == Path(context) else None
                expected = spec['directory_aliases'].get(rel.name) if spec else None
                if expected is None or str(path.readlink()) != expected or target != (tree / context / expected).absolute() or (tree / context / expected).is_symlink():
                    errors.append(f'{path}: undeclared or invalid size-directory alias')
                continue
            if Path(path.readlink()).is_absolute() or not target.is_relative_to(tree.resolve()) or not target.is_file() or target.suffix != '.svg':
                errors.append(f'{path}: alias must be relative, internal and point to an SVG file')
        except (OSError, RuntimeError):
            errors.append(f'{path}: broken alias or cycle')
    return errors


def validate_places(tree):
    errors = []
    places = tree / 'places'
    declared = {*map(str, PLACES['authored_sizes']), *PLACES['directory_aliases']}
    if not places.is_dir() or places.is_symlink():
        errors.append('Places root must be a real directory')
    elif {p.name for p in places.iterdir()} != declared:
        errors.append('Places size directories differ from declared masters and aliases')
    for size in PLACES['authored_sizes']:
        directory = places / str(size)
        if not directory.is_dir() or directory.is_symlink():
            errors.append(f'{directory}: authored size must be a real directory')
    for alias, target in PLACES['directory_aliases'].items():
        p = tree / 'places' / alias
        if not p.is_symlink() or str(p.readlink()) != target:
            errors.append(f'{p}: missing or changed size-directory alias')
    for rel, target in PLACES['lookup_aliases'].items():
        path = tree / rel
        if not path.is_symlink() or str(path.readlink()) != target:
            errors.append(f'{path}: missing or changed Places lookup alias')
    inventory = json.loads((ROOT / 'metadata/migration.json').read_text())['icons']
    if set(PLACES['migration_dispositions']) != {i['old'] for i in inventory if i['path'].startswith('places/')}:
        errors.append('Places dispositions must cover exactly historical Places entries')
    return errors


def validate_devices(tree):
    errors = []
    devices = tree / 'devices'
    declared = {*map(str, DEVICES['authored_sizes']), *DEVICES['directory_aliases']}
    if not devices.is_dir() or devices.is_symlink() or {p.name for p in devices.iterdir()} != declared:
        errors.append('Devices size directories differ from declared masters and aliases')
    for size in DEVICES['authored_sizes']:
        p = devices / str(size)
        if not p.is_dir() or p.is_symlink(): errors.append(f'{p}: authored size must be a real directory')
    for alias, target in DEVICES['directory_aliases'].items():
        p = devices / alias
        if not p.is_symlink() or str(p.readlink()) != target:
            errors.append(f'{p}: missing or changed size-directory alias')
    for rel, target in DEVICES['lookup_aliases'].items():
        p = tree / rel
        if not p.is_symlink() or str(p.readlink()) != target:
            errors.append(f'{p}: missing or changed Devices lookup alias')
    inventory = json.loads((ROOT / 'metadata/migration.json').read_text())['icons']
    if set(DEVICES['migration_dispositions']) != {i['old'] for i in inventory if i['path'].startswith('devices/')}:
        errors.append('Devices dispositions must cover exactly historical Devices entries')
    expected = {f'{size}/{name}.svg' for size in (24,32) for name in DEVICES['proof_names']}
    expected |= {f'24/symbolic/{name}-symbolic.svg' for name in DEVICES['proof_names']}
    expected |= {p.removeprefix('devices/') for p in DEVICES['lookup_aliases']}
    actual = {str(p.relative_to(devices)) for p in devices.rglob('*.svg')}
    if actual != expected: errors.append('Devices artwork inventory differs from five families and aliases')
    return errors


def validate_source(tree=SOURCE):
    errors = alias_errors(tree)
    exemptions = json.loads((ROOT / 'metadata/fixed-artwork.json').read_text())
    for rel, item in exemptions.items():
        path = tree / rel
        if (not path.is_file() or path.is_symlink() or not item.get('rationale')
                or item.get('scope') not in ('asset','elements')
                or Path(rel).is_absolute() or '..' in Path(rel).parts
                or any(c in rel for c in '*?[')
                or (item.get('scope') == 'elements' and not item.get('ids'))):
            errors.append(f'{rel}: stale or invalid exemption')
    try:
        templates = {e['output']: e for e in manifest(ROOT)}
        for rel, entry in templates.items():
            if rel in exemptions or not (tree / rel).is_file() or (tree / rel).is_symlink():
                errors.append(f'{rel}: template missing or masked by fixed exemption')
    except (ValueError, KeyError, OSError) as exc:
        return errors + [str(exc)]
    for path in sorted(tree.rglob('*.svg')):
        if path.is_symlink():
            continue
        rel = path.relative_to(tree)
        try:
            native = int(rel.parts[1])
            directory_metadata(str(rel.parent))
        except (ValueError, KeyError, IndexError):
            errors.append(f'{rel}: invalid context/size directory')
            continue
        if str(rel) in templates:
            try:
                from templates import resolve, RULE
                from theme import PALETTES
                css = next(e.text for e in ET.fromstring(path.read_text()).iter() if local(e.tag) == 'style')
                defaults = {'ColorScheme-'+r:v for r,v in PALETTES['dark'].items()}
                defaults.update({c:PALETTES['presets']['holonight-dark'][t] for c,t in templates[str(rel)]['classes'].items()})
                if dict(RULE.findall(css or '')) != defaults:
                    errors.append(f'{rel}: canonical template defaults must be Dark')
                output = resolve(path.read_text(), templates[str(rel)], PALETTES['presets']['holonight-dark'], PALETTES['dark'])
                validate_frozen(output)
            except (ValueError, KeyError, ET.ParseError, StopIteration) as exc:
                errors.append(f'{rel}: {exc}')
            continue
        errors.extend(f'{rel}: {e}' for e in validate_svg(path,exemptions.get(str(rel)),native))
    errors.extend(validate_places(tree) + validate_devices(tree))
    inventory = json.loads((ROOT / 'metadata/migration.json').read_text())['icons']
    app_dispositions = json.loads((ROOT / 'metadata/apps.json').read_text())['migration_dispositions']
    if set(app_dispositions) != {'scalable/apps/kiro.svg'}:
        errors.append('unexpected Applications migration dispositions')
    for item in inventory:
        path = tree / item['path']
        if item['old'] in app_dispositions:
            disposition = app_dispositions[item['old']]
            if (disposition.get('status') != 'retired' or disposition.get('path') != item['path']
                    or not disposition.get('rationale')):
                errors.append(f'{path}: invalid Applications disposition')
            elif path.exists():
                errors.append(f'{path}: retired name unexpectedly present')
            continue
        if item['path'].startswith('places/'):
            disposition = PLACES['migration_dispositions'].get(item['old'], {})
            if disposition.get('path') != item['path'] or not disposition.get('rationale'):
                errors.append(f'{path}: missing Places disposition')
            elif disposition.get('status') == 'pending-redesign':
                if path.exists(): errors.append(f'{path}: deferred name unexpectedly present')
            elif disposition.get('status') == 'replacement':
                if not path.is_file() or path.resolve() != (tree / disposition.get('target', '')).resolve():
                    errors.append(f'{path}: Places replacement target changed')
            else: errors.append(f'{path}: invalid Places disposition')
            continue
        if item['path'].startswith('devices/'):
            disposition = DEVICES['migration_dispositions'].get(item['old'], {})
            if disposition.get('path') != item['path'] or not disposition.get('rationale'):
                errors.append(f'{path}: missing Devices disposition')
            elif disposition.get('status') == 'retired':
                if path.exists(): errors.append(f'{path}: retired name unexpectedly present')
            elif disposition.get('status') == 'replacement':
                if not path.is_file() or path.resolve() != (tree / disposition.get('target', '')).resolve():
                    errors.append(f'{path}: Devices replacement target changed')
            else: errors.append(f'{path}: invalid Devices disposition')
            continue
        if not path.is_file():
            errors.append(f'missing migrated lookup name: {item["old"]}')
        elif 'target' in item:
            try:
                if not path.is_symlink() or path.resolve() != (tree / item['target']).resolve():
                    errors.append(f'{path}: migrated alias target changed')
            except (OSError, RuntimeError):
                errors.append(f'{path}: alias cycle')
    return errors


def validate_theme(tree, name):
    errors = alias_errors(tree) + validate_places(tree) + validate_devices(tree)
    try:
        config = configparser.ConfigParser(interpolation=None, strict=True)
        config.read_string((tree / 'index.theme').read_text())
        theme = config['Icon Theme']
        if theme['Name'] != name or theme['Inherits'] != VARIANTS[name][1] or theme['FollowsColorScheme'] != 'true':
            errors.append('invalid theme identity, fallback order or FollowsColorScheme')
        dirs = theme['Directories'].split(',')
        if dirs != directories():
            errors.append('directory list/duplicate-name precedence differs from source')
        scaled = [d + '/.' for d in dirs if d.split('/')[0] in MASTER_CONTEXTS]
        if theme.get('ScaledDirectories', '').split(',') != scaled:
            errors.append('scaled directory metadata differs from source')
        if set(config.sections()) != {'Icon Theme', *dirs, *scaled}:
            errors.append('missing or extra metadata sections')
        for directory in dirs + scaled:
            if not (tree / directory).is_dir() or (directory.split('/')[0] not in MASTER_CONTEXTS and not any((tree / directory).glob('*.svg'))):
                errors.append(f'{directory}: missing/empty directory')
            actual = dict(config[directory])
            expected = {k.lower():v for k,v in directory_metadata(directory).items()}
            if actual != expected:
                errors.append(f'{directory}: invalid context, scalable type or size range')
        actual_files = {str(p.relative_to(tree)) for p in tree.rglob('*.svg')}
        source_files = {str(p.relative_to(SOURCE)) for p in SOURCE.rglob('*.svg')}
        if actual_files != source_files:
            errors.append('generated icon inventory differs from source')
        templates = {e['output']: e for e in manifest(ROOT)}
        for rel in source_files & actual_files:
            src, dst = SOURCE / rel, tree / rel
            if src.is_symlink():
                if not dst.is_symlink() or src.readlink() != dst.readlink():
                    errors.append(f'{rel}: generated alias changed')
            elif dst.is_symlink() or dst.read_text() != (default_output(ROOT, templates[rel], VARIANTS[name][0]) if rel in templates else recolor(src.read_text(),VARIANTS[name][0])):
                errors.append(f'{rel}: generated artwork differs beyond semantic defaults')
        for filename in ('LICENSES/GPL-3.0-only.txt', 'LICENSES/GPL-3.0-or-later.txt', 'THIRD_PARTY_NOTICES.md'):
            if (tree / filename).read_bytes() != (ROOT / filename).read_bytes():
                errors.append(f'{filename}: missing or changed attribution/license')
        if (tree / 'REUSE.toml').read_text() != (ROOT / 'REUSE.toml').read_text().replace('icons/', ''):
            errors.append('generated REUSE paths differ from source attribution')
    except (OSError, ValueError, KeyError, configparser.Error, RuntimeError) as exc:
        errors.append(f'invalid theme metadata/tree: {exc}')
    return [f'{tree}: {error}' for error in errors]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--theme-root', type=Path, default=BUILD)
    args = parser.parse_args()
    errors = validate_source()
    for name in VARIANTS:
        errors.extend(validate_theme(args.theme_root / name,name))
    if errors:
        print('\n'.join(errors),file=sys.stderr)
        return 1
    print('Validated source, migration inventory and both theme variants.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
