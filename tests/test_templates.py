"""Token identity, frozen paints, and isolated on-demand installation regressions."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
from templates import manifest, generate, default_output, resolve, validate_frozen
from theme import PALETTES, BUILD, PLACES
from build import build
from install import install
from recolor import recolor_theme


class TemplateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        build()
        cls.entry = manifest(ROOT)[0]
        cls.day = PALETTES['presets']['holonight-day']
        cls.storm = PALETTES['presets']['holonight-storm']

    def test_exact_defaults(self):
        expected = {
            'light': dict(background='#e7eef5', surface='#f1f5fa', textPrimary='#1b2533',
                          accentCyan='#00a8d8', accentBlue='#3e7bdb', accentViolet='#7566d4'),
            'dark': dict(background='#0c1118', surface='#131a24', textPrimary='#e7edf5',
                         accentCyan='#56d7ff', accentBlue='#5ea2ff', accentViolet='#9a8cff'),
        }
        semantic = {
            'light': ['#1b2533','#e7eef5','#3e7bdb','#ffffff','#3e9449','#c38a1c','#d84a68'],
            'dark': ['#e7edf5','#0c1118','#5ea2ff','#081018','#79d97f','#f2c46b','#ff718c'],
        }
        from templates import RULE
        self.assertEqual(len(manifest(ROOT)), 40)
        for variant, tokens in expected.items():
            self.assertEqual(PALETTES['presets']['holonight-'+variant], tokens)
            self.assertEqual(list(PALETTES[variant].values()), semantic[variant])
            for entry in manifest(ROOT):
                result = generate(ROOT, entry, tokens, variant)
                validate_frozen(result)
                paints = {v for e in ET.fromstring(result).iter() for k,v in e.attrib.items()
                          if k in ('fill','stroke','stop-color') and v.startswith('#')}
                self.assertEqual(paints, {tokens[t] for t in entry['classes'].values()})
                name = 'HoloNight' if variant == 'light' else 'HoloNight-Dark'
                self.assertEqual((BUILD/name/entry['output']).read_text(), result)
                self.assertEqual(result, default_output(ROOT, entry, variant))
                css = ET.fromstring((ROOT/entry['source']).read_text()).find('{*}style').text
                canonical = {'ColorScheme-'+r:v for r,v in PALETTES['dark'].items()}
                canonical.update({c:expected['dark'][t] for c,t in entry['classes'].items()})
                self.assertEqual(dict(RULE.findall(css)), canonical)

    def test_invalid_tokens(self):
        for values in [{}, {**self.day, 'typo':'#123456'}, {**self.day, 'surface':'red'}, {**self.day, 'surface':'#12345678'}]:
            with self.assertRaises(ValueError):
                generate(ROOT, self.entry, values, 'light')

    def test_invalid_template_paints_and_css(self):
        text = (ROOT/self.entry['source']).read_text()
        for old,new in [('stop-color="currentColor"','stop-color="#123456"'),
                        ('class="HoloNight-surface"','class="HoloNight-missing"'),
                        ('fill="currentColor"','fill="black"'),
                        ('class="HoloNight-surface"','style="color:red"'),
                        ('url(#rim)','url(#missing)')]:
            with self.assertRaises(ValueError):
                resolve(text.replace(old,new), self.entry, self.day, PALETTES['light'])
        with self.assertRaises(ValueError):
            validate_frozen(text)

    def test_equal_colors_diverge_and_repeat(self):
        same = {**self.day, 'accentBlue':self.day['accentCyan']}
        first = generate(ROOT, self.entry, same, 'light')
        later = generate(ROOT, self.entry, self.day, 'light')
        self.assertNotEqual(first, later)
        self.assertEqual(later, generate(ROOT, self.entry, self.day, 'light'))
        self.assertIn('stop-color="#2f6fe4"', later)
        self.assertIn('stop-color="#008fc7"', later)

    def test_semantic_gradient_stops_and_frozen_implicit_paints(self):
        from validate_icons import validate_svg
        text = (ROOT/'tests/fixtures/inherited.svg').read_text()
        gradient = '<defs><linearGradient id="test"><stop class="ColorScheme-Text" stop-color="currentColor"/></linearGradient></defs>'
        text = text.replace('</svg>', gradient+'</svg>')
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)/'gradient.svg'
            path.write_text(text)
            self.assertEqual(validate_svg(path), [])
            path.write_text(text.replace('stop-color="currentColor"', 'stop-color="#123456"'))
            self.assertTrue(validate_svg(path))
        frozen = generate(ROOT, self.entry, self.day, 'light')
        root = ET.fromstring(frozen)
        next(e for e in root.iter() if e.get('id') == 'house').attrib.pop('fill')
        with self.assertRaises(ValueError):
            validate_frozen(ET.tostring(root, encoding='unicode'))

    def test_installed_command_and_recovery(self):
        with tempfile.TemporaryDirectory() as tmp:
            data = Path(tmp)
            install(data/'icons', refresh=False)
            target = data/'icons/HoloNight'/self.entry['output']
            unrelated = data/'icons/HoloNight/status/24/insync-alert.svg'
            before = unrelated.read_bytes()
            original = target.read_bytes()
            with self.assertRaises(ValueError):
                recolor_theme(data, data/'holonight-icons', 'HoloNight', {}, False)
            self.assertEqual(target.read_bytes(), original)
            self.assertFalse(list((data/'icons').glob('.holonight-recolor-backup-*')))
            bundle = data/'holonight-icons'
            source = (bundle/self.entry['source']).read_bytes()
            cmd = [sys.executable, str(bundle/'scripts/recolor.py'), 'HoloNight', '--preset', 'holonight-storm', '--no-cache']
            subprocess.run(cmd, env={**os.environ, 'XDG_DATA_HOME':tmp}, check=True, stdout=subprocess.DEVNULL)
            expected = generate(bundle, self.entry, self.storm, 'light')
            self.assertEqual(target.read_text(), expected)
            backups = list((data/'icons').glob('.holonight-recolor-backup-*'))
            self.assertEqual((backups[0]/self.entry['output']).read_bytes(), original)
            recolor_theme(data, bundle, 'HoloNight', self.storm, False)
            self.assertEqual(target.read_text(), expected)
            recolor_theme(data, bundle, 'HoloNight', PALETTES['presets']['holonight-light'], False)
            self.assertEqual(target.read_bytes(), original)
            self.assertEqual(unrelated.read_bytes(), before)
            self.assertEqual((bundle/self.entry['source']).read_bytes(), source)
            with patch('recolor.shutil.which', return_value='/test/cache'), patch('recolor.subprocess.run', side_effect=subprocess.CalledProcessError(1,'cache')):
                with self.assertRaises(subprocess.CalledProcessError):
                    recolor_theme(data, bundle, 'HoloNight', self.storm)
            self.assertEqual(target.read_bytes(), original)
            target.unlink()
            target.symlink_to(unrelated)
            with self.assertRaises(ValueError):
                recolor_theme(data, bundle, 'HoloNight', self.storm, False)
            self.assertEqual(unrelated.read_bytes(), before)

    def test_both_masters_presets_aliases_and_partial_rollback(self):
        with tempfile.TemporaryDirectory() as tmp:
            data = Path(tmp)
            install(data/'icons', refresh=False)
            bundle = data/'holonight-icons'
            entries = manifest(bundle)
            for name, variant in [('HoloNight','light'), ('HoloNight-Dark','dark')]:
                theme = data/'icons'/name
                original = {e['output']:(theme/e['output']).read_bytes() for e in entries}
                symbolics = [theme/f'places/24/symbolic/{name}-symbolic.svg'
                             for name in PLACES['proof_names'] if not name.endswith('-symbolic')]
                glyphs = [p.read_bytes() for p in symbolics]
                historical = theme/'places/24/symbolic/folder-download.svg'
                self.assertTrue(historical.is_symlink())
                self.assertEqual(historical.read_bytes(), glyphs[2])
                open_alias = theme/'places/24/symbolic/folder-open.svg'
                self.assertTrue(open_alias.is_symlink())
                self.assertEqual(open_alias.read_bytes(),
                                 (theme/'places/24/symbolic/folder-open-symbolic.svg').read_bytes())
                for preset, values in PALETTES['presets'].items():
                    subprocess.run([sys.executable, str(bundle/'scripts/recolor.py'), name,
                                    '--preset',preset,'--no-cache'],
                                   env={**os.environ, 'XDG_DATA_HOME':tmp}, check=True,
                                   stdout=subprocess.DEVNULL)
                    for entry in entries:
                        target = theme/entry['output']
                        self.assertEqual(target.read_text(), generate(bundle,entry,values,variant))
                    for rel, dest in PLACES['lookup_aliases'].items():
                        alias = theme/rel
                        self.assertTrue(alias.is_symlink())
                        self.assertEqual(alias.read_bytes(), alias.with_name(dest).read_bytes())
                    self.assertEqual([p.read_bytes() for p in symbolics], glyphs)
                recolor_theme(data,bundle,name,PALETTES['presets']['holonight-'+variant],False)
                real_replace = Path.replace
                calls = []
                def fail_new_master(path, target):
                    if '.holonight-recolor-stage-' in str(path):
                        calls.append(str(target))
                        if str(target).endswith('/24/folder-open.svg'):
                            raise OSError('simulated Open master replacement failure')
                    return real_replace(path,target)
                with patch.object(Path, 'replace', fail_new_master):
                    with self.assertRaisesRegex(OSError,'Open master'):
                        recolor_theme(data,bundle,name,self.storm,False)
                failed_index = next(i for i, entry in enumerate(entries)
                                    if entry['output'] == 'places/24/folder-open.svg')
                self.assertEqual(len(calls), failed_index * 2 + 1)
                for entry in entries:
                    self.assertEqual((theme/entry['output']).read_bytes(),original[entry['output']])
                backups = list((data/'icons').glob('.holonight-recolor-backup-*'))
                self.assertTrue(backups)
                for backup in backups:
                    for entry in entries:
                        self.assertTrue((backup/entry['output']).is_file())
                self.assertEqual([p.read_bytes() for p in symbolics], glyphs)
