import os
from pathlib import Path
import pty
import subprocess
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "bin" / "clipref"


class CliprefTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.stubs = self.root / "stubs"
        self.stubs.mkdir()
        self.save_dir = self.root / "save directory"
        self.save_dir.mkdir()
        self.clipboard = self.root / "clipboard"
        self.clipboard.write_bytes(b"original clipboard\n")
        self.env = os.environ.copy()
        self.env.update(
            HOME=str(self.root / "home"),
            XDG_CONFIG_HOME=str(self.root / "config"),
            PATH=f"{self.stubs}:/usr/bin:/bin",
            TMPDIR=str(self.save_dir),
            CLIPREF_TEST_CLIPBOARD=str(self.clipboard),
            CLIPREF_TEST_SYSTEM="Darwin",
        )
        self.stub("uname", 'printf "%s\\n" "$CLIPREF_TEST_SYSTEM"')
        self.stub("pbpaste", 'cat "$CLIPREF_TEST_CLIPBOARD"')
        self.stub("pbcopy", 'cat > "$CLIPREF_TEST_CLIPBOARD"')

    def stub(self, name, body):
        path = self.stubs / name
        path.write_text("#!/bin/bash\n" + body + "\n")
        path.chmod(0o755)

    def run_cli(self, *args, data=b"test input\n", clipboard=False):
        command = ["/bin/bash", str(SCRIPT), *args]
        if clipboard:
            master, slave = pty.openpty()
            try:
                return subprocess.run(command, stdin=slave, capture_output=True,
                                      env=self.env, timeout=5)
            finally:
                os.close(slave)
                os.close(master)
        return subprocess.run(command, input=data, capture_output=True,
                              env=self.env, timeout=5)

    def saved_path(self, result):
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, b"")
        path = Path(os.fsdecode(result.stdout.rstrip(b"\n")))
        self.assertTrue(path.is_absolute())
        self.assertTrue(path.is_file())
        return path

    def test_pipe_preserves_bytes_and_copies_path(self):
        content = "  日本語\r\nline\n\n".encode()
        path = self.saved_path(self.run_cli(data=content))
        self.assertEqual(path.read_bytes(), content)
        self.assertEqual(self.clipboard.read_bytes(), os.fsencode(path))
        self.assertEqual(path.stat().st_mode & 0o777, 0o600)
        self.assertEqual(path.parent.stat().st_mode & 0o777, 0o700)

    def test_preserves_missing_final_newline(self):
        path = self.saved_path(self.run_cli(data=b"no final newline"))
        self.assertEqual(path.read_bytes(), b"no final newline")

    def test_terminal_input_reads_clipboard(self):
        content = b"copied log\n\n"
        self.clipboard.write_bytes(content)
        path = self.saved_path(self.run_cli(clipboard=True))
        self.assertEqual(path.read_bytes(), content)
        self.assertEqual(self.clipboard.read_bytes(), os.fsencode(path))

    def test_empty_input_preserves_clipboard_and_leaves_no_files(self):
        result = self.run_cli(data=b"")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stdout, b"")
        self.assertIn(b"input is empty", result.stderr)
        self.assertEqual(self.clipboard.read_bytes(), b"original clipboard\n")
        self.assertEqual(list(self.save_dir.iterdir()), [])

    def test_no_copy_does_not_call_clipboard_commands(self):
        self.stub("pbcopy", "exit 91")
        self.stub("pbpaste", "exit 92")
        self.saved_path(self.run_cli("--no-copy"))
        self.assertEqual(self.clipboard.read_bytes(), b"original clipboard\n")

    def test_directory_and_extension(self):
        target = self.root / "other directory"
        target.mkdir()
        path = self.saved_path(self.run_cli("--dir", str(target), "--ext", "log"))
        self.assertEqual(path.name, "input.log")
        self.assertEqual(path.parent.parent, target.resolve())

    def test_physical_path_for_symlink_directory(self):
        link = self.root / "link"
        link.symlink_to(self.save_dir, target_is_directory=True)
        path = self.saved_path(self.run_cli("--dir", str(link)))
        self.assertEqual(path.parent.parent, self.save_dir.resolve())

    def test_runs_do_not_overwrite(self):
        first = self.saved_path(self.run_cli(data=b"first"))
        second = self.saved_path(self.run_cli(data=b"second"))
        self.assertNotEqual(first, second)
        self.assertEqual(first.read_bytes(), b"first")
        self.assertEqual(second.read_bytes(), b"second")

    def test_copy_failure_keeps_file_and_reports_path(self):
        self.stub("pbcopy", "exit 1")
        result = self.run_cli(data=b"keep this")
        self.assertNotEqual(result.returncode, 0)
        path = Path(os.fsdecode(result.stdout.rstrip(b"\n")))
        self.assertEqual(path.read_bytes(), b"keep this")
        self.assertIn(b"file saved", result.stderr)
        self.assertEqual(self.clipboard.read_bytes(), b"original clipboard\n")

    def test_clipboard_read_failure_removes_incomplete_file(self):
        self.stub("pbpaste", "printf partial; exit 1")
        result = self.run_cli(clipboard=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stdout, b"")
        self.assertEqual(list(self.save_dir.iterdir()), [])

    def test_file_creation_failure_preserves_clipboard(self):
        self.stub("mktemp", "exit 1")
        result = self.run_cli()
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stdout, b"")
        self.assertIn(b"could not create", result.stderr)
        self.assertEqual(self.clipboard.read_bytes(), b"original clipboard\n")
        self.assertEqual(list(self.save_dir.iterdir()), [])

    def test_input_read_failure_removes_incomplete_file(self):
        self.stub("cat", "printf partial; exit 1")
        result = self.run_cli()
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stdout, b"")
        self.assertIn(b"could not save input", result.stderr)
        self.assertEqual(self.clipboard.read_bytes(), b"original clipboard\n")
        self.assertEqual(list(self.save_dir.iterdir()), [])

    def test_invalid_arguments_do_not_create_files(self):
        for args in [("--ext", "../log"), ("--ext", ""), ("--ext", ".log"),
                     ("--dir",), ("--ext",), ("--unknown",),
                     ("--dir", str(self.root / "missing"))]:
            with self.subTest(args=args):
                result = self.run_cli(*args)
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(result.stdout, b"")
                self.assertEqual(list(self.save_dir.iterdir()), [])
                self.assertEqual(self.clipboard.read_bytes(), b"original clipboard\n")

    def test_non_macos_is_rejected(self):
        self.env["CLIPREF_TEST_SYSTEM"] = "Linux"
        result = self.run_cli()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(b"macOS is required", result.stderr)
        self.assertEqual(list(self.save_dir.iterdir()), [])

    def write_config(self, content):
        path = self.root / "config" / "clipref" / "config"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)

    def test_config_defaults_and_cli_precedence(self):
        target = self.root / "configured directory"
        target.mkdir()
        self.write_config(f"# defaults\ndir = {target}\next = log")
        path = self.saved_path(self.run_cli())
        self.assertEqual(path.parent.parent, target.resolve())
        self.assertEqual(path.name, "input.log")
        path = self.saved_path(self.run_cli("--dir", str(self.save_dir), "--ext", "txt"))
        self.assertEqual(path.parent.parent, self.save_dir.resolve())
        self.assertEqual(path.name, "input.txt")

    def test_home_relative_config_and_fallback_location(self):
        home = Path(self.env["HOME"])
        (home / "logs").mkdir(parents=True)
        self.write_config("dir=~/logs\next=log\n")
        path = self.saved_path(self.run_cli())
        self.assertEqual(path.parent.parent, (home / "logs").resolve())
        self.env.pop("XDG_CONFIG_HOME")
        config = home / ".config" / "clipref" / "config"
        config.parent.mkdir(parents=True)
        config.write_text("ext=md\n")
        self.assertEqual(self.saved_path(self.run_cli()).name, "input.md")

    def test_invalid_config_is_data_and_preserves_clipboard(self):
        marker = self.root / "executed"
        for content in ["unknown=x", "ext=", "ext=../log", "dir=relative", "ext=txt\next=log",
                        "missing equals", f"ext=$(touch {marker})", f"ext=`touch {marker}`"]:
            self.write_config(content)
            result = self.run_cli()
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(result.stdout, b"")
            self.assertEqual(list(self.save_dir.iterdir()), [])
            self.assertFalse(marker.exists())
            self.assertEqual(self.clipboard.read_bytes(), b"original clipboard\n")
        self.assertEqual(self.run_cli("--help").returncode, 0)

    def test_help_does_not_read_clipboard_or_create_files(self):
        self.stub("pbpaste", "exit 1")
        result = self.run_cli("--help")
        self.assertEqual(result.returncode, 0)
        self.assertIn(b"Usage: clipref", result.stdout)
        self.assertEqual(list(self.save_dir.iterdir()), [])

    def test_version_does_not_read_clipboard_or_create_files(self):
        self.stub("pbpaste", "exit 1")
        result = self.run_cli("--version")
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, b"clipref 0.1.0\n")
        self.assertEqual(list(self.save_dir.iterdir()), [])
        self.assertEqual(self.clipboard.read_bytes(), b"original clipboard\n")


if __name__ == "__main__":
    unittest.main()
