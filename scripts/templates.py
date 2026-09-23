"""Strict token templates and deterministic, literal SVG export (stdlib only)."""
import json
from pathlib import Path
import re
from xml.etree import ElementTree as ET

ET.register_namespace('', 'http://www.w3.org/2000/svg')
TOKENS = {'background', 'surface', 'textPrimary', 'accentCyan', 'accentBlue', 'accentViolet'}
COLOR = re.compile(r'#[0-9a-fA-F]{6}\Z')
RULE = re.compile(r'\.([A-Za-z-]+)\s*\{\s*color\s*:\s*(#[0-9a-fA-F]{6})\s*;?\s*\}')
TAGS = {'svg', 'defs', 'style', 'g', 'path', 'rect', 'circle', 'ellipse', 'line',
        'polygon', 'polyline', 'linearGradient', 'radialGradient', 'stop'}
ATTRS = {'id', 'class', 'type', 'width', 'height', 'viewBox', 'd', 'x', 'y', 'x1', 'x2',
         'y1', 'y2', 'cx', 'cy', 'r', 'rx', 'ry', 'fx', 'fy', 'points', 'transform',
         'gradientUnits', 'gradientTransform', 'offset', 'fill', 'stroke', 'stop-color',
         'opacity', 'fill-opacity', 'stroke-opacity', 'stop-opacity', 'stroke-width',
         'stroke-linecap', 'stroke-linejoin', 'fill-rule'}
SHAPES = {'path', 'rect', 'circle', 'ellipse', 'line', 'polygon', 'polyline'}


def local(element):
    return element.tag.rsplit('}', 1)[-1]


def safe_path(value):
    if not isinstance(value, str):
        raise ValueError('manifest path must be a string')
    p = Path(value)
    if p.is_absolute() or '..' in p.parts or str(p) != value:
        raise ValueError('manifest paths must be normalized and relative')
    return p


def manifest(base):
    data = json.loads((base / 'metadata/templates.json').read_text())
    if data.get('version') != 1 or not data.get('templates'):
        raise ValueError('invalid template manifest version or inventory')
    seen = set()
    for item in data['templates']:
        src, dst = safe_path(item['source']), safe_path(item['output'])
        if src != Path('icons') / dst or dst.suffix != '.svg' or len(dst.parts) != 3:
            raise ValueError('template source must be canonical icons/context/size/name.svg')
        if item['output'] in seen:
            raise ValueError('duplicate template output')
        seen.add(item['output'])
        mapping = item['classes']
        if not mapping or any(not re.fullmatch(r'HoloNight-[A-Za-z]+', c) or t not in TOKENS for c,t in mapping.items()):
            raise ValueError('unknown template class/token mapping')
    return data['templates']


def palette(values, required=TOKENS):
    if not isinstance(values, dict) or set(values) != set(required):
        raise ValueError('palette must contain exactly these named tokens: ' + ', '.join(sorted(required)))
    if any(not isinstance(v, str) or not COLOR.fullmatch(v) for v in values.values()):
        raise ValueError('token colors must be opaque #RRGGBB strings')
    return {k: v.lower() for k,v in values.items()}


def resolve(text, item, values, semantic):
    """Validate every effective paint, then freeze role identity into literal paints."""
    values = palette(values)
    root = ET.fromstring(text)
    native = int(Path(item['output']).parts[1])
    if local(root) != 'svg' or root.get('viewBox') != f'0 0 {native} {native}':
        raise ValueError('template canvas must match native size')
    styles = [e for e in root.iter() if local(e) == 'style']
    if len(styles) != 1 or styles[0].get('id') != 'current-color-scheme' or styles[0].get('type') != 'text/css':
        raise ValueError('template needs exactly one semantic stylesheet guard')
    css = styles[0].text or ''
    rules = RULE.findall(css)
    mapping = item['classes']
    expected = set(mapping) | {'ColorScheme-'+r for r in semantic}
    if RULE.sub('', css).strip() or len(rules) != len(expected) or {c for c,v in rules} != expected:
        raise ValueError('invalid template stylesheet definitions')
    ids = [e.get('id') for e in root.iter() if e.get('id')]
    if len(ids) != len(set(ids)):
        raise ValueError('duplicate template ID')
    gradients = {e.get('id') for e in root.iter() if local(e) in {'linearGradient','radialGradient'}}
    used = set()
    def walk(e, inherited, role=None):
        tag = local(e)
        if tag not in TAGS or set(e.attrib) - ATTRS:
            raise ValueError('unsupported template element/attribute: ' + tag)
        role = e.get('class', role)
        if role is not None and role not in mapping:
            raise ValueError('unmapped template role: ' + role)
        paints = dict(inherited)
        for key in ('fill','stroke','stop-color'):
            if key in e.attrib:
                paints[key] = e.get(key)
        keys = ('stop-color',) if tag == 'stop' else ('fill','stroke') if tag in SHAPES else ()
        for key in keys:
            paint = paints.get(key, 'none' if key == 'stroke' else 'black')
            if paint == 'currentColor':
                if role is None:
                    raise ValueError('unclassified currentColor')
                e.set(key, values[mapping[role]])
                used.add(role)
            elif paint == 'none' and key != 'stop-color':
                e.set(key, paint)
            elif re.fullmatch(r'url\(#[\w-]+\)', paint) and paint[5:-1] in gradients and key != 'stop-color':
                e.set(key, paint)
            else:
                raise ValueError('unclassified template paint: ' + paint)
        for child in e:
            walk(child, paints, role)
        # Flatten inherited paint on shapes; remove authoring classes from all nodes.
        e.attrib.pop('class', None)
        if tag not in SHAPES and tag != 'stop':
            for key in ('fill','stroke','stop-color'):
                e.attrib.pop(key, None)
    walk(root, {})
    if used != set(mapping):
        raise ValueError('unused template class mapping')
    styles[0].text = '\n' + '\n'.join(f' .ColorScheme-{r} {{ color:{v}; }}' for r,v in semantic.items()) + '\n'
    return ET.tostring(root, encoding='unicode') + '\n'


def generate(base, item, values, variant):
    config = json.loads((base / 'metadata/palettes.json').read_text())
    result = resolve((base / item['source']).read_text(), item, values, config[variant])
    validate_frozen(result)
    return result


def default_output(base, item, variant):
    config = json.loads((base / 'metadata/palettes.json').read_text())
    preset = 'holonight-' + variant
    return generate(base, item, config['presets'][preset], variant)


def validate_frozen(text):
    root = ET.fromstring(text)
    styles = [e for e in root.iter() if local(e) == 'style']
    roles = {'Text','Background','Highlight','HighlightedText','PositiveText','NeutralText','NegativeText'}
    if len(styles) != 1 or styles[0].get('id') != 'current-color-scheme' or styles[0].get('type') != 'text/css':
        raise ValueError('frozen artwork requires semantic guard')
    css = styles[0].text or ''
    rules = RULE.findall(css)
    if RULE.sub('', css).strip() or {c for c,v in rules} != {'ColorScheme-'+r for r in roles} or len(rules) != len(roles):
        raise ValueError('invalid frozen stylesheet guard')
    gradients = {e.get('id') for e in root.iter() if local(e) in {'linearGradient','radialGradient'}}
    for e in root.iter():
        if local(e) not in TAGS or set(e.attrib) - ATTRS:
            raise ValueError('unsupported frozen element or attribute')
        if 'class' in e.attrib or any('currentColor' in v for v in e.attrib.values()):
            raise ValueError('frozen artwork retains responsive paints')
        for key in ('fill','stroke','stop-color'):
            if key in e.attrib and not (COLOR.fullmatch(e.get(key)) or e.get(key) == 'none' or re.fullmatch(r'url\(#[\w-]+\)', e.get(key))):
                raise ValueError('invalid frozen paint')
    def walk(e, inherited):
        paints = {**inherited, **{k:v for k,v in e.attrib.items() if k in ('fill','stroke','stop-color')}}
        keys = ('stop-color',) if local(e) == 'stop' else ('fill','stroke') if local(e) in SHAPES else ()
        for key in keys:
            value = paints.get(key, 'none' if key == 'stroke' else 'black')
            if COLOR.fullmatch(value) or (key != 'stop-color' and value == 'none'):
                continue
            if key != 'stop-color' and re.fullmatch(r'url\(#[\w-]+\)', value) and value[5:-1] in gradients:
                continue
            raise ValueError('implicit or unresolved frozen paint')
        for child in e:
            walk(child, paints)
    walk(root, {})
