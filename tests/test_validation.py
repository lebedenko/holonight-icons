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
from theme import BUILD, SOURCE, VARIANTS, APPS, PLACES, DEVICES, ACTIONS, PALETTES, STYLE, directories, recolor
from validate_icons import alias_errors, validate_source, validate_svg, validate_theme, validate_actions, validate_apps


class SvgTests(unittest.TestCase):
    def fixture(self, name, exemption=None):
        return validate_svg(ROOT / 'tests/fixtures' / name, exemption, 24)

    def test_accent_fill_and_stroke_contract(self):
        import json
        exemptions = json.loads((ROOT / 'metadata/fixed-artwork.json').read_text())
        for name in ('application-epub+zip', 'application-json'):
            rel = f'mimetypes/32/{name}.svg'
            original = (ROOT / 'icons' / rel).read_text()
            exemption = exemptions[rel]
            with tempfile.TemporaryDirectory() as tmp:
                path = Path(tmp) / 'icon.svg'
                path.write_text(original)
                self.assertEqual(validate_svg(path, exemption, 32), [])
                mutations = [
                    original.replace(' .ColorScheme-Accent { color:#5ea2ff; }', ''),
                    original.replace('class="ColorScheme-Accent"', 'class="ColorScheme-Unknown"'),
                    original.replace('currentColor', '#112233'),
                    original.replace('id="glyph-shadow"', 'id="removed-shadow"'),
                    original.replace('.ColorScheme-Accent {', '.ColorScheme-Highlight {'),
                ]
                for mutation in mutations:
                    path.write_text(mutation)
                    self.assertTrue(validate_svg(path, exemption, 32))

    def test_reviewed_geometry_matches_import(self):
        import xml.etree.ElementTree as ET
        # Checked-in baseline report captures upstream path data and layer order.
        import json
        baseline = json.loads((ROOT / 'tests/fixtures/mimetype-geometry.json').read_text())
        for name, paths in baseline.items():
            root = ET.fromstring((ROOT / f'icons/mimetypes/32/{name}.svg').read_text())
            actual = [{k: v for k, v in e.attrib.items() if k not in ('id', 'class', 'style')}
                      | {'style': ';'.join(v for v in e.get('style', '').split(';')
                                          if not v.startswith(('fill:', 'stroke:')))}
                      for e in root if e.tag.endswith('path')]
            self.assertEqual(actual, paths)

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

    def test_application_imports_and_aliases(self):
        import hashlib
        for rel, entry in APPS['artwork'].items():
            text = (SOURCE / rel).read_text()
            imported = STYLE.sub('', text)
            # Remove the guard's extra newline to recover the exact supplied SVG.
            imported = imported.replace('>\n\n<title>', '>\n<title>', 1)
            self.assertEqual(hashlib.sha256(imported.encode()).hexdigest(), entry['source_sha256'])
        for rel, target in APPS['lookup_aliases'].items():
            self.assertEqual((SOURCE / rel).readlink(), Path(target))
        for name in VARIANTS:
            import configparser
            config = configparser.ConfigParser()
            config.read(BUILD / name / 'index.theme')
            for section in ('apps/170', 'apps/170/.'):
                self.assertEqual(config[section]['MinSize'], '16')
                self.assertEqual(config[section]['MaxSize'], '512')
            self.assertEqual(config['apps/170/.']['Scale'], '2')

    def test_application_mixed_native_sizes(self):
        from theme import index_text
        with tempfile.TemporaryDirectory() as tmp:
            tree = Path(tmp) / 'icons'
            shutil.copytree(SOURCE, tree, symlinks=True)
            directory = tree / 'apps/256'
            directory.mkdir()
            shutil.copy2(ROOT / 'tests/fixtures/fixed.svg', directory / 'future.svg')
            self.assertEqual(validate_apps(tree), [])
            text = index_text('HoloNight', tree)
            self.assertIn('[apps/256/.]', text)
            self.assertIn('[apps/170/.]', text)

    def test_application_replacement_and_retirement_mutations(self):
        with tempfile.TemporaryDirectory() as tmp:
            tree = Path(tmp) / 'icons'
            shutil.copytree(SOURCE, tree, symlinks=True)
            alias = tree / 'apps/170/holonight-pkg-manager.svg'
            alias.unlink()
            alias.symlink_to('holonight-ai.svg')
            self.assertTrue(any('replacement target' in e for e in validate_apps(tree)))
            shutil.copy2(ROOT / 'tests/fixtures/fixed.svg', tree / 'apps/170/acvc-64.svg')
            self.assertTrue(any('retired name unexpectedly present' in e for e in validate_apps(tree)))

    def test_retired_kiro_logo_is_absent(self):
        retired = 'apps/100/kiro.svg'
        self.assertFalse((SOURCE / retired).exists())
        for name in VARIANTS:
            self.assertFalse((BUILD / name / retired).exists())
        with tempfile.TemporaryDirectory() as tmp:
            tree = Path(tmp) / 'icons'
            shutil.copytree(SOURCE, tree, symlinks=True)
            (tree / retired).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / 'tests/fixtures/inherited.svg', tree / retired)
            self.assertTrue(any('retired name unexpectedly present' in error
                                for error in validate_source(tree)))

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
            self.assertEqual((tree/'24'/f'{name}-symbolic.svg').readlink(), Path(f'{name}.svg'))
            self.assertEqual((tree/'24'/f'{name}.svg').read_bytes(),
                             (tree/'24/symbolic'/f'{name}-symbolic.svg').read_bytes())
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
                             {f'24/{name}.svg' for name in PLACES['proof_names']
                              if name.endswith('-symbolic')} |
                             {p.removeprefix('places/') for p in PLACES['lookup_aliases']})
            self.assertEqual({d for d in directories(tree) if d.startswith('places/')},
                             {'places/'+s for s in expected})
            for size in (24,32):
                self.assertFalse((tree/f'places/{size}').is_symlink())
                self.assertTrue((tree/f'places/{size}/.gitkeep').is_file())
            for alias, target in PLACES['directory_aliases'].items():
                self.assertEqual(str((tree/'places'/alias).readlink()),target)

    def test_small_places_are_semantic_and_symbolic_aliases(self):
        names = [name for name in PLACES['proof_names'] if not name.endswith('-symbolic')]
        self.assertFalse((SOURCE/'places/24/symbolic').exists())
        for tree in [SOURCE, *(BUILD/name for name in VARIANTS)]:
            regular_names = {p.stem for p in (tree/'places/24').glob('*.svg')
                             if not p.stem.endswith('-symbolic')}
            symbolic_names = {p.stem.removesuffix('-symbolic') for p in
                              (tree/'places/24').glob('*-symbolic.svg')}
            self.assertEqual(regular_names, symbolic_names)
            self.assertTrue(all((tree/f'places/24/{name}-symbolic.svg').is_symlink()
                                for name in regular_names))
            for name in names:
                regular = tree/f'places/24/{name}.svg'
                symbolic = tree/f'places/24/{name}-symbolic.svg'
                self.assertTrue(regular.is_file() and not regular.is_symlink())
                self.assertEqual(validate_svg(regular), [])
                self.assertTrue(symbolic.is_symlink())
                self.assertEqual(symbolic.readlink(), Path(f'{name}.svg'))
                self.assertEqual(symbolic.read_bytes(), regular.read_bytes())

    def test_large_folder_family_keeps_shared_body(self):
        from xml.etree import ElementTree as ET
        from templates import manifest
        entries = {e['source'] for e in manifest(ROOT)}
        names = [name for name in PLACES['proof_names'] if not name.endswith('-symbolic')]
        for name in names:
            self.assertIn(f'icons/places/32/{name}.svg', entries)
            self.assertNotIn(f'icons/places/24/{name}.svg', entries)
        home = (SOURCE/'places/32/folder-home.svg').read_text()
        body = ''.join(line for line in home.splitlines(keepends=True)
                       if not any(f'id="{part}"' in line for part in
                                  {'house', 'path14', *(f'house-glow-{i}' for i in range(1, 9))}))
        self.assertEqual((SOURCE/'places/32/folder.svg').read_text(), body)
        for name, glyph in [('folder-download','download'), ('folder-documents','documents'),
                            *[(f'folder-{n}',n) for n in ('desktop','pictures','music','videos',
                                'projects','templates','public','build','bookmark','network','recent','trash','trash-full')]]:
            artwork = (SOURCE/f'places/32/{name}.svg').read_text()
            stripped = ''.join(line for line in artwork.splitlines(keepends=True)
                               if f'id="{glyph}' not in line)
            self.assertEqual(stripped, (SOURCE/'places/32/folder.svg').read_text())
            layers = [e for e in ET.fromstring(artwork).iter()
                      if e.get('id','').startswith(glyph)]
            self.assertEqual(len(layers), 9)
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


class ActionsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        build()

    def test_masters_navigation_and_exact_metadata(self):
        import configparser
        for tree in [SOURCE, *(BUILD/name for name in VARIANTS)]:
            self.assertEqual(validate_actions(tree), [])
            self.assertEqual({p.name for p in (tree/'actions').iterdir()}, {'16','20','22','24','32'})
            for rel, target in ACTIONS['lookup_aliases'].items():
                self.assertEqual(str((tree/rel).readlink()), target)
                self.assertEqual((tree/rel).resolve(), (tree/Path(rel).parent/target).resolve())
        for name in VARIANTS:
            config = configparser.ConfigParser()
            config.read(BUILD/name/'index.theme')
            for size in (16,20,22,24,32):
                for suffix in ('', '/.'):
                    section = config[f'actions/{size}{suffix}']
                    self.assertEqual(section['Size'], str(size))
                    self.assertEqual(section['MinSize'], str(size))
                    self.assertEqual(section['MaxSize'], str(size))
                    self.assertEqual(section.get('Scale', '1'), '2' if suffix else '1')
            self.assertEqual({d for d in config['Icon Theme']['Directories'].split(',') if d.startswith('actions/')},
                             {f'actions/{s}' for s in (16,20,22,24,32)})

    def test_invalid_directory_links(self):
        with tempfile.TemporaryDirectory() as tmp:
            tree = Path(tmp)
            (tree/'actions/24').mkdir(parents=True)
            (tree/'actions/32').mkdir()
            path = tree/'actions/20'
            path.symlink_to('24')
            self.assertEqual(alias_errors(tree), [])
            for target in ('32', '../actions/24', '/tmp', '20', 'missing'):
                path.unlink(); path.symlink_to(target)
                self.assertTrue(alias_errors(tree), target)
            path.unlink()
            (tree/'actions/48').symlink_to('32')
            self.assertTrue(alias_errors(tree))

    def test_invalid_navigation_master_and_semantics(self):
        for mutation in ('target','canvas','rectangle','origin','large-canvas','paint','role','stylesheet','master','directory'):
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as tmp:
                tree = Path(tmp)/'icons'
                shutil.copytree(SOURCE/'actions', tree/'actions', symlinks=True)
                path = tree/'actions/24/chevron-up.svg'
                if mutation == 'large-canvas':
                    path = tree/'actions/32/chevron-up.svg'
                text = path.read_text()
                if mutation == 'target':
                    alias=tree/'actions/24/go-up.svg'
                    alias.unlink(); alias.symlink_to('chevron-down.svg')
                elif mutation == 'master':
                    path.unlink(); path.symlink_to('chevron-down.svg')
                elif mutation == 'directory':
                    shutil.rmtree(tree/'actions/32'); (tree/'actions/32').symlink_to('24')
                else:
                    replacements = {'canvas':('viewBox="0 0 24 24"','viewBox="0 0 32 32"'),
                                    'rectangle':('viewBox="0 0 24 24"','viewBox="0 0 20 24"'),
                                    'origin':('viewBox="0 0 24 24"','viewBox="1 0 24 24"'),
                                    'large-canvas':('viewBox="0 0 32 32"','viewBox="0 0 24 24"'),
                                    'paint':('stroke:currentColor','stroke:#abcdef'),
                                    'role':('class="ColorScheme-Text"','class="ColorScheme-Highlight"'),
                                    'stylesheet':('current-color-scheme','missing-style')}
                    path.write_text(text.replace(*replacements[mutation]))
                self.assertTrue(validate_actions(tree))


if __name__ == '__main__':
    unittest.main()
