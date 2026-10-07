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
            XDG_STATE_HOME=str(self.root / "state"),

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

    def test_explicit_clipboard_overrides_pipe_and_empty_stdin(self):
        for data in [b"ignored pipe", b""]:
            self.clipboard.write_bytes(b"clipboard content\n")
            path = self.saved_path(self.run_cli("--clipboard", data=data))
            self.assertEqual(path.read_bytes(), b"clipboard content\n")

    def test_explicit_clipboard_failure_and_empty_input(self):
        self.clipboard.write_bytes(b"")
        result = self.run_cli("--clipboard")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(b"input is empty", result.stderr)
        self.stub("pbpaste", "printf partial; exit 1")
        result = self.run_cli("--clipboard")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(b"could not read clipboard", result.stderr)
        self.assertEqual(list(self.save_dir.iterdir()), [])

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

    def test_meaningful_names_preserve_contents_and_permissions(self):
        for name in ["startup-error.log", "日本語 log.txt", "-leading.txt"]:
            path = self.saved_path(self.run_cli("--name", name, data=b"named log"))
            self.assertEqual(path.name, name)
            self.assertEqual(path.read_bytes(), b"named log")
            self.assertEqual(path.stat().st_mode & 0o777, 0o600)

    def test_invalid_names_do_not_create_files(self):
        for name in ["", ".", "..", "../log", "a/b", "a\\b", "a\nb", "a\rb", "a\tb"]:
            result = self.run_cli("--name", name)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(list(self.save_dir.iterdir()), [])
        result = self.run_cli("--name", "a.log", "--ext", "txt")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(b"cannot be combined", result.stderr)
        self.assertEqual(list(self.save_dir.iterdir()), [])

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

    def test_history_listing_and_last_preserve_path(self):
        first = self.saved_path(self.run_cli(data=b"first"))
        second = self.saved_path(self.run_cli(data=b"second"))
        self.stub("pbpaste", "exit 99")
        result = self.run_cli("list", "--limit", "1")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(len(result.stdout.splitlines()), 1)
        self.assertTrue(result.stdout.startswith(b"exists\t"))
        result = self.run_cli("last")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, os.fsencode(second) + b"\n")
        self.assertEqual(self.clipboard.read_bytes(), os.fsencode(second))
        records = list((self.root / "state" / "clipref" / "history").glob("entry.*"))
        self.assertEqual(len(records), 2)
        for record in records:
            self.assertEqual(record.stat().st_mode & 0o777, 0o600)
        self.assertEqual(first.read_bytes(), b"first")

    def test_history_missing_last_and_no_copy(self):
        path = self.saved_path(self.run_cli())
        self.clipboard.write_bytes(b"unchanged")
        result = self.run_cli("last", "--no-copy")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.clipboard.read_bytes(), b"unchanged")
        path.unlink()
        self.assertTrue(self.run_cli("list").stdout.startswith(b"missing\t"))
        result = self.run_cli("last")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.clipboard.read_bytes(), b"unchanged")

    def test_history_empty_and_invalid_arguments(self):
        self.assertEqual(self.run_cli("list").stdout, b"")
        self.assertNotEqual(self.run_cli("last").returncode, 0)
        for args in [("list", "--limit", "0"), ("list", "--limit", "1001"),
                     ("list", "--limit", "01"), ("list", "--limit"),
                     ("last", "--dir", "/tmp"), ("--limit", "2")]:
            self.assertNotEqual(self.run_cli(*args).returncode, 0)
        self.assertFalse((self.root / "state").exists())

    def test_history_failure_keeps_saved_file_and_copies_path(self):
        history = self.root / "state" / "clipref" / "history"
        history.mkdir(parents=True, mode=0o755)
        result = self.run_cli()
        self.assertEqual(result.returncode, 0, result.stderr)
        path = Path(os.fsdecode(result.stdout.rstrip(b"\n")))
        self.assertTrue(path.is_file())
        self.assertIn(b"history could not be recorded", result.stderr)
        self.assertEqual(self.clipboard.read_bytes(), os.fsencode(path))
        self.assertNotEqual(self.run_cli("list").returncode, 0)

    def test_history_concurrent_saves_have_complete_records(self):
        commands = [["/bin/bash", str(SCRIPT), "--no-copy"] for _ in range(6)]
        processes = [subprocess.Popen(c, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE, env=self.env) for c in commands]
        paths = []
        for process in processes:
            out, err = process.communicate(b"concurrent log", timeout=5)
            self.assertEqual(process.returncode, 0, err)
            self.assertEqual(err, b"")
            paths.append(out.rstrip(b"\n"))
        history = self.root / "state" / "clipref" / "history"
        self.assertEqual({p.read_bytes() for p in history.glob("entry.*")},
                         {p + b"\0" for p in paths})
        self.assertEqual(list(history.glob(".pending.*")), [])

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

    def test_clipboard_name_config_and_history_work_together(self):
        target = self.root / "configured directory"
        target.mkdir()
        self.write_config(f"dir={target}\next=log\n")
        self.clipboard.write_bytes("日本語のログ\n\n".encode())
        path = self.saved_path(self.run_cli("--clipboard", "--name", "startup error.txt",
                                           "--no-copy", data=b"ignored"))
        self.assertEqual(path.name, "startup error.txt")
        self.assertEqual(path.parent.parent, target.resolve())
        self.assertEqual(path.read_bytes(), "日本語のログ\n\n".encode())
        result = self.run_cli("last", "--no-copy")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, os.fsencode(path) + b"\n")
        self.assertEqual(self.clipboard.read_bytes(), "日本語のログ\n\n".encode())

    def test_history_rejects_symlink_directory_without_writing_records(self):
        target = self.root / "other-history"
        target.mkdir(mode=0o700)
        history = self.root / "state" / "clipref" / "history"
        history.parent.mkdir(parents=True)
        history.symlink_to(target, target_is_directory=True)
        result = self.run_cli("--no-copy")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(b"history could not be recorded", result.stderr)
        self.assertEqual(list(target.iterdir()), [])
        self.assertNotEqual(self.run_cli("list").returncode, 0)

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
