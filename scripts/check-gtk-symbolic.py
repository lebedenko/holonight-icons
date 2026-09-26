#!/usr/bin/env python3
"""Exercise GTK's actual symbolic lookup and foreground recoloring."""

import argparse
from functools import lru_cache
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]
SIZES = (16, 20, 22, 24, 32, 48, 64, 96, 128, 256, 512)
COLORS = ('#e61933', '#19bfe6')
ROLE_COLORS = ('#20d030', '#e5c020', '#f02020')


def require_dependencies():
    missing = []
    if importlib.util.find_spec('gi') is None:
        missing.append('Python GObject introspection (python3-gi)')
    else:
        for version in ('3.0', '4.0'):
            probe = subprocess.run(
                [sys.executable, '-c',
                 f'import gi; gi.require_version("Gtk", "{version}"); from gi.repository import Gtk'],
                capture_output=True)
            if probe.returncode:
                missing.append(f'GTK {version} introspection (gir1.2-gtk-{version})')
    if shutil.which('xvfb-run') is None:
        missing.append('Xvfb (xvfb and xvfb-run)')
    if missing:
        raise RuntimeError('GTK symbolic check needs: ' + ', '.join(missing) +
                           '. Install these packages and rerun task verify.')


def cases():
    names = []
    aliases = []
    for context in ('places', 'devices'):
        spec = json.loads((ROOT / 'metadata' / f'{context}.json').read_text())
        names += [name for name in spec['proof_names'] if name.endswith('-symbolic')]
        if context == 'devices':
            names += [name + '-symbolic' for name in spec['proof_names']]
        aliases += [Path(path).stem for path in spec['lookup_aliases']
                    if '/symbolic/' in path and path.endswith('-symbolic.svg')]
    assert len(names) == 20 and len(set(names)) == 20
    result = {(name, size, 1) for name in set(names + aliases) for size in (24, 32)}
    for name in ('folder-home-symbolic', 'drive-harddisk-symbolic'):
        result.update((name, size, scale) for size in SIZES for scale in (1, 2))
    return sorted(result)


def pixels(pixbuf):
    raw = pixbuf.get_pixels()
    channels = pixbuf.get_n_channels()
    stride = pixbuf.get_rowstride()
    for y in range(pixbuf.get_height()):
        for x in range(pixbuf.get_width()):
            i = y * stride + x * channels
            alpha = raw[i + 3] if channels == 4 else 255
            if alpha >= 224:
                yield tuple(raw[i:i + 3])


def check_color(first, second, label):
    a, b = list(pixels(first)), list(pixels(second))
    if not a or not b:
        raise AssertionError(f'{label}: no opaque visible pixels')
    mean = lambda samples: [sum(p[c] for p in samples) / len(samples) for c in range(3)]
    red, cyan = mean(a), mean(b)
    if not (red[0] > red[1] + 70 and cyan[2] > cyan[0] + 70 and
            red[0] > cyan[0] + 70 and cyan[2] > red[2] + 70):
        raise AssertionError(f'{label}: foreground recoloring failed: {red} → {cyan}')


@lru_cache(maxsize=None)
def check_semantic_source(path):
    from validate_icons import validate_svg
    errors = validate_svg(path)
    if errors:
        raise AssertionError(f'{path}: fixed or invalid symbolic paint: {errors}')


def gtk3(theme, test_cases, root):
    import gi
    gi.require_version('Gtk', '3.0')
    gi.require_version('Gdk', '3.0')
    from gi.repository import Gtk, Gdk
    icon_theme = Gtk.IconTheme.new()
    icon_theme.set_search_path([str(root)])
    icon_theme.set_custom_theme(theme)
    colors = [Gdk.RGBA() for _ in COLORS]
    for color, value in zip(colors, COLORS):
        color.parse(value)
    roles = [Gdk.RGBA() for _ in ROLE_COLORS]
    for color, value in zip(roles, ROLE_COLORS):
        color.parse(value)
    for name, size, scale in test_cases:
        label = f'GTK 3 {theme} {name} {size}px @{scale}x'
        info = icon_theme.lookup_icon_for_scale(name, size, scale, Gtk.IconLookupFlags.FORCE_SIZE)
        if info is None or not info.is_symbolic():
            raise AssertionError(f'{label}: missing or not recognized as symbolic')
        path = Path(info.get_filename()).resolve()
        if not path.is_relative_to((root / theme).resolve()):
            raise AssertionError(f'{label}: lookup escaped generated theme: {path}')
        check_semantic_source(path)
        try:
            rendered = [info.load_symbolic(color, *roles) for color in colors]
        except Exception as exc:
            raise RuntimeError(f'{label}: GTK could not render SVG ({exc}); '
                               'install the SVG pixbuf loader (Ubuntu: librsvg2-common)') from exc
        if not all(was_symbolic for _, was_symbolic in rendered):
            raise AssertionError(f'{label}: GTK did not render symbolically')
        check_color(rendered[0][0], rendered[1][0], label)


def gtk4(theme, test_cases, root):
    import gi
    gi.require_version('Gtk', '4.0')
    gi.require_version('Gdk', '4.0')
    from gi.repository import Gtk, Gdk, GdkPixbuf, Gsk
    icon_theme = Gtk.IconTheme.new()
    icon_theme.set_search_path([str(root)])
    icon_theme.set_theme_name(theme)
    window = Gtk.Window()
    window.realize()
    renderer = Gsk.Renderer.new_for_surface(window.get_surface())
    if renderer is None:
        raise RuntimeError('GTK 4 could not create a renderer; check the Xvfb display')
    colors = [Gdk.RGBA() for _ in COLORS]
    for color, value in zip(colors, COLORS):
        color.parse(value)
    roles = [Gdk.RGBA() for _ in ROLE_COLORS]
    for color, value in zip(roles, ROLE_COLORS):
        color.parse(value)
    for name, size, scale in test_cases:
        label = f'GTK 4 {theme} {name} {size}px @{scale}x'
        paintable = icon_theme.lookup_icon(name, None, size, scale,
                                          Gtk.TextDirection.NONE, 0)
        if paintable is None or not paintable.is_symbolic():
            raise AssertionError(f'{label}: missing or not recognized as symbolic')
        file = paintable.get_file()
        path = Path(file.get_path()).resolve() if file else None
        if path is None or not path.is_relative_to((root / theme).resolve()):
            raise AssertionError(f'{label}: lookup escaped generated theme: {path}')
        check_semantic_source(path)
        rendered = []
        for color in colors:
            snapshot = Gtk.Snapshot.new()
            paintable.snapshot_symbolic(snapshot, size * scale, size * scale,
                                        [color, *roles])
            node = snapshot.to_node()
            if node is None:
                raise AssertionError(f'{label}: empty GTK 4 snapshot')
            png = renderer.render_texture(node).save_to_png_bytes()
            loader = GdkPixbuf.PixbufLoader.new_with_type('png')
            loader.write(png.get_data())
            loader.close()
            rendered.append(loader.get_pixbuf())
        check_color(*rendered, label)
    renderer.unrealize()
    window.destroy()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--gtk', choices=('3', '4'))
    parser.add_argument('--theme')
    parser.add_argument('--search-path', type=Path)
    parser.add_argument('--themes-dir', type=Path, default=ROOT / 'build')
    parser.add_argument('--only-name', help='limit cases for debugging a symbolic icon')
    args = parser.parse_args()
    test_cases = cases()
    if args.only_name:
        test_cases = [case for case in test_cases if case[0] == args.only_name]
        if not test_cases:
            parser.error(f'unknown symbolic name: {args.only_name}')
    if args.gtk:
        if not args.theme or not args.search_path:
            parser.error('--gtk requires --theme and --search-path')
        (gtk3 if args.gtk == '3' else gtk4)(args.theme, test_cases, args.search_path)
        print(f'GTK {args.gtk} {args.theme}: {len(test_cases)} symbolic lookups and two-color renders passed')
        return
    require_dependencies()
    for theme in ('HoloNight', 'HoloNight-Dark'):
        if not (args.themes_dir / theme / 'index.theme').is_file():
            raise RuntimeError(f'Missing generated {theme}; run task build first')
    with tempfile.TemporaryDirectory(prefix='holonight-gtk-') as temp:
        icon_root = Path(temp) / 'icons'
        icon_root.mkdir()
        for theme in ('HoloNight', 'HoloNight-Dark'):
            (icon_root / theme).symlink_to(args.themes_dir.resolve() / theme,
                                           target_is_directory=True)
        env = os.environ.copy()
        env['XDG_DATA_HOME'] = temp
        for gtk in ('3', '4'):
            for theme in ('HoloNight', 'HoloNight-Dark'):
                command = ['xvfb-run', '-a', sys.executable, __file__, '--gtk', gtk,
                           '--theme', theme, '--search-path', str(icon_root)]
                if args.only_name:
                    command += ['--only-name', args.only_name]
                subprocess.run(command,
                               check=True, env=env)


if __name__ == '__main__':
    try:
        main()
    except (AssertionError, RuntimeError) as error:
        sys.exit(str(error))
