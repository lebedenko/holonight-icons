"""Regression fixtures for effective SVG paints, theme metadata and installation."""
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from build import build
from install import install
from theme import BUILD, SOURCE, VARIANTS, PLACES, DEVICES, PALETTES, STYLE, directories, recolor
from validate_icons import alias_errors, validate_source, validate_svg, validate_theme


class SvgTests(unittest.TestCase):
    def fixture(self, name, exemption=None):
        return validate_svg(ROOT / 'tests/fixtures' / name, exemption, 24)

    def test_inherited_group(self):
        self.assertEqual(self.fixture('inherited.svg'), [])

    def test_missing_id(self):
        self.assertTrue(self.fixture('missing-id.svg'))

    def test_hardcoded_semantic(self):
        self.assertTrue(self.fixture('hardcoded.svg'))

    def test_implicit_paint(self):
        self.assertTrue(self.fixture('implicit.svg'))

    def test_inline_override(self):
        self.assertTrue(self.fixture('inline-override.svg'))

    def test_missing_role(self):
        self.assertTrue(self.fixture('missing-role.svg'))

    def test_no_class(self):
        self.assertTrue(self.fixture('no-class.svg'))

    def test_fixed_art(self):
        self.assertFalse(self.fixture('fixed.svg', {'scope':'asset','rationale':'Brand mark'}))
        self.assertTrue(self.fixture('fixed.svg'))

    def test_stale_exemption(self):
        self.assertTrue(self.fixture('inherited.svg', {'scope':'asset'}))
        self.assertTrue(self.fixture('inherited.svg', {'scope':'elements','ids':['removed']}))

    def test_mixed_exemption(self):
        self.assertFalse(self.fixture('mixed.svg', {'scope':'elements','ids':['shadow']}))
        self.assertTrue(self.fixture('mixed.svg'))

    def test_stale_mixed_paint_and_fixed_guard(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'fixture.svg'
            text = (ROOT / 'tests/fixtures/mixed.svg').read_text()
            path.write_text(text.replace('fill="#112233"', 'fill="none"'))
            self.assertIn('stale element exemption', validate_svg(path, {'scope':'elements','ids':['shadow']}))
            text = (ROOT / 'tests/fixtures/fixed.svg').read_text()
            path.write_text(text.replace('current-color-scheme', 'unrecognized-style'))
            self.assertTrue(validate_svg(path, {'scope':'asset'}))

    def test_single_quoted_stylesheet_generation(self):
        text = (ROOT / 'tests/fixtures/inherited.svg').read_text().replace('"', "'")
        self.assertIn('color:'+PALETTES['dark']['Text'], recolor(text,'dark'))


class ThemeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        build()

    def test_inventory_and_variants(self):
        self.assertEqual(validate_source(), [])
        for name in VARIANTS:
            self.assertEqual(validate_theme(BUILD / name,name), [])

    def test_devices_masters_aliases_and_retirement(self):
        tree = SOURCE / 'devices'
        self.assertEqual({p.name for p in tree.iterdir()},
                         {'24', '32', *DEVICES['directory_aliases']})
        for alias, target in DEVICES['directory_aliases'].items():
            self.assertEqual(str((tree/alias).readlink()), target)
        self.assertEqual(len(DEVICES['proof_names']), 5)
        for name in DEVICES['proof_names']:
            for size in (24,32):
                self.assertTrue((tree/str(size)/f'{name}.svg').is_file())
            self.assertTrue((tree/'24/symbolic'/f'{name}-symbolic.svg').is_file())
        for rel, target in DEVICES['lookup_aliases'].items():
            self.assertEqual(str((SOURCE/rel).readlink()), target)
        for item in DEVICES['migration_dispositions'].values():
            if item['status'] == 'retired':
                self.assertFalse((SOURCE/item['path']).exists())

    def test_alias_failures(self):
        with tempfile.TemporaryDirectory() as tmp:
            tree=Path(tmp)
            (tree/'broken.svg').symlink_to('missing.svg')
            (tree/'a.svg').symlink_to('b.svg')
            (tree/'b.svg').symlink_to('a.svg')
            (tree/'escape.svg').symlink_to(SOURCE/'actions/24/go-down.svg')
            self.assertEqual(len(alias_errors(tree)),4)

    def test_metadata_and_precedence(self):
        with tempfile.TemporaryDirectory() as tmp:
            tree=Path(tmp)/'HoloNight'
            shutil.copytree(BUILD/'HoloNight',tree,symlinks=True)
            original=(tree/'index.theme').read_text()
            for old,new in [('MinSize=16','MinSize=48'),('FollowsColorScheme=true','FollowsColorScheme=false'),
                            ('Papirus,breeze,hicolor','hicolor,Papirus,breeze'),('Size=24','Size=22')]:
                (tree/'index.theme').write_text(original.replace(old,new))
                self.assertTrue(validate_theme(tree,'HoloNight'))
            import configparser
            config=configparser.ConfigParser()
            config.read_string(original)
            dirs=config['Icon Theme']['Directories']
            (tree/'index.theme').write_text(original.replace(dirs,','.join(reversed(dirs.split(',')))))
            self.assertTrue(validate_theme(tree,'HoloNight'))

    def test_generation_deterministic_and_preserves_artwork(self):
        before={str(p.relative_to(BUILD)):p.read_bytes() for name in VARIANTS for p in (BUILD/name).rglob('*') if p.is_file()}
        build()
        for rel,data in before.items():
            self.assertEqual((BUILD/rel).read_bytes(),data)
        for path in SOURCE.rglob('*.svg'):
            if path.is_symlink(): continue
            text=path.read_text()
            self.assertEqual(STYLE.sub('', recolor(recolor(text,'dark'),'light')), STYLE.sub('', text))

    def test_install_repeat_and_invalid_stage(self):
        with tempfile.TemporaryDirectory() as tmp:
            env={**os.environ,'XDG_DATA_HOME':tmp}
            command=[sys.executable,str(ROOT/'scripts/install.py'),'--no-cache']
            subprocess.run(command,env=env,check=True,stdout=subprocess.DEVNULL)
            base=Path(tmp)/'icons'
            (base/'HoloNight'/'old-marker').write_text('recover me')
            subprocess.run(command,env=env,check=True,stdout=subprocess.DEVNULL)
            self.assertFalse((base/'HoloNight'/'old-marker').exists())
            backups=list(base.glob('.holonight-backup-*'))
            self.assertEqual(len(backups),1)
            self.assertEqual((backups[0]/'HoloNight'/'old-marker').read_text(),'recover me')
            for name in VARIANTS:
                self.assertEqual(validate_theme(base/name,name),[])
            with patch('install.validate_theme',return_value=['invalid stage']):
                with self.assertRaises(ValueError): install(base,refresh=False)
            self.assertEqual(validate_theme(base/'HoloNight','HoloNight'),[])

    def test_install_rejects_incomplete_or_symlinked_bundle(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp) / 'icons'
            install(base, refresh=False)
            marker = base / 'HoloNight' / 'marker'
            marker.write_text('preserve existing installation')
            staged_build = Path(tmp) / 'build'
            shutil.copytree(BUILD / 'holonight-icons', staged_build / 'holonight-icons')
            for name in VARIANTS:
                shutil.copytree(BUILD / name, staged_build / name, symlinks=True)
            script = staged_build / 'holonight-icons/scripts/recolor.py'
            script.unlink()
            with patch('install.BUILD', staged_build):
                with self.assertRaisesRegex(ValueError, 'inventory'):
                    install(base, refresh=False)
                script.symlink_to(ROOT / 'scripts/recolor.py')
                with self.assertRaisesRegex(ValueError, 'symlinks'):
                    install(base, refresh=False)
            self.assertEqual(marker.read_text(), 'preserve existing installation')
            self.assertFalse(list(base.glob('.holonight-backup-*')))
            self.assertTrue((base.parent / 'holonight-icons/scripts/recolor.py').is_file())

    def test_install_rolls_back_both_variants(self):
        with tempfile.TemporaryDirectory() as tmp:
            base=Path(tmp)/'icons'
            install(base,refresh=False)
            for name in VARIANTS: (base/name/'marker').write_text(name)
            original=Path.rename
            def fail_second(path,target):
                if '.holonight-stage-' in str(path) and path.name=='HoloNight-Dark':
                    raise OSError('simulated failure')
                return original(path,target)
            with patch.object(Path,'rename',fail_second):
                with self.assertRaises(OSError): install(base,refresh=False)
            for name in VARIANTS:
                self.assertEqual((base/name/'marker').read_text(),name)

class PlacesTests(unittest.TestCase):
    def test_declared_directory_links_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            tree = Path(tmp)
            (tree/'places/24').mkdir(parents=True)
            link = tree/'places/20'
            link.symlink_to('24')
            self.assertEqual(alias_errors(tree), [])
            for target in ('../places/24', '/tmp', '20', 'missing'):
                link.unlink()
                link.symlink_to(target)
                self.assertTrue(alias_errors(tree), target)
            link.unlink()
            (tree/'places/30').symlink_to('24')
            self.assertTrue(alias_errors(tree))

    def test_home_structure_and_generated_metadata(self):
        expected = {*map(str, PLACES['authored_sizes']), *PLACES['directory_aliases']}
        for tree in [SOURCE, *(BUILD/name for name in VARIANTS)]:
            self.assertEqual({p.name for p in (tree/'places').iterdir()}, expected)
            self.assertEqual({str(p.relative_to(tree/'places')) for p in (tree/'places').rglob('*.svg')},
                             {f'{size}/{name}.svg' for name in PLACES['proof_names']
                              if not name.endswith('-symbolic') for size in (24,32)} |
                             {f'24/symbolic/{name}.svg' for name in PLACES['proof_names']
                              if name.endswith('-symbolic')} |
                             {p.removeprefix('places/') for p in PLACES['lookup_aliases']})
            self.assertEqual({d for d in directories(tree) if d.startswith('places/')},
                             {'places/'+s for s in expected} | {'places/'+s+'/symbolic' for s in ('16','20','22','24')})
            for size in (24,32):
                self.assertFalse((tree/f'places/{size}').is_symlink())
                self.assertTrue((tree/f'places/{size}/.gitkeep').is_file())
            for alias, target in PLACES['directory_aliases'].items():
                self.assertEqual(str((tree/'places'/alias).readlink()),target)

    def test_folder_preserves_approved_home_body(self):
        # Exact text comparison also protects gradient definitions and drawing order.
        for size in (24, 32):
            removed = {'house'}
            if size == 32:
                removed.update({'path14', *(f'house-glow-{i}' for i in range(1, 9))})
            home = (SOURCE/f'places/{size}/folder-home.svg').read_text()
            body = ''.join(line for line in home.splitlines(keepends=True)
                           if not any(f'id="{name}"' in line for name in removed))
            self.assertEqual((SOURCE/f'places/{size}/folder.svg').read_text(), body)

    def test_download_preserves_approved_folder_body(self):
        for size in (24, 32):
            download = (SOURCE/f'places/{size}/folder-download.svg').read_text()
            body = ''.join(line for line in download.splitlines(keepends=True)
                           if 'id="download' not in line)
            self.assertEqual(body, (SOURCE/f'places/{size}/folder.svg').read_text())

    def test_documents_preserves_approved_folder_body(self):
        for size in (24, 32):
            documents = (SOURCE/f'places/{size}/folder-documents.svg').read_text()
            body = ''.join(line for line in documents.splitlines(keepends=True)
                           if 'id="documents' not in line)
            self.assertEqual(body, (SOURCE/f'places/{size}/folder.svg').read_text())

    def test_extended_folder_family(self):
        from xml.etree import ElementTree as ET
        from templates import manifest
        entries = {e['source'] for e in manifest(ROOT)}
        for name in ('desktop', 'pictures', 'music', 'videos', 'projects', 'templates', 'public', 'recent', 'trash', 'trash-full'):
            for size in (24,32):
                with self.subTest(name=name, size=size):
                    path = f'places/{size}/folder-{name}.svg'
                    self.assertIn('icons/'+path, entries)
                    artwork = (SOURCE/path).read_text()
                    body = ''.join(line for line in artwork.splitlines(keepends=True)
                                   if f'id="{name}' not in line)
                    self.assertEqual(body, (SOURCE/f'places/{size}/folder.svg').read_text())
                    layers = [e for e in ET.fromstring(artwork).iter()
                              if e.get('id', '').startswith(name)]
                    self.assertEqual(len(layers), 9 if size == 32 else 1)
                    self.assertTrue(all(e.get('stroke') == 'url(#rim)' for e in layers))
                    self.assertTrue(all(e.get('d') == layers[-1].get('d') for e in layers))
                    if size == 32:
                        self.assertEqual([e.get('opacity') for e in layers[:-1]],
                                         ['.018','.022','.028','.035','.045','.055','.07','.09'])
            symbolic = SOURCE/f'places/24/symbolic/folder-{name}-symbolic.svg'
            self.assertEqual(validate_svg(symbolic), [])
        for alias, target in PLACES['lookup_aliases'].items():
            self.assertTrue((SOURCE/alias).is_symlink())
            self.assertEqual(str((SOURCE/alias).readlink()), target)

    def test_missing_master_alias_and_migration(self):
        with tempfile.TemporaryDirectory() as tmp:
            tree = Path(tmp)/'icons'
            shutil.copytree(SOURCE, tree, symlinks=True)
            for size in (24,32):
                p = tree/f'places/{size}'
                shutil.rmtree(p)
                self.assertTrue(validate_source(tree))
                p.symlink_to('32' if size==24 else '24')
                self.assertTrue(validate_source(tree))
                p.unlink(); p.mkdir(); (p/'.gitkeep').touch()
            p = tree/'places/20'
            p.unlink(); p.mkdir()
            self.assertTrue(validate_source(tree))
            p.rmdir(); p.symlink_to('32')
            self.assertTrue(validate_source(tree))
            p.unlink(); p.symlink_to('24')
            p = tree/'places/30'
            p.mkdir()
            self.assertTrue(validate_source(tree))
            p.rmdir()
            for size in (24,32):
                shutil.copytree(SOURCE/f'places/{size}', tree/f'places/{size}', symlinks=True, dirs_exist_ok=True)
            self.assertEqual(validate_source(tree), [])
            p = tree/'places/24/user-home.svg'
            p.unlink()
            shutil.copy2(ROOT/'tests/fixtures/inherited.svg',p)
            self.assertTrue(validate_source(tree))
            p.unlink()
            (tree/'actions/24/go-down.svg').unlink()
            self.assertTrue(validate_source(tree))


if __name__ == '__main__':
    unittest.main()
