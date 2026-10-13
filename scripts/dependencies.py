#!/usr/bin/env python3
"""Validate installed tools and explicitly prepare the approved renderer source fixture."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tooling'))
from external import check, external_prefix


def features():
    selected = json.loads((ROOT / 'tooling/module.json').read_text())['external_features'].copy()
    for name in selected:
        value = os.environ.get(name, 'ON' if selected[name] else 'OFF').upper()
        if value not in ('ON', 'OFF'):
            raise RuntimeError(f'{name} must be ON or OFF')
        selected[name] = value == 'ON'
    return selected


def archive(path):
    if path.exists():
        number = 1
        while path.with_name(path.name + '.previous-' + str(number)).exists():
            number += 1
        path.rename(path.with_name(path.name + '.previous-' + str(number)))


def fixture_identity():
    return json.loads((ROOT / 'scripts/renderer-fixture.json').read_text())


def validate_fixture(source):
    for name, expected in fixture_identity()['files'].items():
        path = source / name
        if not path.is_file() or path.is_symlink() or hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise RuntimeError(f'Renderer fixture mismatch: {name}; run task deps with HOLONIGHT_QT_SOURCE explicitly.')


def renderer_prerequisites():
    probes = {
        'Python Cairo': 'import cairo',
        'GTK 3 introspection': 'import gi; gi.require_version("Gtk", "3.0"); from gi.repository import Gtk',
        'GTK 4 introspection': 'import gi; gi.require_version("Gtk", "4.0"); from gi.repository import Gtk',
        'SVG/PNG image loaders': 'import gi; gi.require_version("GdkPixbuf", "2.0"); from gi.repository import GdkPixbuf; '
                                 'assert {"svg", "png"} <= {f.get_name() for f in GdkPixbuf.Pixbuf.get_formats()}',
    }
    for label, code in probes.items():
        result = subprocess.run([sys.executable, '-c', code], capture_output=True, text=True)
        if result.returncode:
            raise RuntimeError(f'Missing {label}; install renderer prerequisites explicitly.\n{result.stderr}')
    for command, label in [(['fc-match', '-f', '%{file}', 'DejaVu Sans'], 'DejaVu test font'),
                            (['xvfb-run', '-a', '/bin/true'], 'Xvfb')]:
        try:
            result = subprocess.run(command, capture_output=True, text=True)
        except FileNotFoundError as error:
            raise RuntimeError(f'Missing {label}; install renderer prerequisites explicitly.') from error
        if result.returncode or (label.endswith('font') and
                                ('DejaVuSans' not in result.stdout or not Path(result.stdout).is_file())):
            raise RuntimeError(f'Missing {label}; install renderer prerequisites explicitly.\n{result.stderr}')


def installed(selected):
    if sys.version_info < (3, 10):
        raise RuntimeError('Python >=3.10 is required')
    # Generation and production staging use Python alone; never probe renderer tools for minimal profiles.
    result = {'python': sys.version, 'features': selected,
              'environment': {name: os.environ.get(name) for name in
                              ('CC', 'CXX', 'CFLAGS', 'CXXFLAGS', 'LDFLAGS', 'CMAKE_PREFIX_PATH', 'Qt6_DIR', 'HOLONIGHT_EXTERNAL_PREFIX')}}
    if selected['VERIFY_RENDERERS'] or selected['VERIFY_KDE']:
        config = json.loads((ROOT / 'tooling/module.json').read_text())
        if selected['VERIFY_KDE'] and not selected['VERIFY_RENDERERS']:
            config = dict(config, external_dependencies=[dict(item, feature='VERIFY_KDE') if item['id'] == 'qt' else item
                                                        for item in config['external_dependencies']])
        result['external'] = check(config, scopes=('tool', 'test'), features=selected)
        result['tools'] = {tool: subprocess.check_output([tool, '--version'], text=True).splitlines()[0]
                           for tool in ('cmake', 'c++')}
    if selected['VERIFY_RENDERERS']:
        renderer_prerequisites()
    return result


def prepare(selected):
    evidence = installed(selected)
    state = {'fixture': fixture_identity() if selected['VERIFY_RENDERERS'] else None, 'installed': evidence}
    destination = ROOT / 'build/deps'
    previous = destination / 'renderer-state.json'
    supplied = None
    if selected['VERIFY_RENDERERS']:
        value = os.environ.get('HOLONIGHT_QT_SOURCE')
        if not value:
            raise RuntimeError('Set HOLONIGHT_QT_SOURCE to a local checkout of the approved renderer revision before task deps.')
        supplied = Path(value).resolve()
        # The approved content is the contract; exports and checkouts containing that revision are both supported.
        validate_fixture(supplied)
    if destination.exists() and (not previous.is_file() or json.loads(previous.read_text()) != state):
        archive(destination)
        archive(ROOT / 'build/rendering')
        archive(ROOT / 'build/kde')
    destination.mkdir(parents=True, exist_ok=True)
    if supplied:
        fixture = destination / 'renderer'
        if fixture.exists():
            try:
                validate_fixture(fixture)
            except RuntimeError:
                archive(fixture)
        if not fixture.exists():
            with tempfile.TemporaryDirectory(prefix='renderer-', dir=destination) as temporary:
                exported = Path(temporary)
                for name in fixture_identity()['files']:
                    target = exported / name
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(supplied / name, target)
                validate_fixture(exported)
                exported.rename(fixture)
    previous.write_text(json.dumps(state, indent=2) + '\n')
    print('Installed prerequisites validated; approved renderer fixture prepared.' if supplied else 'Python-only prerequisites validated.')


def prepared_renderer():
    state = ROOT / 'build/deps/renderer-state.json'
    if not state.is_file():
        raise RuntimeError('Missing prepared renderer fixture; run task deps with HOLONIGHT_QT_SOURCE explicitly.')
    data = json.loads(state.read_text())
    if data['fixture'] != fixture_identity() or data['installed']['features'] != features():
        raise RuntimeError('Incompatible prepared renderer identity; run task deps explicitly.')
    fixture = ROOT / 'build/deps/renderer'
    validate_fixture(fixture)
    return fixture


def render(arguments):
    selected = features()
    if not selected['VERIFY_RENDERERS']:
        raise RuntimeError('Qt rendering requires VERIFY_RENDERERS=ON and explicit task deps preparation.')
    fixture = prepared_renderer()
    # Offline discovery remains authoritative; preserve stale build trees when the selected installation changes.
    evidence = installed(selected)
    if evidence != json.loads((ROOT / 'build/deps/renderer-state.json').read_text())['installed']:
        raise RuntimeError('Installed prerequisite identity changed; run task deps explicitly.')
    options = ['-DHOLONIGHT_RENDERER_FIXTURE=' + str(fixture)]
    if external_prefix():
        options += ['-DCMAKE_PREFIX_PATH=' + str(external_prefix())]
    build = ROOT / 'build/rendering'
    subprocess.run(['cmake', '-S', str(ROOT / 'tests/rendering'), '-B', str(build), *options], check=True)
    subprocess.run(['cmake', '--build', str(build), '--parallel', os.environ.get('JOBS', '2')], check=True)
    subprocess.run([str(build / 'render-check'), str(ROOT / 'build'), *arguments], check=True,
                   env=dict(os.environ, QT_QPA_PLATFORM='offscreen', QT_QPA_PLATFORMTHEME=''))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('prepare', 'check', 'render'))
    args, remaining = parser.parse_known_args()
    try:
        if args.command == 'prepare':
            prepare(features())
        elif args.command == 'check':
            installed(features())
        else:
            render(remaining)
    except (OSError, RuntimeError, subprocess.CalledProcessError, ValueError) as error:
        parser.exit(1, f'error: {error}\n')


if __name__ == '__main__':
    main()
