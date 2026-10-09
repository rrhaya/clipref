import os
from pathlib import Path
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]


class InstallTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.stubs = self.root / "stubs"
        self.stubs.mkdir()
        self.target = self.root / "install directory" / "bin"
        self.env = os.environ.copy()
        self.env.update(PATH=f"{self.stubs}:/usr/bin:/bin",
                        TMPDIR=str(self.root),
                        CLIPREF_TEST_SOURCE=str(ROOT / "bin" / "clipref"),
                        CLIPREF_TEST_RELEASE="v0.2.0")
        self.stub("uname", "printf 'Darwin\\n'")
        self.stub("curl", '''
[ "$1" = -fsSL ] || exit 1
[ "$2" = "https://raw.githubusercontent.com/rrhaya/clipref/$CLIPREF_TEST_RELEASE/bin/clipref" ] || exit 1
[ "$3" = -o ] || exit 1
cp "$CLIPREF_TEST_SOURCE" "$4"
''')

    def stub(self, name, body):
        path = self.stubs / name
        path.write_text("#!/bin/bash\n" + body + "\n")
        path.chmod(0o755)

    def run_install(self, *args):
        return subprocess.run(["/bin/bash", str(ROOT / "install.sh"),
                               "--bin-dir", str(self.target), *args],
                              capture_output=True, env=self.env, timeout=5)

    def assert_no_download_files(self):
        self.assertEqual(list(self.root.glob("clipref-install.*")), [])

    def test_installs_executable_and_cleans_download(self):
        result = self.run_install()
        self.assertEqual(result.returncode, 0, result.stderr)
        installed = self.target / "clipref"
        self.assertEqual(installed.read_bytes(), (ROOT / "bin" / "clipref").read_bytes())
        self.assertEqual(installed.stat().st_mode & 0o777, 0o755)
        help_result = subprocess.run([str(installed), "--help"], capture_output=True, timeout=5)
        self.assertEqual(help_result.returncode, 0)
        self.assertIn(b"Usage: clipref", help_result.stdout)
        version_result = subprocess.run([str(installed), "--version"], capture_output=True, timeout=5)
        self.assertEqual(version_result.returncode, 0)
        self.assertEqual(version_result.stdout, b"clipref 0.2.0\n")
        self.assertIn(b"Add this directory to PATH", result.stdout)
        self.assert_no_download_files()

    def test_selects_requested_release(self):
        self.env["CLIPREF_TEST_RELEASE"] = "v0.3.0"
        result = self.run_install("--version", "v0.3.0")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((self.target / "clipref").is_file())
        self.assert_no_download_files()

    def test_rejects_invalid_release_before_download(self):
        for tag in ["", "main", "0.2.0", "v0.1", "../main", "v0.2.0/other", "v0.2.0;echo"]:
            with self.subTest(tag=tag):
                result = self.run_install("--version", tag)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(b"release tag must", result.stderr)
                self.assertFalse(self.target.exists())
                self.assert_no_download_files()

    def test_failed_download_keeps_existing_installation(self):
        self.target.mkdir(parents=True)
        installed = self.target / "clipref"
        installed.write_bytes(b"existing installation")
        self.stub("curl", "exit 22")
        result = self.run_install()
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(installed.read_bytes(), b"existing installation")
        self.assertIn(b"download failed", result.stderr)
        self.assert_no_download_files()

    def test_failed_install_keeps_existing_installation(self):
        self.target.mkdir(parents=True)
        installed = self.target / "clipref"
        installed.write_bytes(b"existing installation")
        self.stub("install", 'printf partial > "$4"; exit 1')
        result = self.run_install()
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(installed.read_bytes(), b"existing installation")
        self.assertEqual(list(self.target.glob(".clipref-install.*")), [])
        self.assert_no_download_files()

    def test_custom_directory_path_advice_uses_actual_directory(self):
        result = self.run_install()
        self.assertEqual(result.returncode, 0, result.stderr)
        advice = result.stdout.decode().split("Add this directory to PATH:", 1)[1]
        self.assertNotIn('export PATH="$HOME/.local/bin:$PATH"', advice)
        command = next(line.strip() for line in advice.splitlines() if "export PATH=" in line)
        check = subprocess.run(["/bin/bash", "-c", command + '; printf "%s" "$PATH"'],
                               capture_output=True, env=self.env, timeout=5)
        self.assertEqual(check.returncode, 0, check.stderr)
        self.assertEqual(check.stdout.decode().split(":", 1)[0], str(self.target.resolve()))

    def test_updates_existing_regular_file(self):
        self.target.mkdir(parents=True)
        installed = self.target / "clipref"
        installed.write_bytes(b"old version")
        result = self.run_install()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(installed.read_bytes(), (ROOT / "bin" / "clipref").read_bytes())
        self.assertEqual(list(self.target.glob(".clipref-install.*")), [])
        self.assert_no_download_files()

    def test_rejects_symlink_destination_without_changing_target(self):
        self.target.mkdir(parents=True)
        other = self.root / "unrelated"
        other.write_bytes(b"unrelated executable")
        (self.target / "clipref").symlink_to(other)
        result = self.run_install()
        self.assertNotEqual(result.returncode, 0)
        self.assertTrue((self.target / "clipref").is_symlink())
        self.assertEqual(other.read_bytes(), b"unrelated executable")
        self.assert_no_download_files()

    def test_rejects_empty_html_and_invalid_script(self):
        for content in [b"", b"<html>not found</html>", b"#!/bin/bash\nif\n"]:
            with self.subTest(content=content):
                source = self.root / "invalid"
                source.write_bytes(content)
                self.env["CLIPREF_TEST_SOURCE"] = str(source)
                result = self.run_install()
                self.assertNotEqual(result.returncode, 0)
                self.assertFalse(self.target.exists())
                self.assert_no_download_files()

    def test_rejects_non_macos_before_download(self):
        self.stub("uname", "printf 'Linux\\n'")
        self.stub("curl", "exit 99")
        result = self.run_install()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(b"macOS is required", result.stderr)
        self.assertFalse(self.target.exists())
        self.assert_no_download_files()

    def test_help_has_no_side_effects(self):
        result = self.run_install("--help")
        self.assertEqual(result.returncode, 0)
        self.assertIn(b"Usage:", result.stdout)
        self.assertFalse(self.target.exists())
        self.assert_no_download_files()

    def test_rejects_invalid_options(self):
        for args in [("--bin-dir",), ("--bin-dir", ""), ("--version",), ("--unknown",)]:
            with self.subTest(args=args):
                result = self.run_install(*args)
                self.assertNotEqual(result.returncode, 0)
                self.assertFalse(self.target.exists())
                self.assert_no_download_files()
