"""System packaging preserves the validated payload and never installs locally."""
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
from build import build, bundle_files
from stage import stage
from theme import BUILD, VARIANTS
from validate_icons import validate_theme


class SystemStaging(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        build()

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.destdir = self.root / 'package'

    def test_cli_packages_both_themes_and_bundle_without_host_effects(self):
        commands = self.root / 'bin'
        commands.mkdir()
        for name in ('gtk-update-icon-cache', 'kbuildsycoca6', 'sudo'):
            script = commands / name
            script.write_text('#!/bin/sh\ntouch "$XDG_DATA_HOME"\nexit 99\n')
            script.chmod(0o755)
        data = self.root / 'user-data'
        result = subprocess.run(
            [sys.executable, str(ROOT / 'scripts/stage.py'), '--destdir', str(self.destdir)],
            env={**os.environ, 'XDG_DATA_HOME': str(data), 'PATH': f'{commands}:{os.environ["PATH"]}'},
            capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(data.exists())
        share = self.destdir / 'usr/share'
        for name in VARIANTS:
            self.assertEqual(validate_theme(share / 'icons' / name, name), [])
            alias = share / 'icons' / name / 'places/20'
            self.assertTrue(alias.is_symlink())
            self.assertEqual(os.readlink(alias), '24')
        bundle = share / 'holonight-icons'
        self.assertEqual({str(p.relative_to(bundle)) for p in bundle.rglob('*') if p.is_file()}, bundle_files())
        self.assertFalse(list(self.destdir.rglob('.holonight-*')))

    def test_occupied_destination_is_unchanged(self):
        occupied = self.destdir / 'usr/share/holonight-icons'
        occupied.mkdir(parents=True)
        (occupied / 'marker').write_text('keep')
        with self.assertRaisesRegex(ValueError, 'already exists'):
            stage(self.destdir)
        self.assertEqual((occupied / 'marker').read_text(), 'keep')
        self.assertFalse((self.destdir / 'usr/share/icons').exists())

    def test_symlinked_parent_is_rejected(self):
        outside = self.root / 'outside'
        outside.mkdir()
        self.destdir.mkdir()
        (self.destdir / 'usr').symlink_to(outside, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, 'Symlinked'):
            stage(self.destdir)
        self.assertEqual(list(outside.iterdir()), [])

    def test_invalid_artifacts_leave_no_partial_payload(self):
        for relative in ('HoloNight/index.theme', 'holonight-icons/scripts/recolor.py'):
            with self.subTest(relative=relative), tempfile.TemporaryDirectory() as tmp:
                artifacts = Path(tmp)
                for name in (*VARIANTS, 'holonight-icons'):
                    shutil.copytree(BUILD / name, artifacts / name, symlinks=True)
                (artifacts / relative).write_text('invalid')
                with patch('stage.BUILD', artifacts), self.assertRaises(ValueError):
                    stage(self.destdir)
                self.assertEqual(list(self.destdir.iterdir()), [])

    def test_relative_destdir_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'absolute'):
            stage(Path('relative'))

    def test_copy_failure_rolls_back_packaged_payloads(self):
        original = Path.rename
        def fail_bundle(path, target):
            if path.name == 'holonight-icons':
                raise OSError('simulated rename failure')
            return original(path, target)
        with patch.object(Path, 'rename', fail_bundle), self.assertRaises(OSError):
            stage(self.destdir)
        self.assertFalse((self.destdir / 'usr/share/icons/HoloNight').exists())
        self.assertFalse((self.destdir / 'usr/share/icons/HoloNight-Dark').exists())
        self.assertFalse(list(self.destdir.glob('.holonight-*')))
