import hashlib
import io
from pathlib import Path
import subprocess
import tarfile
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]


class FormulaPreparationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.archive = Path(self.temp.name) / "release.tar.gz"

    def make_archive(self, content, member="clipref-0.2.0/bin/clipref"):
        with tarfile.open(self.archive, "w:gz") as archive:
            entry = tarfile.TarInfo(member)
            entry.size = len(content)
            archive.addfile(entry, io.BytesIO(content))

    def prepare(self, tag="v0.2.0"):
        return subprocess.run(["/bin/bash", str(ROOT / "packaging/homebrew/prepare-formula.sh"),
                               tag, str(self.archive)], capture_output=True, timeout=5)

    def test_formula_pins_archive_bytes_and_release(self):
        self.make_archive((ROOT / "bin/clipref").read_bytes())
        result = self.prepare()
        self.assertEqual(result.returncode, 0, result.stderr)
        text = result.stdout.decode()
        self.assertIn(f'sha256 "{hashlib.sha256(self.archive.read_bytes()).hexdigest()}"', text)
        self.assertIn('/archive/refs/tags/v0.2.0.tar.gz"', text)
        self.assertIn('"clipref #{version}\\n"', text)
        check = subprocess.run(["/usr/bin/ruby", "-c"], input=result.stdout,
                               capture_output=True, timeout=5)
        self.assertEqual(check.returncode, 0, check.stderr)

    def test_rejects_missing_member_and_mismatched_version(self):
        for content, member in [(b"#!/bin/bash\nversion=0.1.0\n", "clipref-0.2.0/bin/clipref"),
                                (b"#!/bin/bash\nversion=0.2.0\n", "other/bin/clipref")]:
            with self.subTest(member=member, content=content):
                self.make_archive(content, member)
                result = self.prepare()
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(result.stdout, b"")

    def test_rejects_invalid_script_and_tag(self):
        for content in [b"<html>not found</html>\n", b"#!/bin/bash\nif\n"]:
            self.make_archive(content)
            result = self.prepare()
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(result.stdout, b"")
        self.assertNotEqual(self.prepare("main").returncode, 0)
