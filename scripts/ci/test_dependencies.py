#!/usr/bin/env python3
"""Offline regressions for installed prerequisites and prepared renderer isolation."""
import json
import hashlib
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
import dependencies
import external


class DependenciesTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix='icons prerequisites with spaces ')
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.config = json.loads((ROOT / 'tooling/module.json').read_text())
        (self.root / 'tooling').mkdir()
        (self.root / 'tooling/module.json').write_text(json.dumps(self.config))
        self.selected = {'VERIFY_RENDERERS': True, 'VERIFY_KDE': False}

    def package(self, name='Qt6', version='6.11.0', targets=('Qt6::Core', 'Qt6::Gui', 'Qt6::Svg')):
        directory = self.root / 'lib/cmake' / name
        directory.mkdir(parents=True, exist_ok=True)
        (directory / (name + 'Config.cmake')).write_text(
            f'set({name}_VERSION "{version}")\n' + '\n'.join(f'add_library({target} INTERFACE IMPORTED)' for target in targets))
        (directory / (name + 'ConfigVersion.cmake')).write_text(
            f'set(PACKAGE_VERSION "{version}")\n'
            'if(PACKAGE_VERSION VERSION_LESS PACKAGE_FIND_VERSION)\nset(PACKAGE_VERSION_COMPATIBLE FALSE)\n'
            'else()\nset(PACKAGE_VERSION_COMPATIBLE TRUE)\nendif()\n')
        return directory

    def probe(self, dependency):
        config = {'module': 'icons-probe', 'external_dependencies': [dependency]}
        source = self.root / 'probe'
        source.mkdir(exist_ok=True)
        text = external.probe_source([config], ('test',))
        # Isolate package discovery after compiler/tool discovery; no host Qt/KF6 may mask failures.
        text = text.replace('# icons-probe:',
                            'set(CMAKE_FIND_USE_CMAKE_SYSTEM_PATH FALSE)\n'
                            'set(CMAKE_FIND_USE_SYSTEM_ENVIRONMENT_PATH FALSE)\n# icons-probe:')
        (source / 'CMakeLists.txt').write_text(text)
        return subprocess.run(['cmake', '-S', str(source), '-B', str(source / 'build'), '-G', 'Ninja',
                               '-DCMAKE_PREFIX_PATH=' + str(self.root)], capture_output=True, text=True)

    def test_old_qt_is_rejected(self):
        self.package(version='6.10.3')
        result = self.probe({'id': 'qt', 'scope': ['test'], 'components': ['Core', 'Gui', 'Svg']})
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('6.11', result.stderr)

    def test_missing_qt_is_rejected(self):
        result = self.probe({'id': 'qt', 'scope': ['test'], 'components': ['Core', 'Gui', 'Svg']})
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('Qt6', result.stderr)

    def test_missing_qt_target_is_rejected(self):
        self.package(targets=('Qt6::Core', 'Qt6::Gui'))
        result = self.probe({'id': 'qt', 'scope': ['test'], 'components': ['Core', 'Gui', 'Svg'],
                             'targets': ['Qt6::Core', 'Qt6::Gui', 'Qt6::Svg']})
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('Qt6::Svg', result.stderr)

    def test_enabled_kde_requires_icon_themes_target(self):
        self.package('KF6IconThemes', targets=())
        result = self.probe({'id': 'kiconthemes', 'scope': ['test'], 'targets': ['KF6::IconThemes']})
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('KF6::IconThemes', result.stderr)

    def test_enabled_kde_missing_package_fails(self):
        result = self.probe({'id': 'kiconthemes', 'scope': ['test'], 'targets': ['KF6::IconThemes']})
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('KF6IconThemes', result.stderr)

    def test_missing_gtk_packages_fail_without_acquisition(self):
        empty = self.root / 'empty-pkg-config'
        empty.mkdir()
        for dependency, package in (('gtk3', 'gtk+-3.0'), ('gtk4', 'gtk4')):
            with self.subTest(package=package), patch.dict(os.environ,
                    {'PKG_CONFIG_LIBDIR': str(empty), 'PKG_CONFIG_PATH': ''}):
                result = self.probe({'id': dependency, 'scope': ['test']})
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(package, result.stdout + result.stderr)

    def test_disabled_renderers_do_not_probe_or_prepare(self):
        with patch.dict(os.environ, {'VERIFY_RENDERERS': 'OFF', 'VERIFY_KDE': 'OFF'}), \
             patch.object(dependencies, 'check') as check, patch.object(dependencies.subprocess, 'run') as run:
            dependencies.installed(dependencies.features())
        check.assert_not_called()
        run.assert_not_called()
        ids = {item['id'] for item in external.requirements(self.config, ('test',),
                                                          {'VERIFY_RENDERERS': False, 'VERIFY_KDE': False})}
        self.assertEqual(ids, set())

    def test_production_profiles_exclude_renderer_prerequisites(self):
        for distribution in ('arch', 'debian'):
            packages = external.package_names([self.config], distribution)
            expected = ['hicolor-icon-theme', 'python'] if distribution == 'arch' else ['hicolor-icon-theme', 'python3']
            self.assertEqual(packages, expected)

    def test_renderer_prerequisite_failures_are_actionable(self):
        for failed in ('Python Cairo', 'GTK 3 introspection', 'GTK 4 introspection', 'SVG/PNG image loaders', 'DejaVu test font', 'Xvfb'):
            with self.subTest(failed=failed):
                counter = iter(('Python Cairo', 'GTK 3 introspection', 'GTK 4 introspection', 'SVG/PNG image loaders', 'DejaVu test font', 'Xvfb'))
                def probe(command, **kwargs):
                    label = next(counter)
                    return subprocess.CompletedProcess(command, int(label == failed),
                                                       '/usr/share/fonts/TTF/DejaVuSans.ttf' if label.endswith('font') else '', 'fixture failure')
                with patch.object(dependencies.subprocess, 'run', side_effect=probe), \
                     patch.object(Path, 'is_file', return_value=True):
                    with self.assertRaisesRegex(RuntimeError, failed):
                        dependencies.renderer_prerequisites()

    def test_missing_preparation_preserves_stale_cache_and_never_prepares(self):
        stale = self.root / 'build/rendering/CMakeCache.txt'
        stale.parent.mkdir(parents=True)
        stale.write_text('stale cache')
        with patch.object(dependencies, 'ROOT', self.root), patch.object(dependencies, 'prepare') as prepare, \
             patch.object(dependencies.subprocess, 'run') as run:
            with self.assertRaisesRegex(RuntimeError, 'Missing prepared renderer'):
                dependencies.render([])
            prepare.assert_not_called()
            run.assert_not_called()
        self.assertEqual(stale.read_text(), 'stale cache')

    def test_preparation_requires_explicit_source_and_archives_incompatible_artifacts(self):
        identity = {'revision': 'fixture', 'files': {'src/icons/iconrenderer.cpp':
                    hashlib.sha256(b'approved').hexdigest()}}
        supplied = self.root / 'source with spaces'
        (supplied / 'src/icons').mkdir(parents=True)
        (supplied / 'src/icons/iconrenderer.cpp').write_bytes(b'approved')
        old = self.root / 'build/deps'
        old.mkdir(parents=True)
        (old / 'renderer-state.json').write_text('{}')
        (old / 'important').write_text('preserve')
        stale = self.root / 'build/rendering'
        stale.mkdir()
        (stale / 'CMakeCache.txt').write_text('preserve cache')
        with patch.object(dependencies, 'ROOT', self.root), \
             patch.object(dependencies, 'fixture_identity', return_value=identity), \
             patch.object(dependencies, 'installed', return_value={'features': self.selected}), \
             patch.dict(os.environ, {}, clear=True):
            with self.assertRaisesRegex(RuntimeError, 'HOLONIGHT_QT_SOURCE'):
                dependencies.prepare(self.selected)
            self.assertTrue((old / 'important').exists())
            os.environ['HOLONIGHT_QT_SOURCE'] = str(supplied)
            dependencies.prepare(self.selected)
            self.assertEqual(dependencies.prepared_renderer() / 'src/icons/iconrenderer.cpp', old / 'renderer/src/icons/iconrenderer.cpp')
            self.assertEqual((self.root / 'build/deps.previous-1/important').read_text(), 'preserve')
            self.assertEqual((self.root / 'build/rendering.previous-1/CMakeCache.txt').read_text(), 'preserve cache')


if __name__ == '__main__':
    unittest.main()
